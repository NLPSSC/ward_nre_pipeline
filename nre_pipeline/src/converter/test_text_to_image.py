#!/usr/bin/env python3
"""
Test the TextToImageConverter with PIL fallback (since genalog has dependency issues).
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nre_pipeline.converter._text_to_img import TextToImageConverter
from nre_pipeline.models._document import Document


def test_pil_converter():
    """Test the PIL-based text-to-image converter."""

    print("Testing TextToImageConverter with PIL fallback...")

    # Create a sample document
    sample_text = """
MEDICAL RECORD

Patient: John Doe
Date of Birth: 01/15/1980  
Date of Visit: 10/10/2025
Medical Record Number: 12345

CHIEF COMPLAINT:
Patient presents with chest pain and shortness of breath.

HISTORY OF PRESENT ILLNESS:
The patient is a 45-year-old male who reports experiencing chest pain 
that started approximately 2 hours ago. The pain is described as a 
crushing sensation in the center of his chest, radiating to his left arm. 
He also reports associated shortness of breath and nausea.

PHYSICAL EXAMINATION:
Vital Signs: BP 140/90, HR 95, RR 22, Temp 98.6°F
General: Patient appears anxious and diaphoretic
HEENT: Normal
Cardiovascular: Regular rate and rhythm, no murmurs
Respiratory: Clear to auscultation bilaterally
Abdomen: Soft, non-tender

ASSESSMENT AND PLAN:
1. Rule out myocardial infarction
   - Order EKG and cardiac enzymes
   - Monitor on telemetry
2. Chest pain workup
   - Chest X-ray
   - Consider stress test if enzymes negative
3. Continue monitoring vital signs

Dr. Jane Smith, MD
Internal Medicine
"""

    document = Document(note_id="test_001", text=sample_text)

    # Test with default PIL settings
    print("1. Testing with default PIL settings...")
    converter = TextToImageConverter(use_genalog=False)

    image = converter.convert(document)

    if image:
        output_path = "test_medical_note_pil.png"
        image.save(output_path)
        print(f"   ✓ Image saved as {output_path}")
        print(f"   ✓ Image size: {image.size}")
        print(f"   ✓ Image mode: {image.mode}")
    else:
        print("   ✗ Failed to convert document to image")
        return False

    # Test with custom settings
    print("\n2. Testing with custom PIL settings...")
    custom_converter = TextToImageConverter(
        use_genalog=False,
        font_size=14,
        page_width=600,
        page_height=800,
        margin=30,
        line_spacing=1.4,
        text_color="navy",
        background_color="lightgray",
    )

    custom_image = custom_converter.convert(document)

    if custom_image:
        custom_output_path = "test_medical_note_custom.png"
        custom_image.save(custom_output_path)
        print(f"   ✓ Custom image saved as {custom_output_path}")
        print(f"   ✓ Custom image size: {custom_image.size}")
    else:
        print("   ✗ Failed to convert with custom settings")
        return False

    # Test with short text
    print("\n3. Testing with short text...")
    short_doc = Document(
        note_id="short_001", text="This is a short medical note for testing."
    )
    short_image = converter.convert(short_doc)

    if short_image:
        short_output_path = "test_short_note.png"
        short_image.save(short_output_path)
        print(f"   ✓ Short text image saved as {short_output_path}")
    else:
        print("   ✗ Failed to convert short text")
        return False

    print("\n✓ All PIL converter tests passed!")
    return True


def test_genalog_availability():
    """Test if genalog is available and working."""
    print("\nTesting genalog availability...")

    try:
        converter = TextToImageConverter(use_genalog=True)
        print("   ✓ Genalog is available and working")
        return True
    except Exception as e:
        print(f"   ✗ Genalog not available: {e}")
        return False


if __name__ == "__main__":
    print("=== TextToImageConverter Test Suite ===\n")

    try:
        # Test PIL fallback
        pil_success = test_pil_converter()

        # Test genalog availability
        genalog_success = test_genalog_availability()

        print("\n=== Test Results ===")
        print(f"PIL converter: {'✓ PASS' if pil_success else '✗ FAIL'}")
        print(f"Genalog converter: {'✓ PASS' if genalog_success else '✗ FAIL'}")

        if pil_success:
            print("\n✓ TextToImageConverter is working with PIL fallback!")
            print(
                "   You can use it without genalog for basic text-to-image conversion."
            )

        if not genalog_success:
            print("\n⚠ Genalog has dependency conflicts with your Python environment.")
            print(
                "   The converter will use PIL fallback, which provides basic functionality."
            )

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
