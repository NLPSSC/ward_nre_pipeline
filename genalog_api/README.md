# Genalog Text-to-Image API

A RESTful API service that converts text documents to images using the Genalog library. This API is designed for generating synthetic document images from text content, which can be useful for document processing, OCR training, and data augmentation tasks.

## Features

- 🔄 Convert plain text to document images
- 📄 Upload text files for conversion
- 🎨 Customizable image dimensions and formatting
- 🚀 Fast API with automatic documentation
- 🛡️ Error handling and validation
- 📊 Health check endpoints

## Environment Setup

### Using Conda (Recommended)

```shell
cd Z:\_\active\nlpssc\project_ward_non-routine_events\nre_pipeline

mamba create -p .\envs\genalog_api_env -f .\src\genalog_api\environment.yml
mamba activate .\envs\genalog_api_env
```

### Using pip

```shell
pip install -r requirements.txt
```

## Quick Start

1. **Start the API server:**
   ```shell
   python __main__.py
   ```
   
   Or use the batch script (Windows):
   ```shell
   start_api.bat
   ```

2. **Access the API:**
   - API Base URL: `http://localhost:8000`
   - Interactive Documentation: `http://localhost:8000/docs`
   - Alternative Documentation: `http://localhost:8000/redoc`

3. **Test the API:**
   ```shell
   python test_client.py
   ```

## API Endpoints

### GET `/`
Root endpoint providing API information and available endpoints.

### GET `/health`
Health check endpoint for monitoring service status.

### POST `/convert-text`
Convert text content directly to an image.

**Request Body:**
```json
{
  "text": "Your text content here",
  "image_format": "png",
  "width": 800,
  "height": 600,
  "font_size": 12,
  "font_family": "Arial"
}
```

**Response:**
```json
{
  "image_base64": "base64-encoded-image-data",
  "image_format": "png",
  "message": "Text successfully converted to image"
}
```

### POST `/convert-file`
Upload a text file and convert it to an image.

**Parameters:**
- `file`: Text file to upload
- `image_format`: Output format (png, jpg, etc.)
- `width`: Target image width
- `height`: Target image height

**Response:** Binary image data

## Usage Examples

### Python Client Example

```python
import requests
import base64

# Convert text to image
url = "http://localhost:8000/convert-text"
payload = {
    "text": "Hello, World!",
    "image_format": "png",
    "width": 800,
    "height": 600
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    result = response.json()
    image_data = base64.b64decode(result["image_base64"])
    
    with open("output.png", "wb") as f:
        f.write(image_data)
```

### cURL Examples

**Convert text:**
```bash
curl -X POST "http://localhost:8000/convert-text" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Sample text for conversion",
       "image_format": "png",
       "width": 800,
       "height": 600
     }'
```

**Upload file:**
```bash
curl -X POST "http://localhost:8000/convert-file" \
     -F "file=@sample.txt" \
     -F "image_format=png" \
     -F "width=800" \
     -F "height=600" \
     --output converted_image.png
```

## Configuration Options

### Text-to-Image Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | required | Text content to convert |
| `image_format` | string | "png" | Output image format |
| `width` | integer | 800 | Target image width in pixels |
| `height` | integer | 600 | Target image height in pixels |
| `font_size` | integer | 12 | Font size for text rendering |
| `font_family` | string | "Arial" | Font family for text rendering |

## Development

### Project Structure

```
genalog_api/
├── api/
│   ├── __init__.py
│   └── main.py          # Main FastAPI application
├── __main__.py          # Entry point
├── environment.yml      # Conda environment
├── requirements.txt     # Python dependencies
├── start_api.bat       # Windows startup script
├── test_client.py      # Test client examples
└── README.md           # This file
```

### Running in Development Mode

The API runs with auto-reload enabled by default, so changes to the code will automatically restart the server.

### Testing

Run the test client to verify all endpoints:

```shell
python test_client.py
```

This will test:
- Health check endpoint
- Text-to-image conversion
- File upload functionality

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Genalog**: Microsoft's synthetic document generation library
- **Pillow**: Python Imaging Library for image processing
- **Pydantic**: Data validation using Python type annotations

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input data or file format
- **500 Internal Server Error**: Issues with text-to-image conversion
- **422 Unprocessable Entity**: Validation errors

## Limitations

- Text files must be UTF-8 encoded
- Maximum recommended text length: ~10,000 characters
- Supported image formats: PNG, JPEG, etc. (depends on Pillow support)
- Font family options are limited to system-available fonts

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation as needed
4. Ensure all lint checks pass

## License

This project follows the same license as the parent NRE Pipeline project.# Updated devcontainer configuration
