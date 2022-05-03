#!/usr/bin/env python

import csv
import argparse
import logging
from datetime import datetime
import uuid
from certificate import fill

logging.basicConfig(level=logging.DEBUG)
run_id = str(uuid.uuid4())
logging.info({
    "status": "started",
    "identifier": run_id,
    "time": str(datetime.now())
})

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
    output_path = args.outputpath
else:
    output_path = "certs"

if args.certificatefile:
    certificate_template = args.certificatefile
else:
    certificate_template = "./certificate-template.jpg"

logging.info({
    "timesheet": filepath,
    "certificate_directory": output_path,
    "certificate_template": certificate_template
})


with open(filepath) as csvfile:
    tsreader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in tsreader:
        logging.info({"data": row, "time": str(datetime.now())})
        fill(row, certificate_template, run_id, output_path)

logging.info({
    "status": "completed",
    "identifier": run_id,
    "time": str(datetime.now())
})
