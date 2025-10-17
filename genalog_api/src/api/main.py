"""
RESTful API for converting text documents to images using Genalog.
"""

import base64
import tempfile
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
from genalog.generation.document import DocumentGenerator
from pydantic import BaseModel


# Pydantic models
class TextToImageRequest(BaseModel):
    text: str
    image_format: Optional[str] = "png"
    width: Optional[int] = 800
    height: Optional[int] = 600
    font_size: Optional[int] = 12
    font_family: Optional[str] = "Arial"


class TextToImageResponse(BaseModel):
    image_base64: str
    image_format: str
    message: str


# FastAPI app
app = FastAPI(
    title="Genalog Text-to-Image API",
    description="RESTful API for converting text documents to images using Genalog",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Genalog Text-to-Image API",
        "version": "1.0.0",
        "endpoints": {
            "convert_text": "/convert-text",
            "convert_file": "/convert-file",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "genalog-api"}


@app.post("/convert-text", response_model=TextToImageResponse)
async def convert_text_to_image(request: TextToImageRequest):
    """
    Convert text to image using Genalog.

    Args:
        request: TextToImageRequest containing text and formatting options

    Returns:
        TextToImageResponse with base64 encoded image
    """
    try:
        # Initialize document generator
        doc_generator = DocumentGenerator()

        # Create temporary file for text
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file.write(request.text)
            temp_path = Path(temp_file.name)

        try:
            # Generate document image
            # Configure document generation parameters
            doc_generator.template_list = ["text_block.html.jinja"]

            # Generate the document
            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = Path(temp_dir)

                # Generate document from text
                docs = doc_generator.create_img_from_text(
                    text=request.text,
                    output_folder=output_dir,
                    target_image_width=request.width,
                    target_image_height=request.height,
                )

                if not docs:
                    raise HTTPException(
                        status_code=500, detail="Failed to generate image from text"
                    )

                # Get the first generated document
                doc_path = docs[0]

                # Read the generated image
                with open(doc_path, "rb") as img_file:
                    img_data = img_file.read()

                # Convert to base64
                img_base64 = base64.b64encode(img_data).decode("utf-8")

                return TextToImageResponse(
                    image_base64=img_base64,
                    image_format=request.image_format or "png",
                    message="Text successfully converted to image",
                )

        finally:
            # Clean up temporary text file
            if temp_path.exists():
                temp_path.unlink()

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error converting text to image: {str(e)}"
        )


@app.post("/convert-file")
async def convert_file_to_image(
    file: UploadFile = File(...),
    image_format: Optional[str] = "png",
    width: Optional[int] = 800,
    height: Optional[int] = 600,
):
    """
    Convert uploaded text file to image using Genalog.

    Args:
        file: Uploaded text file
        image_format: Output image format (png, jpg, etc.)
        width: Target image width
        height: Target image height

    Returns:
        Response with image data
    """
    try:
        # Read file content
        content = await file.read()
        text = content.decode("utf-8")

        # Create request object
        request = TextToImageRequest(
            text=text, image_format=image_format, width=width, height=height
        )

        # Convert to image
        result = await convert_text_to_image(request)

        # Decode base64 image
        img_data = base64.b64decode(result.image_base64)

        # Return image as response
        return Response(
            content=img_data,
            media_type=f"image/{image_format}",
            headers={
                "Content-Disposition": f"attachment; filename=converted_image.{image_format}"
            },
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be a valid text file")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error converting file to image: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
