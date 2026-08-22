import os
import tempfile
import unittest
import shutil
from unittest.mock import MagicMock, patch
from PIL import Image

from fill_certificates.config import EventConfig, FieldConfig
from fill_certificates.processor import EventProcessor
from fill_certificates.gdrive import GoogleDriveUploader


class TestGoogleDriveIntegration(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.template_path = os.path.join(self.test_dir, "template.jpg")
        img = Image.new("RGB", (800, 600), color="white")
        img.save(self.template_path)

        self.data_path = os.path.join(self.test_dir, "data.csv")
        with open(self.data_path, "w", encoding="utf-8") as f:
            f.write("name,distance\n")
            f.write('"Alice","5 km"\n')
            f.write('"Bob","10 km"\n')

        self.output_dir = os.path.join(self.test_dir, "certs")
        self.creds_file = os.path.join(self.test_dir, "credentials.json")
        with open(self.creds_file, "w") as f:
            f.write("{}")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_gdrive_uploader_missing_creds(self):
        with self.assertRaises(FileNotFoundError):
            GoogleDriveUploader(credentials_file=os.path.join(self.test_dir, "non_existent.json"))

    @patch("fill_certificates.gdrive.GoogleDriveUploader._init_service")
    def test_gdrive_upload_file_mock(self, mock_init):
        uploader = GoogleDriveUploader(credentials_file=self.creds_file)
        mock_service = MagicMock()
        mock_create = MagicMock()
        mock_create.execute.return_value = {
            "id": "file_12345",
            "webViewLink": "https://drive.google.com/file/d/file_12345/view?usp=sharing"
        }
        mock_service.files().create.return_value = mock_create
        mock_service.permissions().create.return_value = MagicMock()
        uploader.service = mock_service

        link = uploader.upload_file(self.template_path, folder_id="folder_abc", make_public=True)
        self.assertEqual(link, "https://drive.google.com/file/d/file_12345/view?usp=sharing")

    @patch("fill_certificates.processor.GoogleDriveUploader")
    def test_event_processor_writes_gdrive_link_to_csv(self, mock_uploader_cls):
        mock_uploader = MagicMock()
        mock_uploader.upload_file.side_effect = [
            "https://drive.google.com/file/d/link_alice/view",
            "https://drive.google.com/file/d/link_bob/view"
        ]
        mock_uploader_cls.return_value = mock_uploader

        event_cfg = EventConfig(
            event_name="gdrive_event",
            event_dir=self.test_dir,
            config_file=os.path.join(self.test_dir, "config.ini"),
            template_path=self.template_path,
            data_file=self.data_path,
            output_dir=self.output_dir,
            upload_gdrive=True,
            gdrive_folder_id="folder_xyz",
            gdrive_credentials_file=self.creds_file,
            gdrive_url_column="certificate_url",
            fields={
                "name": FieldConfig(name="name", height=100, font_size=40),
            },
        )

        res = EventProcessor.process_event(event_cfg)
        self.assertEqual(res["success"], 2)
        self.assertEqual(len(res["uploaded_links"]), 2)

        # Read updated CSV and verify certificate_url column was added
        with open(self.data_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("certificate_url", content)
        self.assertIn("https://drive.google.com/file/d/link_alice/view", content)
        self.assertIn("https://drive.google.com/file/d/link_bob/view", content)


if __name__ == "__main__":
    unittest.main()
