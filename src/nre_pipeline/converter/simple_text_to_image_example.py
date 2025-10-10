#!/usr/bin/env python3
"""
Simple example showing how to use TextToImageConverter without genalog.

This uses the PIL fallback which provides basic text-to-image conversion
without requiring genalog's complex dependencies.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nre_pipeline.converter._text_to_img import TextToImageConverter
from nre_pipeline.models._document import Document


def main():
    print("=== Simple Text to Image Example ===\n")

    # Sample medical text
    medical_text = """
PATIENT: John Smith
DOB: 03/15/1975
MRN: 456789
DATE: October 10, 2025

CHIEF COMPLAINT:
Patient reports persistent cough and fatigue for the past week.

HISTORY:
45-year-old male presents with dry cough, low-grade fever, and 
general malaise. Symptoms began 7 days ago. No recent travel 
or known exposures.

VITAL SIGNS:
Temperature: 100.2°F
Blood Pressure: 128/82
Heart Rate: 88 bpm
Respiratory Rate: 18
Oxygen Saturation: 96% on room air

ASSESSMENT:
Possible viral upper respiratory infection

PLAN:
1. Symptomatic treatment with rest and fluids
2. Return if symptoms worsen or persist >10 days
3. Follow-up in 1 week

Dr. Emily Johnson, MD
Family Medicine
    """

    # Create document
    document = Document(note_id="example_001", text=medical_text)

    # Initialize converter (will use PIL fallback since genalog has dependency issues)
    converter = TextToImageConverter(
        use_genalog=False,  # Explicitly use PIL fallback
        font_size=12,
        page_width=800,
        page_height=1000,
        margin=60,
        line_spacing=1.3,
        text_color="black",
        background_color="white",
    )

    print("Converting text to image...")

    # Convert to image
    image = converter.convert(document)

    if image:
        output_file = "medical_note_example.png"
        image.save(output_file)
        print(f"✓ Success! Image saved as: {output_file}")
        print(f"  Image size: {image.size[0]}x{image.size[1]} pixels")
        print(f"  Color mode: {image.mode}")

        # You can now use this image for:
        print("\nYou can now:")
        print("  • Use the image for OCR testing")
        print("  • Include it in document processing pipelines")
        print("  • Apply additional image processing")
        print("  • Save in different formats (JPEG, TIFF, etc.)")

    else:
        print("✗ Failed to convert text to image")
        return

    # Example of custom styling
    print("\n=== Custom Styling Example ===")

    custom_converter = TextToImageConverter(
        use_genalog=False,
        font_size=10,
        page_width=600,
        page_height=400,
        margin=20,
        line_spacing=1.1,
        text_color="darkblue",
        background_color="lightcyan",
    )

    short_text = """
URGENT ALERT: Patient requires immediate attention.
Blood pressure: 180/120 mmHg
Recommend immediate evaluation.
    """

    alert_doc = Document(note_id="alert_001", text=short_text)
    alert_image = custom_converter.convert(alert_doc)

    if alert_image:
        alert_file = "alert_example.png"
        alert_image.save(alert_file)
        print(f"✓ Alert image saved as: {alert_file}")

    print("\n=== Summary ===")
    print("The TextToImageConverter provides a working solution for converting")
    print("document text to images without requiring genalog's complex dependencies.")
    print("While not as feature-rich as genalog, it handles basic text-to-image")
    print("conversion needs for your NRE pipeline.")


if __name__ == "__main__":
    main()
