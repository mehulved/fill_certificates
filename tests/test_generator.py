import os
import tempfile
import unittest
import shutil
from PIL import Image

from fill_certificates.config import EventConfig, FieldConfig
from fill_certificates.generator import CertificateGenerator


class TestCertificateGenerator(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.template_path = os.path.join(self.test_dir, "template.jpg")
        img = Image.new("RGB", (800, 600), color="white")
        img.save(self.template_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_generate_certificate(self):
        output_dir = os.path.join(self.test_dir, "certs")
        event_cfg = EventConfig(
            event_name="test_event",
            event_dir=self.test_dir,
            config_file=os.path.join(self.test_dir, "config.ini"),
            template_path=self.template_path,
            data_file=os.path.join(self.test_dir, "data.csv"),
            output_dir=output_dir,
            fields={
                "name": FieldConfig(name="name", height=100, font_size=40),
                "score": FieldConfig(name="score", height=200, font_size=30, width=400),
            },
        )

        data_row = {"name": "Alice Smith", "score": "95"}
        out_path = CertificateGenerator.generate_certificate(data_row, event_cfg)

        self.assertTrue(os.path.exists(out_path))
        self.assertTrue(out_path.endswith("alice_smith.jpg"))
        # Check generated image can be opened
        res_img = Image.open(out_path)
        self.assertEqual(res_img.size, (800, 600))
        res_img.close()


if __name__ == "__main__":
    unittest.main()
