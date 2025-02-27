import boto3
import filetype
from django.conf import settings
from PIL import Image
import io
from fuzzywuzzy import fuzz

textract_client = boto3.client(
    "textract",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def extract_text_from_ID(document):
    """Extract text from images (JPEG, PNG) or PDFs using AWS Textract."""
    content = document.read()
    # Reset so that next function can read document
    document.seek(0) 
    kind = filetype.guess(content)

    if kind is None:
        raise ValueError("Unsupported file type")

    if kind.extension in ["jpg", "jpeg", "png"]:
        response = textract_client.analyze_document(
            Document={"Bytes": content}, FeatureTypes=["FORMS"]
        )
    elif kind.extension == "pdf":
        response = textract_client.analyze_document(
            Document={"Bytes": content}, FeatureTypes=["TABLES", "FORMS"]
        )
    else:
        raise ValueError("Unsupported file format")

    extracted_text = " ".join(
        [item["Text"] for item in response["Blocks"] if item["BlockType"] == "WORD"]
    )
    # Reset so that next function can read document
    document.seek(0)

    return extracted_text


# def is_name_matching(provided_name, extracted_text):
#     return provided_name.lower() in extracted_text.lower()


def is_name_matching(provided_name, extracted_text, threshold=80):

    provided_name = provided_name.lower().strip()
    extracted_text = extracted_text.lower().strip()

    # Use fuzzy matching to compare the provided name with extracted name
    match_score = fuzz.partial_ratio(provided_name, extracted_text)
    return match_score >= threshold


rekognition_client = boto3.client(
    "rekognition",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def extract_face_from_ID(document):

    image_bytes = document.read()

    response = rekognition_client.detect_faces(
        Image={"Bytes": image_bytes}, Attributes=["ALL"]
    )

    if not response.get("FaceDetails"):
        return None 

    # Open the image with Pillow
    image = Image.open(io.BytesIO(image_bytes))

    # Get face bounding box (assuming only one face)
    face_data = response["FaceDetails"][0]["BoundingBox"]

    width, height = image.size
    left = int(face_data["Left"] * width)
    top = int(face_data["Top"] * height)
    right = int((face_data["Left"] + face_data["Width"]) * width)
    bottom = int((face_data["Top"] + face_data["Height"]) * height)

    # Crop face
    face_image = image.crop((left, top, right, bottom))

    # Convert cropped image to bytes
    face_io = io.BytesIO()
    face_image.save(face_io, format="JPEG")  # Save as JPEG
    return face_io.getvalue()  # Return bytes of the cropped image
