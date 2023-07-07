class Events:
    def __init__(self, config, template, timesheet, text_color):
        self.config = config
        self.template = template
        self.timesheet = timesheet
        self.text_color = text_color

    def read_config(self):
        import configparser
        import logging
        logger = logging.getLogger(__name__)

        config = configparser.ConfigParser()
        config.read(self.config)
        config_dump = {}
        for each_section in config.sections():
            for (each_key, each_val) in config.items(each_section):
                config_dump[each_key] = each_val
        logger.debug({"config": config_dump})
        return config

    def get_dimensions(*, image, font, item, config, key):
        import logging
        logger = logging.getLogger(__name__)

        image_width, image_height = image.size
        logger.info({
            "image": {
                "width": image_width,
                "height": image_height
            }
        })
        canvas_width, canvas_height = font.getsize(item)
        try:
            item_width = config.getint(key, 'width', fallback=0)
        except KeyError:
            item_canvas_center = int((image_width - canvas_width) / 2)
            item_left_offset = config.getint(key, 'width_offset_left', fallback=0)
            item_right_offset = config.getint(key, 'width_offset_right', fallback=0)
            item_width = item_left_offset + item_canvas_center - item_right_offset
        try:
            item_height = int(config.get(key, 'height'))
        except KeyError:
            raise
        dimensions = (item_width, item_height)
        return dimensions

    def fill(self, data, template, uuid, cert_dir):
        from datetime import datetime
        from PIL import Image
        from PIL import ImageFont
        from PIL import ImageDraw
        import logging
        logger = logging.getLogger(__name__)

        config = read_config(self)
        logger.info({
            "data": data,
        })
        img = Image.open(template)
        draw = ImageDraw.Draw(img)
        # Credits:
        # https://stackoverflow.com/questions/1970807/center-middle-align-text-with-pil

        for key, value in data.items():
            logger.info({
                key: value
            })
            item = data[key].strip()
            font_size = config.getint(key, 'font_size')
            font = ImageFont.truetype(r'./news-serif.ttf', font_size)

            item_dimensions = get_dimensions(image=img, font=font, item=item, config=config, key=key)
            item_colour = self.text_color
            draw.text(item_dimensions, item, item_colour, font=font)

        cert_name = data['name'].lower().replace(' ', '_')
        cert_path = f'{cert_dir}/{cert_name}.jpg'
        try:
            img.save(cert_path)
            img.close()
            logger.info({
                "status": "saved",
                "certificate": cert_path,
                "identifier": uuid,
                "time": str(datetime.now())
            })
        except FileNotFoundError:
            logger.error({
                "status": "error",
                "exception": "Unable to save file. Please check the given directory exists.",
                "identifier": uuid,
                "time": datetime.now()
            })
            exit(1)
