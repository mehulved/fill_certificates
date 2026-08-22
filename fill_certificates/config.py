"""
Configuration parsing and dataclasses for fill_certificates.
"""

import os
import glob
import configparser
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)


def parse_color(color_str: str) -> Tuple[int, int, int]:
    """Parse color string in format 'R,G,B' or hex '#RRGGBB' into (R, G, B) tuple."""
    if not color_str:
        return (0, 0, 0)
    color_str = color_str.strip()
    if color_str.startswith("#"):
        color_str = color_str.lstrip("#")
        if len(color_str) == 6:
            return (int(color_str[0:2], 16), int(color_str[2:4], 16), int(color_str[4:6], 16))
    if "," in color_str:
        parts = [int(p.strip()) for p in color_str.split(",") if p.strip()]
        if len(parts) == 3:
            return (parts[0], parts[1], parts[2])
    return (0, 0, 0)


@dataclass
class FieldConfig:
    name: str
    height: int = 0
    width: Optional[int] = None
    width_offset_left: int = 0
    width_offset_right: int = 0
    font_size: int = 40
    font_path: Optional[str] = None
    color: Optional[Tuple[int, int, int]] = None


@dataclass
class EventConfig:
    event_name: str
    event_dir: str
    config_file: str
    template_path: str
    data_file: str
    output_dir: str
    font_path: str = "news-serif.ttf"
    text_color: Tuple[int, int, int] = (0, 0, 0)
    name_field: str = "name"
    fields: Dict[str, FieldConfig] = field(default_factory=dict)


