import unittest
import uuid
from pathlib import Path

from download_utils import is_valid_pinterest_url, resolve_download_file


class MainHelperTests(unittest.TestCase):
    def test_valid_pinterest_url(self):
        self.assertTrue(
            is_valid_pinterest_url("https://www.pinterest.com/user/my-board/")
        )
        self.assertTrue(
            is_valid_pinterest_url("https://br.pinterest.com/user/my-board/")
        )

    def test_invalid_pinterest_url(self):
        self.assertFalse(is_valid_pinterest_url("https://example.com/user/board"))
        self.assertFalse(is_valid_pinterest_url("ftp://pinterest.com/user/board"))
        self.assertFalse(is_valid_pinterest_url("https://www.pinterest.com/"))

    def test_valid_download_file_resolution(self):
        filename = f"{uuid.uuid4()}.zip"
        resolved = resolve_download_file(Path("downloads"), filename)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.name, filename)

    def test_invalid_download_file_resolution(self):
        self.assertIsNone(resolve_download_file(Path("downloads"), "../secret.zip"))
        self.assertIsNone(resolve_download_file(Path("downloads"), "not-a-uuid.zip"))
        self.assertIsNone(resolve_download_file(Path("downloads"), "archive.tar.gz"))


if __name__ == "__main__":
    unittest.main()
