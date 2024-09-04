from fractions import Fraction
import re

def dms_to_decimal(dms):
    """
    Convert DMS (degrees, minutes, seconds) string format to decimal degrees.
    """
    match = re.match(r"(\d+)\s*deg\s*(\d+)'\s*([\d.]+)\"\s*([NSEW])", dms)
    if not match:
        raise ValueError(f"Invalid DMS format: {dms}")
    
    degrees = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    direction = match.group(4)
    
    decimal_degrees = degrees + minutes / 60 + seconds / 3600
    
    if direction in ['S', 'W']:
        decimal_degrees *= -1
    
    return decimal_degrees, direction

def ratio_to_decimal(ratio):
    """
    Convert a ratio format (degrees, minutes, seconds) to decimal degrees.
    """
    degrees, minutes, seconds = ratio
    degrees = float(Fraction(degrees))
    minutes = float(Fraction(minutes))
    seconds = float(Fraction(seconds))
    
    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
    return decimal_degrees

# Exemples de données GPS
# Format JPEG
jpeg_latitude = [15, 40, Fraction(265389, 12500)]
jpeg_longitude = [96, 34, Fraction(226779, 5000)]

# Format HEIC
heic_latitude = '10 deg 34\' 17.77" N'
heic_longitude = '103 deg 19\' 18.21" E'

# Conversion des formats
jpeg_latitude_decimal = ratio_to_decimal(jpeg_latitude)
jpeg_longitude_decimal = ratio_to_decimal(jpeg_longitude)

heic_latitude_decimal, latitude_ref = dms_to_decimal(heic_latitude)
heic_longitude_decimal, longitude_ref = dms_to_decimal(heic_longitude)

gps_info = (f"Latitude : {heic_latitude_decimal} {latitude_ref}, "
            f"Longitude : {heic_longitude_decimal} {longitude_ref}"
            )

# Affichage des résultats
print(f"JPEG Latitude en degrés décimaux: {jpeg_latitude_decimal}")
print(f"JPEG Longitude en degrés décimaux: {jpeg_longitude_decimal}")
print(f"HEIC Latitude en degrés décimaux: {heic_latitude_decimal}")
print(f"HEIC Longitude en degrés décimaux: {heic_longitude_decimal}")
