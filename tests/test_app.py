import io
import re
import unittest

from PIL import Image
import app as app_module


class ImageForensicsWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_module.app.config["TESTING"] = True
        cls.client = app_module.app.test_client()

    @staticmethod
    def make_image(fmt="PNG"):
        stream = io.BytesIO()
        Image.new("RGB", (48, 32), (120, 80, 200)).save(stream, format=fmt)
        stream.seek(0)
        return stream

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Image Forensics Lab", response.data)

    def test_unsupported_extension_rejected(self):
        response = self.client.post(
            "/analyze",
            data={"image": (io.BytesIO(b"hello"), "notes.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Unsupported extension", response.data)

    def test_corrupt_image_rejected(self):
        response = self.client.post(
            "/analyze",
            data={"image": (io.BytesIO(b"not an image"), "fake.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"could not be decoded", response.data)

    def test_png_analysis_and_pdf(self):
        response = self.client.post(
            "/analyze",
            data={"image": (self.make_image("PNG"), "sample.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SHA-256 file hash", response.data)
        match = re.search(rb'href="(/report/[a-f0-9]{32})"', response.data)
        self.assertIsNotNone(match)
        pdf_response = self.client.get(match.group(1).decode())
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response.mimetype, "application/pdf")
        self.assertTrue(pdf_response.data.startswith(b"%PDF"))

    def test_jpeg_analysis_includes_ela(self):
        response = self.client.post(
            "/analyze",
            data={"image": (self.make_image("JPEG"), "sample.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Error Level Analysis", response.data)
        self.assertIn(b".png", response.data)


if __name__ == "__main__":
    unittest.main()
