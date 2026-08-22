"""
Batch processing logic for event certificate generation and optional Google Drive uploads.
"""

import csv
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .config import ConfigManager, EventConfig
from .generator import CertificateGenerator
from .gdrive import GoogleDriveUploader

logger = logging.getLogger(__name__)


class EventProcessor:
    """Manages CSV data loading, batch certificate generation, and optional Google Drive uploads."""

    @staticmethod
    def process_event(event_config: EventConfig, run_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a single event by reading its CSV data, creating output certificates, and updating CSV links."""
        if not run_id:
            run_id = str(uuid.uuid4())

        logger.info(f"Starting certificate generation for event '{event_config.event_name}' (Run ID: {run_id})")
        logger.info(f"Using template: {event_config.template_path}")
        logger.info(f"Using data file: {event_config.data_file}")
        logger.info(f"Output directory: {event_config.output_dir}")

        if not os.path.exists(event_config.data_file):
            raise FileNotFoundError(
                f"Data file '{event_config.data_file}' not found for event '{event_config.event_name}'."
            )

        uploader = None
        if event_config.upload_gdrive:
            logger.info("Google Drive upload enabled. Initializing Uploader...")
            uploader = GoogleDriveUploader(credentials_file=event_config.gdrive_credentials_file)

        rows: List[Dict[str, Any]] = []
        fieldnames: List[str] = []

        with open(event_config.data_file, mode="r", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",", quotechar='"')
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

        url_col = event_config.gdrive_url_column
        if event_config.upload_gdrive and url_col not in fieldnames:
            fieldnames.append(url_col)

        processed_count = 0
        success_count = 0
        error_count = 0
        output_files: List[str] = []
        uploaded_links: List[str] = []

        for row in rows:
            processed_count += 1
            try:
                out_path = CertificateGenerator.generate_certificate(
                    data_row=row,
                    event_config=event_config,
                )
                success_count += 1
                output_files.append(out_path)

                if uploader:
                    web_link = uploader.upload_file(
                        file_path=out_path,
                        folder_id=event_config.gdrive_folder_id,
                        make_public=event_config.gdrive_public,
                    )
                    row[url_col] = web_link
                    uploaded_links.append(web_link)
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing row {row}: {e}", exc_info=True)

        # Write updated CSV back if Google Drive links were generated
        if event_config.upload_gdrive and uploaded_links:
            logger.info(f"Updating CSV data file '{event_config.data_file}' with generated Google Drive links in column '{url_col}'...")
            with open(event_config.data_file, mode="w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                writer.writerows(rows)

        summary = {
            "event_name": event_config.event_name,
            "run_id": run_id,
            "timestamp": str(datetime.now()),
            "processed": processed_count,
            "success": success_count,
            "error": error_count,
            "output_files": output_files,
            "uploaded_links": uploaded_links,
        }

        logger.info(
            f"Completed event '{event_config.event_name}': {success_count}/{processed_count} generated successfully."
        )
        return summary

    @classmethod
    def discover_and_process_all(cls, events_root: str = "events") -> List[Dict[str, Any]]:
        """Find all event directories in events_root and process them sequentially."""
        event_names = ConfigManager.discover_events(events_root)
        if not event_names:
            logger.warning(f"No event directories found in '{events_root}'.")
            return []

        results = []
        for event_name in event_names:
            event_dir = os.path.join(events_root, event_name)
            logger.info(f"Processing discovered event in directory: {event_dir}")
            cfg = ConfigManager.load_event_config(event_dir=event_dir)
            res = cls.process_event(cfg)
            results.append(res)
        return results
