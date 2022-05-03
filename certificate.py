#!/usr/bin/env python

def fill(data, template, uuid, cert_dir):
    import configparser
    import logging
    from datetime import datetime
    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw

    config = configparser.ConfigParser()
    config.read('config.ini')
    config_dump = {}
    for each_section in config.sections():
        for (each_key, each_val) in config.items(each_section):
            config_dump[each_key] = each_val
    logging.debug({"config": config_dump})

    logging.info({
        "data": data,
    })
    img = Image.open(template)
    draw = ImageDraw.Draw(img)
    # Credits:
    # https://stackoverflow.com/questions/1970807/center-middle-align-text-with-pil

    image_width, image_height = img.size
    logging.info({
        "image": {
            "width": image_width,
            "height": image_height
        }
    })
    for key, value in data.items():
        logging.info({
            key: value
        })
        item = data[key].strip()
        font_size = config.getint(key, 'font_size')
        font = ImageFont.truetype(r'./news-serif.ttf', font_size)
        w, h = font.getsize(item)
        try:
            item_width = config.getint(key, 'width', fallback=0)
        except KeyError:
            item_canvas_center = int((image_width-w)/2)
            item_left_offset = config.getint(key, 'width_offset_left', fallback=0)
            item_right_offset = config.getint(key, 'width_offset_right', fallback=0)
            item_width = item_left_offset + item_canvas_center - item_right_offset
        item_height = int(config.get(key, 'height'))
        draw.text((item_width, item_height), item, (0, 0, 0), font=font)

    cert_name = data['name'].lower().replace(' ', '_')
    cert_path = f'{cert_dir}/{cert_name}.jpg'
    try:
        img.save(cert_path)
        img.close()
        logging.info({
            "status": "saved",
            "certificate": cert_path,
            "identifier": uuid,
            "time": str(datetime.now())
        })
    except FileNotFoundError:
        logging.error({
            "status": "error",
            "exception": "Unable to save file. Please check the given directory exists.",
            "identifier": uuid,
            "time": datetime.now()
        })
        exit(1)
