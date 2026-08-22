import os
import tempfile
import unittest
import shutil

from fill_certificates.config import ConfigManager, parse_color


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_color(self):
        self.assertEqual(parse_color("#FF0000"), (255, 0, 0))
        self.assertEqual(parse_color("0,128,255"), (0, 128, 255))
        self.assertEqual(parse_color(""), (0, 0, 0))

    def test_load_event_config_defaults(self):
        config_path = os.path.join(self.test_dir, "config.ini")
        with open(config_path, "w") as f:
            f.write("""
[event]
template=template.jpg
data_file=data/test.csv
output_dir=certs
text_color=255,0,0

[name]
height=100
font_size=50

[score]
height=200
width=300
font_size=30
""")

        cfg = ConfigManager.load_event_config(event_dir=self.test_dir)
        self.assertEqual(cfg.event_name, os.path.basename(self.test_dir))
        self.assertEqual(cfg.text_color, (255, 0, 0))
        self.assertIn("name", cfg.fields)
        self.assertIn("score", cfg.fields)
        self.assertEqual(cfg.fields["name"].height, 100)
        self.assertEqual(cfg.fields["name"].font_size, 50)
        self.assertEqual(cfg.fields["score"].width, 300)

    def test_discover_events(self):
        events_dir = os.path.join(self.test_dir, "events")
        os.makedirs(os.path.join(events_dir, "event1"))
        os.makedirs(os.path.join(events_dir, "event2"))

        discovered = ConfigManager.discover_events(events_dir)
        self.assertEqual(discovered, ["event1", "event2"])


if __name__ == "__main__":
    unittest.main()
