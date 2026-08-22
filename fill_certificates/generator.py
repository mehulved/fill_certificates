"""
Certificate rendering logic using Pillow.
"""

import os
import logging
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageFont, ImageDraw
from .config import EventConfig, FieldConfig

logger = logging.getLogger(__name__)


class CertificateGenerator:
    """Renders text onto certificate templates using Pillow."""

    @staticmethod
    def calculate_field_position(
        image_size: Tuple[int, int],
        text: str,
        font: ImageFont.ImageFont,
        draw: ImageDraw.ImageDraw,
        field_config: FieldConfig,
    ) -> Tuple[int, int]:
        """Calculate (x, y) coordinates for text positioning."""
        image_width, image_height = image_size

        # Pillow 10+ text measurement
        if hasattr(draw, "textbbox"):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
        elif hasattr(font, "getbbox"):
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
        else:
            # Legacy fallback if available
            text_width = font.getsize(text)[0]

        if field_config.width is not None and field_config.width > 0:
            item_width = field_config.width
        else:
            item_canvas_center = int((image_width - text_width) / 2)
            item_width = field_config.width_offset_left + item_canvas_center - field_config.width_offset_right

        item_height = field_config.height
        return (item_width, item_height)

    @classmethod
    def generate_certificate(
        cls,
        data_row: Dict[str, Any],
        event_config: EventConfig,
        custom_filename: Optional[str] = None,
    ) -> str:
        """Render a single certificate for a given data row."""
        template_path = event_config.template_path
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Certificate template image not found: {template_path}")

        img = Image.open(template_path)
        # Convert image to RGB if needed to draw text cleanly
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        draw = ImageDraw.Draw(img)

        # Normalize key names from CSV
        normalized_row = {k.strip().lower(): str(v).strip() for k, v in data_row.items() if k}

        for key, field_cfg in event_config.fields.items():
            if key not in normalized_row:
                logger.warning(f"Field '{key}' configured in config.ini but missing in CSV row data.")
                continue

            text_val = normalized_row[key]
            if not text_val:
                continue

            # Resolve font
            font_path = field_cfg.font_path or event_config.font_path
            if not os.path.isabs(font_path) and not os.path.exists(font_path):
                # Search relative to event dir or execution directory
                event_rel_font = os.path.join(event_config.event_dir, font_path)
                if os.path.exists(event_rel_font):
                    font_path = event_rel_font
                elif os.path.exists(os.path.abspath(font_path)):
                    font_path = os.path.abspath(font_path)

            try:
                font = ImageFont.truetype(font_path, field_cfg.font_size)
            except Exception as e:
                logger.warning(f"Unable to load font {font_path}: {e}. Falling back to default PIL font.")
                font = ImageFont.load_default()

            pos = cls.calculate_field_position(img.size, text_val, font, draw, field_cfg)
            color = field_cfg.color or event_config.text_color
            draw.text(pos, text_val, fill=color, font=font)

        # Determine output filename
        if custom_filename:
            filename = custom_filename
        else:
            name_val = normalized_row.get(event_config.name_field.lower(), "certificate")
            safe_name = name_val.lower().replace(" ", "_")
            ext = os.path.splitext(template_path)[1] or ".jpg"
            filename = f"{safe_name}{ext}"

        os.makedirs(event_config.output_dir, exist_ok=True)
        output_path = os.path.join(event_config.output_dir, filename)

        img.save(output_path)
        img.close()
        logger.info(f"Generated certificate saved to: {output_path}")
        return output_path
