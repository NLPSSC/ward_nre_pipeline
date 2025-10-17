"""
Performance and load testing for the Genalog API.
"""

import time
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestPerformance:
    """Test performance-related scenarios."""
    
    def test_response_time_convert_text(self, client, sample_text, mock_document_generator, sample_image_bytes):
        """Test response time for text conversion."""
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
            
            start_time = time.time()
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds (mocked scenario)
    
    def test_multiple_rapid_requests(self, client, sample_text, mock_document_generator, sample_image_bytes):
        """Test handling multiple rapid requests."""
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
            
            # Send 10 requests in rapid succession
            responses = []
            start_time = time.time()
            
            for i in range(10):
                request_data = {"text": f"{sample_text} - Request {i}"}
                response = client.post("/convert-text", json=request_data)
                responses.append(response)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
            
            # Should handle all requests reasonably quickly (mocked)
            assert total_time < 10.0
    
    def test_memory_usage_simulation(self, client, mock_document_generator, sample_image_bytes):
        """Simulate memory usage patterns with varying text sizes."""
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
            
            # Test with progressively larger text inputs
            text_sizes = [100, 1000, 5000, 10000]  # Characters
            
            for size in text_sizes:
                large_text = "A" * size
                request_data = {"text": large_text}
                
                response = client.post("/convert-text", json=request_data)
                assert response.status_code == 200
                
                # Verify response contains expected data
                data = response.json()
                assert "image_base64" in data
                assert len(data["image_base64"]) > 0
    
    def test_concurrent_different_formats(self, client, sample_text, mock_document_generator, sample_image_bytes):
        """Test concurrent requests with different image formats."""
        formats = ["png", "jpg", "gif", "webp"]
        responses = []
        
        for fmt in formats:
            mock_document_generator.create_img_from_text.return_value = [Path(f"/fake/path/image.{fmt}")]
            
            with patch("builtins.open") as mock_open, \
                 patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
                 patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
                 patch("pathlib.Path.exists", return_value=True), \
                 patch("pathlib.Path.unlink"):
                
                mock_open.return_value.__enter__.return_value.read.return_value = sample_image_bytes
                mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
                mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
                mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
                
                request_data = {
                    "text": sample_text,
                    "image_format": fmt
                }
                
                response = client.post("/convert-text", json=request_data)
                responses.append((fmt, response))
        
        # All formats should be processed successfully
        for fmt, response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["image_format"] == fmt


class TestResourceManagement:
    """Test resource management and cleanup."""
    
    def test_temporary_file_cleanup(self, client, sample_text, mock_document_generator, sample_image_bytes):
        """Test that temporary files are properly cleaned up."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        with patch("builtins.open") as mock_open, \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink") as mock_unlink:
            
            mock_open.return_value.__enter__.return_value.read.return_value = sample_image_bytes
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == 200
            
            # Verify cleanup was called
            mock_unlink.assert_called()
    
    def test_cleanup_on_exception(self, client, sample_text, mock_document_generator):
        """Test that cleanup occurs even when exceptions happen."""
        mock_document_generator.create_img_from_text.side_effect = Exception("Processing failed")
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink") as mock_unlink:
            
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            
            request_data = {"text": sample_text}
            response = client.post("/convert-text", json=request_data)
            
            assert response.status_code == 500
            
            # Verify cleanup was still called despite the exception
            mock_unlink.assert_called()
    
    def test_resource_limits_simulation(self, client, mock_document_generator, sample_image_bytes):
        """Simulate resource limit scenarios."""
        mock_document_generator.create_img_from_text.return_value = [Path("/fake/path/image.png")]
        
        # Simulate creating many large images
        with patch("builtins.open") as mock_open, \
             patch("tempfile.NamedTemporaryFile") as mock_temp_file, \
             patch("tempfile.TemporaryDirectory") as mock_temp_dir, \
             patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.unlink"):
            
            # Simulate larger image data
            large_image_data = sample_image_bytes * 1000  # Make it larger
            mock_open.return_value.__enter__.return_value.read.return_value = large_image_data
            mock_temp_file.return_value.__enter__.return_value.name = "/fake/temp/file.txt"
            mock_temp_file.return_value.__enter__.return_value.write = MagicMock()
            mock_temp_dir.return_value.__enter__.return_value = "/fake/temp/dir"
            
            # Process multiple large requests
            for i in range(5):
                large_text = "Large document content " * 1000
                request_data = {
                    "text": large_text,
                    "width": 2048,
                    "height": 2048
                }
                
                response = client.post("/convert-text", json=request_data)
                assert response.status_code == 200
                
                # Verify response contains valid data
                data = response.json()
                assert "image_base64" in data
                assert len(data["image_base64"]) > 0