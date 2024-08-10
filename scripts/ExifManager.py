import exifread
from geopy.geocoders import Nominatim

class ExifManager:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="photo_analyzer")

    def extract_exif(self, filepath):
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f)
        
        # Extraction des données de base
        date_taken = tags.get('EXIF DateTimeOriginal', 'Unknown')
        focal_length = tags.get('EXIF FocalLength', 'Unknown')
        aperture = tags.get('EXIF FNumber', 'Unknown')
        shutter_speed = tags.get('EXIF ExposureTime', 'Unknown')
        camera_model = tags.get('Image Model', 'Unknown')
        gps_info = self.extract_gps(tags)
        
        return {
            'date_taken': date_taken,
            'focal_length': focal_length,
            'aperture': aperture,
            'shutter_speed': shutter_speed,
            'camera_model': camera_model,
            'gps_info': gps_info,
        }

    def extract_gps(self, tags):
        gps_latitude = tags.get('GPS GPSLatitude', None)
        gps_latitude_ref = tags.get('GPS GPSLatitudeRef', None)
        gps_longitude = tags.get('GPS GPSLongitude', None)
        gps_longitude_ref = tags.get('GPS GPSLongitudeRef', None)
        
        if gps_latitude and gps_longitude and gps_latitude_ref and gps_longitude_ref:
            lat = self.convert_to_degrees(gps_latitude)
            lon = self.convert_to_degrees(gps_longitude)
            if gps_latitude_ref.values[0] != 'N':
                lat = -lat
            if gps_longitude_ref.values[0] != 'E':
                lon = -lon
            return lat, lon
        return None

    @staticmethod
    def convert_to_degrees(value):
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)
    
    def reverse_geocode(self, gps_info):
        if gps_info:
            location = self.geolocator.reverse(gps_info)
            return location.address if location else "Unknown Location"
        return "Unknown Location"
