# Text to Image Conversion 

This document explains how to convert `document.text` into images within the NRE Pipeline using the `TextToImageConverter` class.

## Overview

The `TextToImageConverter` class provides two conversion methods:
1. **Genalog backend** (advanced): Uses the [genalog](https://github.com/NLPSSC/genalog) library for sophisticated document generation with templates and degradation effects
2. **PIL fallback** (basic): Uses Python's PIL library for simple text-to-image conversion when genalog is unavailable

## Quick Start

```python
from src.nre_pipeline.models._document import Document
from src.nre_pipeline.converter._text_to_img import TextToImageConverter

# Create a document
document = Document(
    note_id="example_001",
    text="Your medical text here..."
)

# Initialize converter (automatically uses best available backend)
converter = TextToImageConverter()

# Convert to image
image = converter.convert(document)

if image:
    image.save("output.png")
```

## Genalog Installation Issues

**Note**: The genalog package has dependency conflicts with modern Python environments due to outdated requirements (numpy==1.18.1, biopython==1.76). If you encounter installation errors, the converter will automatically fall back to PIL-based rendering.

### If you want to try installing genalog:

```bash
# This may fail due to dependency conflicts
pip install genalog
```

### If genalog installation fails:
The converter will work perfectly with the PIL fallback - no additional installation needed!

## PIL Fallback Usage

The PIL fallback provides reliable text-to-image conversion without external dependencies:

```python
# Explicitly use PIL backend
converter = TextToImageConverter(
    use_genalog=False,
    font_size=12,
    page_width=800,
    page_height=1000,
    margin=60,
    line_spacing=1.3,
    text_color="black",
    background_color="white"
)

image = converter.convert(document)
```

### PIL Configuration Options

```python
converter = TextToImageConverter(
    use_genalog=False,           # Force PIL backend
    font_size=14,                # Font size in points
    font_family="arial.ttf",     # Font file (falls back to default if not found)
    page_width=800,              # Image width in pixels
    page_height=1100,            # Image height in pixels
    margin=50,                   # Margin in pixels
    line_spacing=1.2,            # Line spacing multiplier
    text_color="black",          # Text color
    background_color="white"     # Background color
)
```

## Genalog Backend (Advanced)

If genalog is available, you can use advanced features:

### Style Combinations

```python
converter = TextToImageConverter(
    use_genalog=True,
    style_combinations={
        "font_family": ["Times", "Arial", "Helvetica"],
        "font_size": ["10px", "12px", "14px"],
        "text_align": ["left", "center", "justify"],
        "language": ["en_US"],
        "hyphenate": [True, False],
    }
)
```

### Degradation Effects

```python
converter = TextToImageConverter(
    use_genalog=True,
    degradations=[
        ("blur", {"radius": 3}),
        ("bleed_through", {"alpha": 0.8}),
        ("morphology", {
            "operation": "open", 
            "kernel_shape": (3, 3), 
            "kernel_type": "ones"
        }),
        ("salt", {"amount": 0.05}),
        ("pepper", {"amount": 0.02}),
    ]
)
```

### Templates

```python
converter = TextToImageConverter(
    use_genalog=True,
    template="letter.html.jinja"  # or "columns.html.jinja", "text_block.html.jinja"
)
```

## Examples

### Basic Medical Note Conversion

```python
medical_text = """
PATIENT: John Smith
DOB: 03/15/1975
DATE: October 10, 2025

CHIEF COMPLAINT:
Patient reports persistent cough and fatigue.

ASSESSMENT:
Possible viral upper respiratory infection

PLAN:
1. Symptomatic treatment
2. Follow-up in 1 week
"""

document = Document(note_id="note_001", text=medical_text)
converter = TextToImageConverter()
image = converter.convert(document)
image.save("medical_note.png")
```

### Custom Styling Example

```python
# Alert-style document with custom colors
converter = TextToImageConverter(
    use_genalog=False,
    font_size=14,
    page_width=600,
    page_height=400,
    text_color="darkred",
    background_color="lightyellow"
)

alert_text = "URGENT: Patient requires immediate attention."
alert_doc = Document(note_id="alert_001", text=alert_text)
alert_image = converter.convert(alert_doc)
alert_image.save("urgent_alert.png")
```

### Integration with NRE Pipeline

```python
from src.nre_pipeline.processor._base import Processor

class TextToImageProcessor(Processor):
    def __init__(self, processor_id: int, user_interrupt=None):
        super().__init__(processor_id, user_interrupt)
        self.converter = TextToImageConverter(
            font_size=12,
            page_width=800,
            page_height=1100
        )
    
    def _call(self, document_batch):
        for document in document_batch.documents:
            if self.user_interrupted():
                break
                
            image = self.converter.convert(document)
            if image:
                output_path = f"images/{document.note_id}.png"
                image.save(output_path)
                
            yield NLPResult(
                document=document,
                annotations=[],
                metadata={"image_generated": image is not None}
            )
```

## Testing

Run the included examples to test the converter:

```bash
# Test the converter with PIL fallback
python test_text_to_image.py

# Run simple example
python simple_text_to_image_example.py
```

## Output Formats

The converter returns PIL Image objects that can be saved in various formats:

```python
image = converter.convert(document)

# Save in different formats
image.save("output.png")        # PNG (default)
image.save("output.jpg")        # JPEG
image.save("output.tiff")       # TIFF
image.save("output.bmp")        # BMP

# Convert to different modes
grayscale = image.convert('L')   # Convert to grayscale
grayscale.save("output_gray.png")
```

## Comparison: PIL vs Genalog

| Feature | PIL Fallback | Genalog |
|---------|-------------|---------|
| Installation | ✓ No extra deps | ✗ Dependency conflicts |
| Basic text rendering | ✓ Yes | ✓ Yes |
| Custom fonts | ✓ Limited | ✓ Full support |
| Text layouts | ✗ Simple only | ✓ HTML templates |
| Degradation effects | ✗ No | ✓ Advanced |
| Document templates | ✗ No | ✓ Multiple layouts |
| Reliability | ✓ High | ⚠ Dependency issues |

## Troubleshooting

### Common Issues

1. **Font not found**: PIL fallback uses system default font if specified font isn't available
2. **Text too long**: PIL fallback truncates text that doesn't fit on the page
3. **Genalog import errors**: Converter automatically falls back to PIL

### Performance Tips

- Use appropriate image sizes (smaller = faster)
- For batch processing, reuse converter instances
- PIL fallback is faster than genalog for simple text

## Summary

The `TextToImageConverter` provides a robust solution for converting document text to images:

- **Works out of the box** with PIL fallback (no external dependencies)
- **Gracefully handles** genalog installation issues
- **Suitable for** basic text-to-image conversion needs in your NRE pipeline
- **Extensible** with genalog features if available

The PIL fallback ensures your pipeline remains functional even when genalog's complex dependencies can't be installed.