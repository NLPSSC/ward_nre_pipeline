"""
Test configuration and fixtures for Genalog API tests.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.genalog_api.api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "This is a test document with some sample text for conversion to image."


@pytest.fixture
def mock_document_generator():
    """Mock DocumentGenerator for testing."""
    with patch("src.genalog_api.api.main.DocumentGenerator") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_image_bytes():
    """Sample image bytes for testing."""
    # Create a minimal PNG-like byte sequence for testing
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"


@pytest.fixture
def sample_base64_image():
    """Sample base64 encoded image for testing."""
    import base64

    sample_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    return base64.b64encode(sample_bytes).decode("utf-8")
