import exifread
from PIL import Image

class ExifExtractor:
    @staticmethod
    def get_exif_data(filename):
        exif_data = {}
        try:
            with open(filename, 'rb') as file:
                tags = exifread.process_file(file, details=False)
                for tag in ('DateTimeOriginal', 'GPSInfo', 'FocalLength', 'ApertureValue', 'ShutterSpeedValue'):
                    if tag in tags:
                        exif_data[tag] = str(tags[tag])
                if 'GPSInfo' in tags:
                    gps_info = tags['GPSInfo']
                    latitude = gps_info.get('GPSLatitude', None)
                    longitude = gps_info.get('GPSLongitude', None)
                    if latitude and longitude:
                        exif_data['GPSInfo'] = f"{latitude} {longitude}"
        except Exception as e:
            print(f"Erreur lors de l'extraction des données EXIF pour {filename}: {e}")
        return exif_data
