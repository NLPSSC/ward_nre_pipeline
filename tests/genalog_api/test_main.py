"""
Unit tests for the Genalog API main endpoints.
"""

import io
from fastapi import status
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_returns_api_info(self, client):
        """Test that root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "Genalog Text-to-Image API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert data["endpoints"]["convert_text"] == "/convert-text"
        assert data["endpoints"]["convert_file"] == "/convert-file"
        assert data["endpoints"]["health"] == "/health"


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "genalog-api"


class TestConvertTextEndpoint:
    """Test the convert text to image endpoint."""
    
    def test_convert_text_success(self, client, sample_text, sample_base64_image, mock_document_generator, sample_image_bytes):
        """Test successful text to image conversion."""
        # Mock the document generator to return a fake image path
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        # Mock file operations
        with patch("builtins.open", mock_open(read_data=sample_image_bytes)), \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir:
            
            # Mock temporary file
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            
            # Mock temporary directory
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            # Mock Path operations
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.unlink") as mock_unlink:
                
                request_data = {
                    "text": sample_text,
                    "image_format": "png",
                    "width": 800,
                    "height": 600
                }
                
                response = client.post("/convert-text", json=request_data)
                
                assert response.status_code == status.HTTP_200_OK
                
                data = response.json()
                assert "image_base64" in data
                assert data["image_format"] == "png"
                assert data["message"] == "Text successfully converted to image"
                
                # Verify the document generator was called correctly
                mock_document_generator.create_img_from_text.assert_called_once()
                
                # Verify cleanup
                mock_unlink.assert_called_once()
    
    def test_convert_text_default_parameters(self, client, sample_text, sample_base64_image, mock_document_generator, sample_image_bytes):
        """Test text conversion with default parameters."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open", mock_open(read_data=sample_image_bytes)), \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["image_format"] == "png"  # Default format
    
    def test_convert_text_no_documents_generated(self, client, sample_text, mock_document_generator):
        """Test when no documents are generated."""
        mock_document_generator.create_img_from_text.return_value = []
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to generate image from text" in response.json()["detail"]
    
    def test_convert_text_exception_handling(self, client, sample_text, mock_document_generator):
        """Test exception handling in text conversion."""
        mock_document_generator.create_img_from_text.side_effect = Exception("Test error")
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Error converting text to image: Test error" in response.json()["detail"]
    
    def test_convert_text_invalid_request(self, client):
        """Test invalid request data."""
        # Missing required 'text' field
        response = client.post("/convert-text", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_convert_text_custom_parameters(self, client, sample_text, sample_base64_image, mock_document_generator, sample_image_bytes):
        """Test text conversion with custom parameters."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.jpg")]
        
        with patch("builtins.open", mock_open(read_data=sample_image_bytes)), \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {
                "text": sample_text,
                "image_format": "jpg",
                "width": 1024,
                "height": 768,
                "font_size": 14,
                "font_family": "Times New Roman"
            }
            
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            assert data["image_format"] == "jpg"


class TestConvertFileEndpoint:
    """Test the convert file to image endpoint."""
    
    def test_convert_file_success(self, client, sample_text, sample_base64_image, mock_document_generator, sample_image_bytes):
        """Test successful file to image conversion."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open", mock_open(read_data=sample_image_bytes)), \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            # Create a fake file
            file_content = sample_text.encode('utf-8')
            files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
            
            response = client.post("/convert-file", files=files)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            assert "attachment" in response.headers["content-disposition"]
    
    def test_convert_file_with_parameters(self, client, sample_text, mock_document_generator, sample_image_bytes):
        """Test file conversion with custom parameters."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.jpg")]
        
        with patch("builtins.open", mock_open(read_data=sample_image_bytes)), \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            file_content = sample_text.encode('utf-8')
            files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
            data = {"image_format": "jpg", "width": 1024, "height": 768}
            
            response = client.post("/convert-file", files=files, data=data)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/jpg"
    
    def test_convert_file_unicode_decode_error(self, client):
        """Test handling of non-text files."""
        # Create a fake binary file that can't be decoded as UTF-8
        binary_content = b'\x80\x81\x82\x83'
        files = {"file": ("test.bin", io.BytesIO(binary_content), "application/octet-stream")}
        
        response = client.post("/convert-file", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "File must be a valid text file" in response.json()["detail"]
    
    def test_convert_file_processing_error(self, client, sample_text, mock_document_generator):
        """Test handling of processing errors during file conversion."""
        mock_document_generator.create_img_from_text.side_effect = Exception("Processing error")
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            
            file_content = sample_text.encode('utf-8')
            files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
            
            response = client.post("/convert-file", files=files)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Error converting file to image: Processing error" in response.json()["detail"]
    
    def test_convert_file_no_file_provided(self, client):
        """Test when no file is provided."""
        response = client.post("/convert-file")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY