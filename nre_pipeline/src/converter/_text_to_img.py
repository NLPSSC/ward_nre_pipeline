import os
import tempfile
from typing import Any, Dict, List, Optional

from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont
from PIL.Image import Image

from nre_pipeline.models._document import Document

# Try to import genalog, but provide fallback if not available
try:
    from genalog.pipeline import AnalogDocumentGeneration

    GENALOG_AVAILABLE = True
except ImportError:
    GENALOG_AVAILABLE = False
    AnalogDocumentGeneration = None


class TextToImageConverter:
    """
    A class that converts text documents to image format.

    Uses genalog if available, otherwise falls back to PIL-based text rendering.
    """

    def __init__(self, **config):
        self._num_processor_workers = config.get("num_processor_workers", 1)
        self._use_genalog = config.get("use_genalog", True) and GENALOG_AVAILABLE

        if self._use_genalog:
            self._init_genalog_converter(config)
        else:
            self._init_pil_converter(config)

    def _init_genalog_converter(self, config):
        """Initialize genalog-based converter."""
        # Default style configurations
        self._style_combinations = config.get(
            "style_combinations",
            {
                "font_family": ["Times"],
                "font_size": ["12px"],
                "text_align": ["left"],
                "language": ["en_US"],
                "hyphenate": [False],
            },
        )

        # Default degradation effects
        self._degradations = config.get(
            "degradations",
            [
                ("blur", {"radius": 3}),
                ("bleed_through", {"alpha": 0.8}),
                (
                    "morphology",
                    {
                        "operation": "open",
                        "kernel_shape": (3, 3),
                        "kernel_type": "ones",
                    },
                ),
            ],
        )

        # HTML template to use
        self._template = config.get("template", "text_block.html.jinja")

        # Image resolution
        self._resolution = config.get("resolution", 300)

        # Initialize the genalog document generator
        self._doc_generator = AnalogDocumentGeneration(
            styles=self._style_combinations,
            degradations=self._degradations,
            resolution=self._resolution,
        )

    def _init_pil_converter(self, config):
        """Initialize PIL-based converter as fallback."""
        self._font_size = config.get("font_size", 12)
        self._font_family = config.get("font_family", "arial.ttf")
        self._line_spacing = config.get("line_spacing", 1.2)
        self._margin = config.get("margin", 50)
        self._page_width = config.get("page_width", 800)
        self._page_height = config.get("page_height", 1100)
        self._text_color = config.get("text_color", "black")
        self._background_color = config.get("background_color", "white")

        # Try to load font
        try:
            self._font = ImageFont.truetype(self._font_family, self._font_size)
        except (IOError, OSError):
            # Fallback to default font
            try:
                self._font = ImageFont.load_default()
            except Exception:
                self._font = None

    def convert(self, document: Document) -> Optional[Image]:
        """
        Convert a text document to an image.

        Args:
            document: The text document to convert

        Returns:
            PIL.Image: The converted image, or None if conversion fails
        """
        if self._use_genalog:
            return self._convert_with_genalog(document)
        else:
            return self._convert_with_pil(document)

    def _convert_with_genalog(self, document: Document) -> Optional[Image]:
        """Convert using genalog."""
        try:
            if not document.text or not document.text.strip():
                return None

            # Create a temporary file with the document text
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as temp_file:
                temp_file.write(document.text)
                temp_file_path = temp_file.name

            try:
                # Generate image using genalog
                img_array = self._doc_generator.generate_img(
                    temp_file_path,
                    self._template,
                    target_folder=None,  # Return as numpy array
                )

                if img_array is None:
                    return None

                # Convert numpy array to PIL Image
                # genalog returns grayscale images as numpy arrays
                if len(img_array.shape) == 2:  # Grayscale
                    pil_image = PILImage.fromarray(img_array, mode="L")
                else:  # RGB or other formats
                    pil_image = PILImage.fromarray(img_array)

                return pil_image

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            print(f"Error converting text to image with genalog: {e}")
            return None

    def _convert_with_pil(self, document: Document) -> Optional[Image]:
        """Convert using PIL as fallback."""
        try:
            if not document.text or not document.text.strip():
                return None

            # Create image
            image = PILImage.new(
                "RGB", (self._page_width, self._page_height), self._background_color
            )
            draw = ImageDraw.Draw(image)

            # Prepare text
            text = document.text.strip()

            if not self._font:
                # If no font available, create a simple text image
                draw.text(
                    (self._margin, self._margin),
                    "Text rendering unavailable",
                    fill=self._text_color,
                )
                return image

            # Word wrap text
            wrapped_lines = self._wrap_text(
                text, draw, self._page_width - 2 * self._margin
            )

            # Draw text line by line
            y = self._margin
            line_height = int(self._font_size * self._line_spacing)

            for line in wrapped_lines:
                if y + line_height > self._page_height - self._margin:
                    break  # Stop if we run out of space

                draw.text(
                    (self._margin, y), line, font=self._font, fill=self._text_color
                )
                y += line_height

            return image

        except Exception as e:
            print(f"Error converting text to image with PIL: {e}")
            return None

    def _wrap_text(self, text: str, draw, max_width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        if not self._font:
            return [text]

        lines = []
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            if not paragraph.strip():
                lines.append("")
                continue

            words = paragraph.split()
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])

                # Get text bounding box
                bbox = draw.textbbox((0, 0), test_line, font=self._font)
                text_width = bbox[2] - bbox[0]

                if text_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                    else:
                        # Single word is too long, just add it
                        lines.append(word)

            if current_line:
                lines.append(" ".join(current_line))

        return lines

    def convert_with_custom_styles(
        self,
        document: Document,
        styles: Optional[Dict[str, Any]] = None,
        degradations: Optional[List[Any]] = None,
    ) -> Optional[Image]:
        """
        Convert a text document to an image with custom styles and degradations.
        Only works with genalog backend.

        Args:
            document: The text document to convert
            styles: Custom style combinations dictionary
            degradations: Custom degradation effects list

        Returns:
            PIL.Image: The converted image, or None if conversion fails
        """
        if not self._use_genalog:
            print("Custom styles only available with genalog backend")
            return self.convert(document)

        if styles or degradations:
            # Create a temporary generator with custom settings
            temp_generator = AnalogDocumentGeneration(
                styles=styles or self._style_combinations,
                degradations=degradations or self._degradations,
                resolution=self._resolution,
            )

            try:
                if not document.text or not document.text.strip():
                    return None

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False, encoding="utf-8"
                ) as temp_file:
                    temp_file.write(document.text)
                    temp_file_path = temp_file.name

                try:
                    img_array = temp_generator.generate_img(
                        temp_file_path, self._template, target_folder=None
                    )

                    if img_array is None:
                        return None

                    if len(img_array.shape) == 2:
                        pil_image = PILImage.fromarray(img_array, mode="L")
                    else:
                        pil_image = PILImage.fromarray(img_array)

                    return pil_image

                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            except Exception as e:
                print(f"Error converting text to image with custom styles: {e}")
                return None
        else:
            return self.convert(document)
