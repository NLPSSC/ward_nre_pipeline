"""
Unit tests for the Pydantic models used in the Genalog API.
"""

import pytest
from pydantic import ValidationError
from src.genalog_api.api.main import TextToImageRequest, TextToImageResponse


class TestTextToImageRequest:
    """Test the TextToImageRequest model."""
    
    def test_minimal_request(self):
        """Test creating a request with only required fields."""
        request = TextToImageRequest(text="Hello, World!")
        
        assert request.text == "Hello, World!"
        assert request.image_format == "png"  # Default value
        assert request.width == 800  # Default value
        assert request.height == 600  # Default value
        assert request.font_size == 12  # Default value
        assert request.font_family == "Arial"  # Default value
    
    def test_full_request(self):
        """Test creating a request with all fields specified."""
        request = TextToImageRequest(
            text="Test document content",
            image_format="jpg",
            width=1024,
            height=768,
            font_size=14,
            font_family="Times New Roman"
        )
        
        assert request.text == "Test document content"
        assert request.image_format == "jpg"
        assert request.width == 1024
        assert request.height == 768
        assert request.font_size == 14
        assert request.font_family == "Times New Roman"
    
    def test_empty_text_validation(self):
        """Test that empty text is allowed."""
        request = TextToImageRequest(text="")
        assert request.text == ""
    
    def test_missing_text_validation(self):
        """Test that missing text field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            TextToImageRequest()
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("text",)
    
    def test_none_optional_fields(self):
        """Test that None values for optional fields use defaults."""
        request = TextToImageRequest(
            text="Test",
            image_format=None,
            width=None,
            height=None,
            font_size=None,
            font_family=None
        )
        
        assert request.image_format == "png"
        assert request.width == 800
        assert request.height == 600
        assert request.font_size == 12
        assert request.font_family == "Arial"
    
    def test_custom_values(self):
        """Test with various custom values."""
        request = TextToImageRequest(
            text="Custom text",
            image_format="webp",
            width=1920,
            height=1080,
            font_size=16,
            font_family="Helvetica"
        )
        
        assert request.text == "Custom text"
        assert request.image_format == "webp"
        assert request.width == 1920
        assert request.height == 1080
        assert request.font_size == 16
        assert request.font_family == "Helvetica"


class TestTextToImageResponse:
    """Test the TextToImageResponse model."""
    
    def test_valid_response(self):
        """Test creating a valid response."""
        response = TextToImageResponse(
            image_base64="SGVsbG8gV29ybGQ=",  # "Hello World" in base64
            image_format="png",
            message="Success"
        )
        
        assert response.image_base64 == "SGVsbG8gV29ybGQ="
        assert response.image_format == "png"
        assert response.message == "Success"
    
    def test_empty_base64(self):
        """Test with empty base64 string."""
        response = TextToImageResponse(
            image_base64="",
            image_format="jpg",
            message="Empty image"
        )
        
        assert response.image_base64 == ""
        assert response.image_format == "jpg"
        assert response.message == "Empty image"
    
    def test_missing_fields_validation(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            TextToImageResponse()
        
        errors = exc_info.value.errors()
        assert len(errors) == 3  # All three fields are required
        
        error_fields = {error["loc"][0] for error in errors}
        assert error_fields == {"image_base64", "image_format", "message"}
    
    def test_long_base64_string(self):
        """Test with a long base64 string."""
        long_base64 = "SGVsbG8gV29ybGQ=" * 1000  # Repeat pattern
        response = TextToImageResponse(
            image_base64=long_base64,
            image_format="png",
            message="Large image"
        )
        
        assert response.image_base64 == long_base64
        assert response.image_format == "png"
        assert response.message == "Large image"
    
    def test_special_characters_in_message(self):
        """Test with special characters in message."""
        response = TextToImageResponse(
            image_base64="dGVzdA==",
            image_format="gif",
            message="Success! Conversion completed with special chars: àáâãäå"
        )
        
        assert response.message == "Success! Conversion completed with special chars: àáâãäå"
    
    def test_different_image_formats(self):
        """Test with different image formats."""
        formats = ["png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff"]
        
        for fmt in formats:
            response = TextToImageResponse(
                image_base64="dGVzdA==",
                image_format=fmt,
                message=f"Image in {fmt} format"
            )
            assert response.image_format == fmt
            assert fmt in response.message