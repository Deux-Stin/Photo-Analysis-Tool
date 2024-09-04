# app/utils.py

from PIL import Image
import exifread
import os

class ExifUtils:
    @staticmethod
    def get_exif_data(image_path):
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            if not exif_data:
                with open(image_path, 'rb') as f:
                    tags = exifread.process_file(f)
                    return tags
            return exif_data
        except Exception as e:
            print(f"Error reading {image_path}: {e}")
            return None
