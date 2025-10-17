"""
Example client for testing the Genalog Text-to-Image API.
"""

import base64
from pathlib import Path

import requests


def test_text_to_image_api():
    """Test the text-to-image API endpoint."""

    # API endpoint
    url = "http://localhost:8000/convert-text"

    # Sample text
    sample_text = """
    This is a sample medical note for testing the text-to-image conversion API.
    
    Patient: John Doe
    Date: 2025-10-17
    
    Chief Complaint: Patient reports feeling unwell for the past 3 days.
    
    History of Present Illness:
    The patient is a 45-year-old male who presents with a 3-day history of 
    fever, fatigue, and mild headache. No nausea or vomiting reported.
    
    Physical Examination:
    - Temperature: 101.2°F
    - Blood Pressure: 120/80 mmHg
    - Heart Rate: 88 bpm
    - Respiratory Rate: 16/min
    
    Assessment and Plan:
    1. Viral syndrome - supportive care
    2. Follow up in 1 week if symptoms persist
    3. Return immediately if symptoms worsen
    """

    # Request payload
    payload = {
        "text": sample_text,
        "image_format": "png",
        "width": 800,
        "height": 600,
        "font_size": 12,
        "font_family": "Arial",
    }

    try:
        # Make the API request
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()

            # Save the image
            image_data = base64.b64decode(result["image_base64"])
            output_path = Path("test_output.png")

            with open(output_path, "wb") as f:
                f.write(image_data)

            print(f"✅ Success! Image saved to: {output_path}")
            print(f"📝 Message: {result['message']}")
            print(f"🖼️  Format: {result['image_format']}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Error: Could not connect to API. Make sure the server is running on http://localhost:8000"
        )
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_file_upload_api():
    """Test the file upload API endpoint."""

    # Create a test file
    test_file_path = Path("test_input.txt")
    sample_text = """Sample medical document for file upload test.

This demonstrates the file upload capability of the API."""

    with open(test_file_path, "w") as f:
        f.write(sample_text)

    try:
        # API endpoint
        url = "http://localhost:8000/convert-file"

        # Upload file
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_input.txt", f, "text/plain")}
            data = {"image_format": "png", "width": 800, "height": 600}
            response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            # Save the returned image
            output_path = Path("test_file_output.png")
            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"✅ File upload success! Image saved to: {output_path}")
        else:
            print(f"❌ File upload error: {response.status_code}")
            print(f"📄 Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Error: Could not connect to API. Make sure the server is running on http://localhost:8000"
        )
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        # Clean up test file
        if test_file_path.exists():
            test_file_path.unlink()


def test_health_endpoint():
    """Test the health check endpoint."""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check: {result}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(
            "❌ Error: Could not connect to API. Make sure the server is running on http://localhost:8000"
        )


if __name__ == "__main__":
    print("🚀 Testing Genalog Text-to-Image API")
    print("=" * 50)

    print("\n1. Testing health endpoint...")
    test_health_endpoint()

    print("\n2. Testing text-to-image conversion...")
    test_text_to_image_api()

    print("\n3. Testing file upload...")
    test_file_upload_api()

    print("\n✨ Testing complete!")
