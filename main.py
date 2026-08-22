#!/usr/bin/env python
"""
Main CLI entry point for batch certificate generation.
"""

import sys
import os
import argparse
import logging
import uuid
from datetime import datetime

from fill_certificates import ConfigManager, EventProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("fill_certificates")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fill certificate templates from CSV data for single or multiple events."
    )
    parser.add_argument(
        "--event", "-e",
        help="Specify event name located in events/ directory (e.g., --event marathon_2026)"
    )
    parser.add_argument(
        "--event-dir", "-d",
        help="Specify custom event directory path containing config.ini, data/, certs/, template.jpg"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Process all events discovered under events/ directory"
    )
    parser.add_argument(
        "--list-events", "-l",
        action="store_true",
        help="List available event directories"
    )
    parser.add_argument(
        "--events-root",
        default="events",
        help="Root directory for event folders (default: events/)"
    )
    parser.add_argument(
        "--datafile",
        help="Override path to input CSV file"
    )
    parser.add_argument(
        "--outputpath",
        help="Override output directory path for certificates"
    )
    parser.add_argument(
        "--certificatefile",
        help="Override path to certificate template image"
    )
    parser.add_argument(
        "--config",
        help="Override path to config.ini file"
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    run_id = str(uuid.uuid4())

    logger.info(f"Certificate generator started (Run ID: {run_id})")

    # List events
    if args.list_events:
        events = ConfigManager.discover_events(args.events_root)
        if events:
            print(f"Discovered events in '{args.events_root}':")
            for ev in events:
                print(f" - {ev}")
        else:
            print(f"No event directories found in '{args.events_root}'.")
        return 0

    # Process all events
    if args.all:
        events = ConfigManager.discover_events(args.events_root)
        if not events:
            logger.warning(f"No events found in '{args.events_root}'.")
            return 0
        total_errors = 0
        for ev in events:
            ev_dir = os.path.join(args.events_root, ev)
            cfg = ConfigManager.load_event_config(
                event_dir=ev_dir,
                config_file=args.config,
                template_override=args.certificatefile,
                data_override=args.datafile,
                output_override=args.outputpath,
            )
            res = EventProcessor.process_event(cfg, run_id=run_id)
            total_errors += res.get("error", 0)
        return 1 if total_errors > 0 else 0

    # Resolve event directory for single run
    target_dir = "events/default" if os.path.exists("events/default") else "."
    if args.event_dir:
        target_dir = args.event_dir
    elif args.event:
        # Check if events/<event> exists, otherwise treat as path
        potential_dir = os.path.join(args.events_root, args.event)
        if os.path.exists(potential_dir):
            target_dir = potential_dir
        else:
            target_dir = args.event

    cfg = ConfigManager.load_event_config(
        event_dir=target_dir,
        config_file=args.config,
        template_override=args.certificatefile,
        data_override=args.datafile,
        output_override=args.outputpath,
    )

    try:
        summary = EventProcessor.process_event(cfg, run_id=run_id)
        logger.info(f"Run completed. Generated {summary['success']} certificates.")
        if summary.get("error", 0) > 0:
            return 1
        return 0
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
