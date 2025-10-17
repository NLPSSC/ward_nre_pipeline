"""
Integration tests for the Genalog API.
"""

import base64
import io
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestAPIIntegration:
    """Test API endpoints integration."""

    def test_full_text_to_image_workflow(
        self, client, sample_text, mock_document_generator, sample_image_bytes
    ):
        """Test the complete workflow from text to image."""
        # Setup mock
        mock_document_generator.create_img_from_text.return_value = [
            Path("/fake/path/image.png")
        ]

        with (
            patch("builtins.open") as mock_open_func,
            patch("tempfile.NamedTemporaryFile") as mock_temp_file,
            patch("tempfile.TemporaryDirectory") as mock_temp_dir,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink"),
        ):
            # Setup file mocking
            mock_open_func.return_value.__enter__.return_value.read.return_value = (
                sample_image_bytes
            )
            mock_temp_file.return_value.__enter__.return_value.name = (
                "/fake/temp/file.txt"
            )
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"

            # Step 1: Check API is healthy
            health_response = client.get("/health")
            assert health_response.status_code == 200

            # Step 2: Check API info
            root_response = client.get("/")
            assert root_response.status_code == 200

            # Step 3: Convert text to image
            text_request = {
                "text": sample_text,
                "image_format": "png",
                "width": 1024,
                "height": 768,
            }

            convert_response = client.post("/convert-text", json=text_request)
            assert convert_response.status_code == 200

            # Validate response
            convert_data = convert_response.json()
            assert "image_base64" in convert_data
            assert convert_data["image_format"] == "png"
            assert convert_data["message"] == "Text successfully converted to image"

            # Verify base64 can be decoded
            image_data = base64.b64decode(convert_data["image_base64"])
            assert len(image_data) > 0

    def test_file_upload_workflow(
        self, client, sample_text, mock_document_generator, sample_image_bytes
    ):
        """Test the complete file upload to image workflow."""
        mock_document_generator.create_img_from_text.return_value = [
            Path("/fake/path/image.jpg")
        ]

        with (
            patch("builtins.open") as mock_open_func,
            patch("tempfile.NamedTemporaryFile") as mock_temp_file,
            patch("tempfile.TemporaryDirectory") as mock_temp_dir,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink"),
        ):
            # Setup file mocking
            mock_open_func.return_value.__enter__.return_value.read.return_value = (
                sample_image_bytes
            )
            mock_temp_file.return_value.__enter__.return_value.name = (
                "/fake/temp/file.txt"
            )
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"

            # Create test file
            file_content = sample_text.encode("utf-8")
            files = {"file": ("document.txt", io.BytesIO(file_content), "text/plain")}
            data = {"image_format": "jpg", "width": 1200, "height": 900}

            # Upload and convert file
            response = client.post("/convert-file", files=files, data=data)

            assert response.status_code == 200
            assert response.headers["content-type"] == "image/jpg"
            assert "converted_image.jpg" in response.headers["content-disposition"]

            # Verify response contains image data
            assert len(response.content) > 0

    def test_error_handling_workflow(
        self, client, sample_text, mock_document_generator
    ):
        """Test error handling across different scenarios."""
        # Test with document generation failure
        mock_document_generator.create_img_from_text.return_value = []

        with (
            patch("tempfile.NamedTemporaryFile") as mock_temp_file,
            patch("tempfile.TemporaryDirectory") as mock_temp_dir,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink"),
        ):
            mock_temp_file.return_value.__enter__.return_value.name = (
                "/fake/temp/file.txt"
            )
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"

            # Should fail with no documents generated
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)

            assert response.status_code == 500
            assert "Failed to generate image from text" in response.json()["detail"]

    def test_concurrent_requests_simulation(
        self, client, sample_text, mock_document_generator, sample_image_bytes
    ):
        """Simulate multiple concurrent requests."""
        mock_document_generator.create_img_from_text.return_value = [
            Path("/fake/path/image.png")
        ]

        with (
            patch("builtins.open") as mock_open_func,
            patch("tempfile.NamedTemporaryFile") as mock_temp_file,
            patch("tempfile.TemporaryDirectory") as mock_temp_dir,
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.unlink"),
        ):
            mock_open_func.return_value.__enter__.return_value.read.return_value = (
                sample_image_bytes
            )
            mock_temp_file.return_value.__enter__.return_value.name = (
                "/fake/temp/file.txt"
            )
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"

            # Simulate multiple requests
            responses = []
            for i in range(3):
                request_data = {
                    "text": f"{sample_text} - Request {i}",
                    "image_format": "png",
                }
                response = client.post("/convert-text", json=request_data)
                responses.append(response)

            # All should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert "image_base64" in data

    def test_different_formats_workflow(
        self, client, sample_text, mock_document_generator, sample_image_bytes
    ):
        """Test workflow with different image formats."""
        formats = ["png", "jpg", "gif"]

        for fmt in formats:
            mock_document_generator.create_img_from_text.return_value = [
                Path(f"/fake/path/image.{fmt}")
            ]

            with (
                patch("builtins.open") as mock_open_func,
                patch("tempfile.NamedTemporaryFile") as mock_temp_file,
                patch("tempfile.TemporaryDirectory") as mock_temp_dir,
                patch("pathlib.Path.exists", return_value=True),
                patch("pathlib.Path.unlink"),
            ):
                mock_open_func.return_value.__enter__.return_value.read.return_value = (
                    sample_image_bytes
                )
                mock_temp_file.return_value.__enter__.return_value.name = (
                    "/fake/temp/file.txt"
                )
                mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
                mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"

                request_data = {"text": sample_text, "image_format": fmt}

                response = client.post("/convert-text", json=request_data)

                assert response.status_code == 200
                data = response.json()
                assert data["image_format"] == fmt
