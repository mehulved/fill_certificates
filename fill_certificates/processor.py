"""
Batch processing logic for event certificate generation.
"""

import csv
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .config import ConfigManager, EventConfig
from .generator import CertificateGenerator

logger = logging.getLogger(__name__)


class EventProcessor:
    """Manages CSV data loading and batch processing of certificates for events."""

    @staticmethod
    def process_event(event_config: EventConfig, run_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a single event by reading its CSV data and creating output certificates."""
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

        processed_count = 0
        success_count = 0
        error_count = 0
        output_files: List[str] = []

        with open(event_config.data_file, mode="r", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",", quotechar='"')
            for row in reader:
                processed_count += 1
                try:
                    out_path = CertificateGenerator.generate_certificate(
                        data_row=row,
                        event_config=event_config,
                    )
                    success_count += 1
                    output_files.append(out_path)
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error generating certificate for row {row}: {e}", exc_info=True)

        summary = {
            "event_name": event_config.event_name,
            "run_id": run_id,
            "timestamp": str(datetime.now()),
            "processed": processed_count,
            "success": success_count,
            "error": error_count,
            "output_files": output_files,
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
