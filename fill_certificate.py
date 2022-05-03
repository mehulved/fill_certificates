#!/usr/bin/env python

import csv
import argparse
import logging
from datetime import datetime
import uuid
from certificate import fill


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setup_paths():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datafile", help="Pass optional file path. Default: data/timesheet.csv")
    parser.add_argument("--outputpath", help="Pass optional output path. Default: certs/")
    parser.add_argument("--certificatefile", help="Pass optional certificate file. Default: ./certificate-template.jpg")
    args = parser.parse_args()

    if args.datafile:
        filepath = args.datafile
    else:
        filepath = f"data/timesheet.csv"

    if args.outputpath:
        cert_path = args.outputpath
    else:
        cert_path = "certs"

    if args.certificatefile:
        template = args.certificatefile
    else:
        template = "./certificate-template.jpg"

    logger.info({
        "timesheet": filepath,
        "certificate_directory": cert_path,
        "certificate_template": template
    })
    path_list = {
        "timesheet": filepath,
        "cert_path": cert_path,
        "template": template
    }
    return path_list


if __name__ == "__main__":
    # Logging
    run_id = str(uuid.uuid4())
    logger.info({
        "status": "started",
        "identifier": run_id,
        "time": str(datetime.now())
    })
    # Paths
    paths = setup_paths()
    timesheet = paths["timesheet"]
    certificate_template = paths["template"]
    output_path = paths["cert_path"]
    # Read data
    with open(timesheet) as csvfile:
        tsreader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in tsreader:
            logger.info({"data": row, "time": str(datetime.now())})
            fill(row, certificate_template, run_id, output_path)
    # Finish
    logger.info({
        "status": "completed",
        "identifier": run_id,
        "time": str(datetime.now())
    })
