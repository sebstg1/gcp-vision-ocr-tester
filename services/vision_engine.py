import os
import io
from google.cloud import vision
from PIL import Image

class OcrEngine:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
        pass

    def extract_text_from_image(self, image: Image.Image) -> str:
        """
        Returns text extracted from a PIL.Image object.
        """
        try:
            client = vision.ImageAnnotatorClient()
            
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format if image.format else 'PNG')
            content = img_byte_arr.getvalue()
            
            image_vision = vision.Image(content=content)
            response = client.text_detection(image=image_vision)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f'{response.error.message}')
            
            if texts:
                return texts[0].description
            return "No text detected."
            
        except Exception as e:
            return f"Error processing image: {str(e)}"