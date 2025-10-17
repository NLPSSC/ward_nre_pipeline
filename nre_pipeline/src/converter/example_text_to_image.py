#!/usr/bin/env python3
"""
Example usage of TextToImageConverter with genalog.

First, you need to install genalog:
pip install genalog

Then run this script to see how to convert text documents to images.
"""

from src.nre_pipeline.converter._text_to_img import TextToImageConverter
from src.nre_pipeline.models._document import Document


def example_basic_conversion():
    """Example of basic text-to-image conversion."""

    # Create a sample document
    sample_text = """
    This is a sample medical note for testing purposes.
    
    Patient: John Doe
    Date: 2024-10-10
    
    Chief Complaint: Patient presents with chest pain and shortness of breath.
    
    History of Present Illness: The patient is a 45-year-old male who reports 
    experiencing chest pain that started approximately 2 hours ago. The pain is 
    described as a crushing sensation in the center of his chest, radiating to 
    his left arm. He also reports associated shortness of breath and nausea.
    
    Assessment and Plan:
    1. Rule out myocardial infarction - Order EKG and cardiac enzymes
    2. Monitor vital signs closely
    3. Consider cardiology consultation if indicated
    
    Dr. Smith, MD
    """

    document = Document(note_id="example_note_001", text=sample_text)

    # Initialize converter with default settings
    converter = TextToImageConverter()

    # Convert document to image
    image = converter.convert(document)

    if image:
        # Save the image
        image.save("example_output.png")
        print("Image saved as example_output.png")
        print(f"Image size: {image.size}")
        print(f"Image mode: {image.mode}")
    else:
        print("Failed to convert document to image")


def example_custom_styles():
    """Example with custom styling and degradation."""

    document = Document(
        note_id="custom_test_001",
        text="This is a test document with custom styling applied.",
    )

    # Custom styles - different fonts, sizes, etc.
    custom_styles = {
        "font_family": ["Arial", "Times"],
        "font_size": ["14px", "16px"],
        "text_align": ["center"],
        "language": ["en_US"],
        "hyphenate": [True],
    }

    # Custom degradation effects
    custom_degradations = [
        ("blur", {"radius": 5}),
        ("salt", {"amount": 0.05}),
        ("pepper", {"amount": 0.02}),
    ]

    converter = TextToImageConverter()

    # Convert with custom settings
    image = converter.convert_with_custom_styles(
        document, styles=custom_styles, degradations=custom_degradations
    )

    if image:
        image.save("custom_styled_output.png")
        print("Custom styled image saved as custom_styled_output.png")
    else:
        print("Failed to convert with custom styles")


def example_different_templates():
    """Example using different genalog templates."""

    document = Document(
        note_id="template_test_001", text="Sample text for different template layouts."
    )

    templates = [
        "text_block.html.jinja",  # Simple text block
        "letter.html.jinja",  # Letter-like layout
        "columns.html.jinja",  # Multi-column layout
    ]

    for template in templates:
        try:
            converter = TextToImageConverter(template=template)
            image = converter.convert(document)

            if image:
                filename = f"output_{template.replace('.html.jinja', '')}.png"
                image.save(filename)
                print(f"Created {filename} using {template}")
            else:
                print(f"Failed to create image with {template}")

        except Exception as e:
            print(f"Error with template {template}: {e}")


if __name__ == "__main__":
    print("=== Text to Image Conversion Examples ===\n")

    try:
        print("1. Basic conversion:")
        example_basic_conversion()
        print()

        print("2. Custom styles and degradation:")
        example_custom_styles()
        print()

        print("3. Different templates:")
        example_different_templates()
        print()

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure genalog is installed: pip install genalog")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you're running this from the project root directory.")

    print("=== Examples completed ===")
