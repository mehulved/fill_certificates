import os
import tempfile
import unittest
import shutil
from PIL import Image

from fill_certificates.config import EventConfig, FieldConfig
from fill_certificates.processor import EventProcessor


class TestEventProcessor(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.template_path = os.path.join(self.test_dir, "template.jpg")
        img = Image.new("RGB", (800, 600), color="white")
        img.save(self.template_path)

        self.data_path = os.path.join(self.test_dir, "data.csv")
        with open(self.data_path, "w", encoding="utf-8") as f:
            f.write("name,rank\n")
            f.write('"Bob Jones","1st"\n')
            f.write('"Carol Danvers","2nd"\n')

        self.output_dir = os.path.join(self.test_dir, "certs")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_process_event(self):
        event_cfg = EventConfig(
            event_name="race_2026",
            event_dir=self.test_dir,
            config_file=os.path.join(self.test_dir, "config.ini"),
            template_path=self.template_path,
            data_file=self.data_path,
            output_dir=self.output_dir,
            fields={
                "name": FieldConfig(name="name", height=150, font_size=36),
                "rank": FieldConfig(name="rank", height=250, font_size=28),
            },
        )

        res = EventProcessor.process_event(event_cfg)
        self.assertEqual(res["processed"], 2)
        self.assertEqual(res["success"], 2)
        self.assertEqual(res["error"], 0)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "bob_jones.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "carol_danvers.jpg")))


if __name__ == "__main__":
    unittest.main()
