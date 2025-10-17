"""
Unit tests for error handling and edge cases in the Genalog API.
"""

import io
from unittest.mock import patch, MagicMock
from pathlib import Path
from fastapi import status


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_document_generator_import_error(self, client, sample_text):
        """Test handling when DocumentGenerator can't be imported."""
        with patch('src.genalog_api.api.main.DocumentGenerator', side_effect=ImportError("genalog not installed")):
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "genalog not installed" in response.json()["detail"]
    
    def test_file_io_error(self, client, sample_text, mock_document_generator):
        """Test handling of file I/O errors."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("builtins.open", side_effect=IOError("File not found")), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "File not found" in response.json()["detail"]
    
    def test_temp_file_creation_error(self, client, sample_text):
        """Test handling when temporary file creation fails."""
        with patch("tempfile.NamedTemporaryFile", side_effect=OSError("No space left on device")):
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "No space left on device" in response.json()["detail"]
    
    def test_temp_directory_creation_error(self, client, sample_text, mock_document_generator):
        """Test handling when temporary directory creation fails."""
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory", side_effect=OSError("Permission denied")), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Permission denied" in response.json()["detail"]
    
    def test_base64_encoding_error(self, client, sample_text, mock_document_generator):
        """Test handling when base64 encoding fails."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("builtins.open") as mock_open, \
             patch("base64.b64encode", side_effect=Exception("Encoding error")), \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            mock_open.return_value.__enter__.return_value.read.return_value = b"fake_image_data"
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Encoding error" in response.json()["detail"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_text(self, client, mock_document_generator, sample_image_bytes):
        """Test with very long text input."""
        long_text = "A" * 10000  # 10KB of text
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open") as mock_open, \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_open.return_value.__enter__.return_value.read.return_value = sample_image_bytes
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {"text": long_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_empty_text(self, client, mock_document_generator, sample_image_bytes):
        """Test with empty text input."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open") as mock_open, \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_open.return_value.__enter__.return_value.read.return_value = sample_image_bytes
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {"text": ""}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_special_characters_text(self, client, mock_document_generator, sample_image_bytes):
        """Test with special characters and Unicode."""
        special_text = "Hello 世界! 🌍 Special chars: àáâãäå ñ ü ß"
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open") as mock_open, \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_open.return_value.__enter__.return_value.read.return_value = sample_image_bytes
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {"text": special_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_extreme_dimensions(self, client, sample_text, mock_document_generator, sample_image_bytes):
        """Test with extreme width and height values."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open") as mock_open, \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_open.return_value.__enter__.return_value.read.return_value = sample_image_bytes
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            # Test very large dimensions
            request_data = {
                "text": sample_text,
                "width": 10000,
                "height": 10000
            }
            response = client.post("/convert-text", json=request_data)
            assert response.status_code == status.HTTP_200_OK
            
            # Test very small dimensions
            request_data = {
                "text": sample_text,
                "width": 1,
                "height": 1
            }
            response = client.post("/convert-text", json=request_data)
            assert response.status_code == status.HTTP_200_OK
    
    def test_very_large_file_upload(self, client, mock_document_generator, sample_image_bytes):
        """Test uploading a very large file."""
        # Create a large file (1MB of text)
        large_content = "This is a test line.\n" * 50000
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open") as mock_open, \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_open.return_value.__enter__.return_value.read.return_value = sample_image_bytes
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            file_content = large_content.encode('utf-8')
            files = {"file": ("large_test.txt", io.BytesIO(file_content), "text/plain")}
            
            response = client.post("/convert-file", files=files)
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_invalid_utf8_sequences(self, client):
        """Test with files containing invalid UTF-8 sequences."""
        # Create content with invalid UTF-8 sequences
        invalid_utf8 = b"Valid text\xff\xfe\x00Invalid UTF-8"
        files = {"file": ("invalid.txt", io.BytesIO(invalid_utf8), "text/plain")}
        
        response = client.post("/convert-file", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "File must be a valid text file" in response.json()["detail"]