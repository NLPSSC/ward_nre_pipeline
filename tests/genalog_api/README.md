# Genalog API Tests

This directory contains comprehensive unit tests for the Genalog Text-to-Image API.

## Test Files

### `conftest.py`
Contains test configuration, fixtures, and common setup used across all test files:
- `client`: FastAPI test client fixture
- `sample_text`: Sample text for testing
- `mock_document_generator`: Mocked DocumentGenerator for testing
- `sample_image_bytes`: Sample image bytes for testing
- `sample_base64_image`: Base64 encoded sample image

### `test_main.py`
Tests for the main API endpoints:

#### TestRootEndpoint
- Tests the root endpoint (`/`) returns correct API information

#### TestHealthEndpoint
- Tests the health check endpoint (`/health`)

#### TestConvertTextEndpoint
- Tests text-to-image conversion (`/convert-text`)
- Success scenarios with various parameters
- Error handling (no documents generated, exceptions)
- Invalid request validation
- Custom parameters testing

#### TestConvertFileEndpoint
- Tests file upload and conversion (`/convert-file`)
- Success scenarios with different file types
- Unicode decode error handling
- Processing error handling
- Missing file validation

### `test_models.py`
Tests for Pydantic models:

#### TestTextToImageRequest
- Tests `TextToImageRequest` model validation
- Default values testing
- Required field validation
- Custom parameter validation

#### TestTextToImageResponse
- Tests `TextToImageResponse` model validation
- Required field validation
- Various data type testing

### `test_integration.py`
Integration tests that test complete workflows:

#### TestAPIIntegration
- Full text-to-image workflow testing
- File upload workflow testing
- Error handling across multiple endpoints
- Concurrent request simulation
- Different image format workflows

### `test_error_handling.py`
Comprehensive error handling and edge case testing:

#### TestErrorHandling
- DocumentGenerator import errors
- File I/O errors
- Temporary file/directory creation errors
- Base64 encoding errors

#### TestEdgeCases
- Very long text inputs
- Empty text inputs
- Special characters and Unicode
- Extreme image dimensions
- Large file uploads
- Invalid UTF-8 sequences

### `test_performance.py`
Performance and resource management testing:

#### TestPerformance
- Response time testing
- Multiple rapid requests handling
- Memory usage simulation
- Concurrent requests with different formats

#### TestResourceManagement
- Temporary file cleanup verification
- Cleanup on exception scenarios
- Resource limit simulations

## Running the Tests

### Prerequisites
```bash
pip install pytest fastapi httpx
```

### Run All Tests
```bash
pytest tests/genalog_api/
```

### Run Specific Test File
```bash
pytest tests/genalog_api/test_main.py
```

### Run Tests with Coverage
```bash
pytest tests/genalog_api/ --cov=src.genalog_api
```

### Run Tests with Verbose Output
```bash
pytest tests/genalog_api/ -v
```

## Test Coverage

The tests cover:

1. **API Endpoints**: All HTTP endpoints with various scenarios
2. **Data Models**: Pydantic model validation and edge cases
3. **Error Handling**: Exception scenarios and error responses
4. **Integration**: End-to-end workflows
5. **Performance**: Load testing and resource management
6. **Edge Cases**: Boundary conditions and unusual inputs

## Mocking Strategy

The tests use extensive mocking to:
- Isolate the API logic from external dependencies
- Control the behavior of the Genalog DocumentGenerator
- Simulate file system operations
- Test error conditions reliably

Key mocked components:
- `DocumentGenerator` from genalog
- File operations (`open`, `tempfile`)
- Path operations
- Base64 encoding/decoding

## Test Data

Tests use consistent test data:
- Sample text: "This is a test document with some sample text for conversion to image."
- Sample image bytes: Minimal PNG header for testing
- Various text sizes and formats for edge case testing

## Continuous Integration

These tests are designed to run in CI/CD environments and provide:
- Fast execution through mocking
- Reliable results without external dependencies
- Comprehensive coverage reporting
- Clear error messages for debugging