class ConfigManager:
    """Manages reading and building event configuration objects."""

    @staticmethod
    def discover_events(events_root: str = "events") -> List[str]:
        """Find all event directories under events_root."""
        if not os.path.exists(events_root) or not os.path.isdir(events_root):
            return []
        events = []
        for entry in os.listdir(events_root):
            full_path = os.path.join(events_root, entry)
            if os.path.isdir(full_path):
                # An event dir contains config.ini or a data directory or template
                events.append(entry)
        events.sort()
        return events

    @staticmethod
    def load_event_config(
        event_dir: str = ".",
        config_file: Optional[str] = None,
        template_override: Optional[str] = None,
        data_override: Optional[str] = None,
        output_override: Optional[str] = None,
    ) -> EventConfig:
        """Build EventConfig by loading config.ini from event_dir and resolving defaults."""
        event_dir = os.path.abspath(event_dir)
        event_name = os.path.basename(event_dir.rstrip(os.sep)) or "default"

        # Determine config file path
        if not config_file:
            config_file = os.path.join(event_dir, "config.ini")
            if not os.path.exists(config_file) and event_dir != os.path.abspath("."):
                # fallback to root config.ini if event directory has no config.ini
                root_cfg = os.path.abspath("config.ini")
                if os.path.exists(root_cfg):
                    config_file = root_cfg

        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file)
            logger.debug(f"Loaded config from {config_file}")
        else:
            logger.warning(f"Config file not found at {config_file}, using defaults.")

        # Event-level settings from [event] or [general] section
        event_section = {}
        if config.has_section("event"):
            event_section = dict(config.items("event"))
        elif config.has_section("general"):
            event_section = dict(config.items("general"))

        # Helper to make relative path absolute against event_dir or subfolders (templates/, data/)
        def resolve_rel_path(path_str: Optional[str], subfolder: str = "") -> Optional[str]:
            if not path_str:
                return None
            if os.path.isabs(path_str):
                return path_str
            # Check direct relative to event_dir
            event_rel = os.path.join(event_dir, path_str)
            if os.path.exists(event_rel):
                return event_rel
            # Check inside subfolder (e.g. templates/ or data/)
            if subfolder:
                sub_rel = os.path.join(event_dir, subfolder, os.path.basename(path_str))
                if os.path.exists(sub_rel):
                    return sub_rel
            return path_str

        # Resolve template path
        template_path = template_override or resolve_rel_path(event_section.get("template"), "templates")
        if not template_path or not os.path.exists(template_path):
            templates_dir = os.path.join(event_dir, "templates")
            template_candidates = []
            if os.path.exists(templates_dir):
                template_candidates.extend(glob.glob(os.path.join(templates_dir, "*.jpg")))
                template_candidates.extend(glob.glob(os.path.join(templates_dir, "*.png")))
                template_candidates.extend(glob.glob(os.path.join(templates_dir, "*.jpeg")))

            template_candidates.extend([
                os.path.join(event_dir, "templates", "template.jpg"),
                os.path.join(event_dir, "templates", "certificate-template.jpg"),
                os.path.join(event_dir, "template.jpg"),
                os.path.join(event_dir, "certificate-template.jpg"),
                os.path.abspath("certificate-template.jpg"),
            ])
            for candidate in template_candidates:
                if os.path.exists(candidate):
                    template_path = candidate
                    break
            if not template_path:
                template_path = os.path.join(event_dir, "templates", "template.jpg")

        # Resolve data file path
        data_file = data_override or resolve_rel_path(event_section.get("data_file"), "data")
        if not data_file or not os.path.exists(data_file):
            data_dir = os.path.join(event_dir, "data")
            csv_files = glob.glob(os.path.join(data_dir, "*.csv")) if os.path.exists(data_dir) else []
            if csv_files:
                data_file = csv_files[0]
            elif os.path.exists(os.path.join(event_dir, "timesheet.csv")):
                data_file = os.path.join(event_dir, "timesheet.csv")
            elif os.path.exists(os.path.abspath("data/timesheet.csv")):
                data_file = os.path.abspath("data/timesheet.csv")
            else:
                data_file = os.path.join(data_dir, "timesheet.csv")

        # Resolve output path
        output_dir = output_override or event_section.get("output_dir")
        if not output_dir:
            output_dir = os.path.join(event_dir, "certs")
        elif not os.path.isabs(output_dir):
            output_dir = os.path.join(event_dir, output_dir)

        # Resolve global font and color
        font_path = event_section.get("font_path", "news-serif.ttf")
        if not os.path.isabs(font_path) and not os.path.exists(font_path):
            event_font = os.path.join(event_dir, font_path)
            if os.path.exists(event_font):
                font_path = event_font
            else:
                root_font = os.path.abspath("news-serif.ttf")
                if os.path.exists(root_font):
                    font_path = root_font

        text_color_raw = event_section.get("text_color", "0,0,0")
        text_color = parse_color(text_color_raw)
        name_field = event_section.get("name_field", "name")

        # Resolve field-level configurations
        fields: Dict[str, FieldConfig] = {}
        ignored_sections = {"event", "general", "image"}

        for section in config.sections():
            if section in ignored_sections:
                continue

            field_name = section.lower()
            height = config.getint(section, "height", fallback=0)
            
            # Width is optional
            width = None
            if config.has_option(section, "width"):
                w_val = config.getint(section, "width")
                if w_val > 0:
                    width = w_val

            left_offset = config.getint(section, "width_offset_left", fallback=0)
            right_offset = config.getint(section, "width_offset_right", fallback=0)
            f_size = config.getint(section, "font_size", fallback=40)
            
            f_path = config.get(section, "font_path", fallback=None)
            f_color_raw = config.get(section, "color", fallback=None)
            f_color = parse_color(f_color_raw) if f_color_raw else None

            fields[field_name] = FieldConfig(
                name=field_name,
                height=height,
                width=width,
                width_offset_left=left_offset,
                width_offset_right=right_offset,
                font_size=f_size,
                font_path=f_path,
                color=f_color,
            )

        return EventConfig(
            event_name=event_name,
            event_dir=event_dir,
            config_file=config_file,
            template_path=template_path,
            data_file=data_file,
            output_dir=output_dir,
            font_path=font_path,
            text_color=text_color,
            name_field=name_field,
            fields=fields,
        )
