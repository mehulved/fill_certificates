"""
Google Drive integration module for uploading certificates and generating public view links.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GoogleDriveUploader:
    """Handles authentication and file uploads to Google Drive."""

    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.service = None
        self._init_service()

    def _init_service(self):
        if not self.credentials_file or not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Google Drive credentials file not found: '{self.credentials_file}'"
            )

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/drive.file"]
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES
            )
            self.service = build("drive", "v3", credentials=creds)
            logger.info(f"Successfully authenticated with Google Drive API using {self.credentials_file}")
        except ImportError:
            raise ImportError(
                "Google Drive API client packages not installed. "
                "Please install them via: pip install google-api-python-client google-auth google-auth-httplib2"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            raise

    def upload_file(
        self,
        file_path: str,
        folder_id: Optional[str] = None,
        make_public: bool = True,
    ) -> str:
        """
        Uploads a local file to Google Drive and returns the public view link.
        """
        if not self.service:
            raise RuntimeError("Google Drive service is not initialized.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File to upload not found: {file_path}")

        filename = os.path.basename(file_path)
        file_metadata = {"name": filename}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        try:
            from googleapiclient.http import MediaFileUpload
            media = MediaFileUpload(file_path, resumable=True)
        except ImportError:
            # Fallback mock/dummy media if googleapiclient is mocked in test environment
            media = None

        logger.info(f"Uploading '{filename}' to Google Drive (Folder ID: {folder_id or 'Root'})...")
        file_obj = (
            self.service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink, webContentLink",
            )
            .execute()
        )

        file_id = file_obj.get("id")
        web_link = file_obj.get("webViewLink", f"https://drive.google.com/file/d/{file_id}/view")

        if make_public and file_id:
            logger.info(f"Setting public read permission for Google Drive file ID: {file_id}")
            permission = {
                "type": "anyone",
                "role": "reader",
            }
            self.service.permissions().create(fileId=file_id, body=permission).execute()

        logger.info(f"Successfully uploaded to Google Drive. Link: {web_link}")
        return web_link
