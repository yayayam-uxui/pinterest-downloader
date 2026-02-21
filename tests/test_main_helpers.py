import unittest
import uuid

from main import _is_valid_pinterest_url, _resolve_download_file


class MainHelperTests(unittest.TestCase):
    def test_valid_pinterest_url(self):
        self.assertTrue(
            _is_valid_pinterest_url("https://www.pinterest.com/user/my-board/")
        )
        self.assertTrue(
            _is_valid_pinterest_url("https://br.pinterest.com/user/my-board/")
        )

    def test_invalid_pinterest_url(self):
        self.assertFalse(_is_valid_pinterest_url("https://example.com/user/board"))
        self.assertFalse(_is_valid_pinterest_url("ftp://pinterest.com/user/board"))
        self.assertFalse(_is_valid_pinterest_url("https://www.pinterest.com/"))

    def test_valid_download_file_resolution(self):
        filename = f"{uuid.uuid4()}.zip"
        resolved = _resolve_download_file(filename)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.name, filename)

    def test_invalid_download_file_resolution(self):
        self.assertIsNone(_resolve_download_file("../secret.zip"))
        self.assertIsNone(_resolve_download_file("not-a-uuid.zip"))
        self.assertIsNone(_resolve_download_file("archive.tar.gz"))


if __name__ == "__main__":
    unittest.main()
