#!/usr/bin/env python

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import csv
import configparser
import argparse
import logging
from datetime import datetime
import uuid

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


config = configparser.ConfigParser()
config.read('config.ini')
config_dump = {}
for each_section in config.sections():
    for (each_key, each_val) in config.items(each_section):
        config_dump[each_key] = each_val
logging.debug({"config": config_dump})


with open(filepath) as csvfile:
    tsreader = csv.DictReader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in tsreader:
        logging.info({
            "item": row,
            "time": str(datetime.now())
        })
        img = Image.open(certificate_template)
        draw = ImageDraw.Draw(img)
        # Credits:
        # https://stackoverflow.com/questions/1970807/center-middle-align-text-with-pil

        W, H = img.size
        logging.info({
            "image": {
                "width": W,
                "height": H
            }
        })
        for key, value in row.items():
            logging.info({
                key: value
            })
            item = row[key].strip()
            font_size = config.getint(key, 'font_size')
            font = ImageFont.truetype(r'./news-serif.ttf', font_size)
            w, h = font.getsize(item)
            item_left_offset = config.getint(key, 'width_offset_left', fallback=0)
            item_right_offset = config.getint(key, 'width_offset_right', fallback=0)
            try:
                item_width = config.getint(key, 'width', fallback=0)
            except KeyError:
                item_canvas_center = int((W-w)/2)
                item_width = item_left_offset + item_canvas_center - item_right_offset
            item_height = int(config.get(key, 'height'))
            draw.text((item_width, item_height), item, (0, 0, 0), font=font)

        cert_name = row['name'].lower().replace(' ', '_')
        cert_path = f'{output_path}/{cert_name}.jpg'
        try:
            img.save(cert_path)
            img.close()
            logging.info({
                "status": "saved",
                "certificate": cert_path,
                "time": str(datetime.now())
            })
        except FileNotFoundError:
            logging.error({
                "status": "error",
                "exception": "Unable to save file. Please check the given directory exists.",
                "identifier": run_id,
                "time": datetime.now()
            })
            exit(1)
logging.info({
    "status": "completed",
    "identifier": run_id,
    "time": str(datetime.now())
})
