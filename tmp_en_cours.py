from fractions import Fraction
import datetime
import sqlite3
import os
import exifread
import json
import subprocess
from statistics import mean
from PIL import Image, ExifTags
import re

class DatabaseManager:
    def __init__(self, db_path='data/photos.db'):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        # Créer le répertoire si nécessaire
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Créer la table photos si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                date_taken TEXT,
                hour_taken TEXT,
                focal_length REAL,
                aperture REAL,
                shutter_speed REAL,
                folder_path TEXT,
                brand_name TEXT,
                camera_model TEXT,
                gps_info TEXT,
                UNIQUE(filename, folder_path)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized and table 'photos' is created.")

    @staticmethod
    def get_exif_data(filepath):
        result = subprocess.run(['exiftool', '-json', filepath], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Erreur lors de l'exécution de exiftool: {result.stderr}")
            return None

        exif_data = json.loads(result.stdout)
        if not exif_data:
            print("Aucune donnée EXIF trouvée.")
            return None
        
        return exif_data[0]


    @staticmethod
    def process_image(filepath):
        _, ext = os.path.splitext(filepath)
        ext = ext.lower().strip('.')

        # Utiliser exiftool pour les fichiers heic
        if ext in ['heic', 'heif']: #, 'arw', 'cr2', 'nef'
            tags = DatabaseManager.get_exif_data(filepath)
        else:
            # Utiliser exifread pour les fichiers jpg, jpeg, tiff, etc.
            with open(filepath, 'rb') as f:
                tags = exifread.process_file(f)

        filename = os.path.basename(filepath)

        # Récupération et formatage de la date
        date_taken = tags.get('EXIF DateTimeOriginal', tags.get('DateTimeOriginal', 'Unknown'))
        if date_taken != 'Unknown':
            try:
                # Conversion de "YYYY:MM:DD HH:MM:SS" en "YYYY-MM-DD"
                date_taken = datetime.datetime.strptime(str(date_taken), "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d")
            except ValueError:
                print(f"Failed to parse date: {date_taken}")
                date_taken = 'Unknown'

        focal_length = tags.get('EXIF FocalLengthIn35mmFilm', tags.get('FocalLengthIn35mmFormat', 'Unknown'))
        aperture = tags.get('EXIF FNumber', tags.get('Aperture','Unknown'))
        shutter_speed = tags.get('EXIF ExposureTime', tags.get('ShutterSpeed', 'Unknown'))

        brand_name = tags.get('Image Make', tags.get('Make', 'Unknown'))
        camera_model = tags.get('Image Model', tags.get('Model', 'Unknown'))

        if ext not in ['heic', 'heif']:
            focal_length = str(focal_length.values) if focal_length !='Unknown' else 'Unknown'
            brand_name = str(brand_name.values) if brand_name != 'Unknown' else 'Unknown'
            camera_model = str(camera_model.values) if camera_model != 'Unknown' else 'Unknown'
            # Décodage info GPS :
            gps_latitude_ref = tags.get('GPS GPSLatitudeRef', 'Unknown')
            gps_latitude_ref = str(gps_latitude_ref.values) if gps_latitude_ref != 'Unknown' else 'Unknown'
            gps_latitude = tags.get('GPS GPSLatitude', 'Unknown')
            gps_latitude = gps_latitude.values if gps_latitude != 'Unknown' else [Fraction(0), Fraction(0), Fraction(0)]
            gps_longitude_ref = tags.get('GPS GPSLongitudeRef', 'Unknown')
            gps_longitude_ref = str(gps_longitude_ref.values) if gps_longitude_ref != 'Unknown' else 'Unknown'
            gps_longitude = tags.get('GPS GPSLongitude', 'Unknown')
            gps_longitude = gps_longitude.values if gps_longitude != 'Unknown' else [Fraction(0), Fraction(0), Fraction(0)]
        else:
            # # Décodage info GPS :
            # gps_latitude_ref = tags.get('GPS GPSLatitudeRef', tags.get('GPSLatitudeRef', 'Unknown'))
            # try:
            #     gps_latitude_ref = str(gps_latitude_ref.values) if gps_latitude_ref != 'Unknown' else 'Unknown'
            # except Exception as e:
            #     print(f"Error processing file '{filepath}': {e}")
            # gps_latitude_ref = gps_latitude_ref[0]

            # gps_latitude = tags.get('GPS GPSLatitude', tags.get('GPSLatitude', 'Unknown'))

            # try:
            #     gps_latitude = gps_latitude.values if gps_latitude != 'Unknown' else [Fraction(0), Fraction(0), Fraction(0)]
            # except Exception as e:
            #     print(f"Error processing file '{filepath}': {e}")

            # gps_longitude_ref = tags.get('GPS GPSLongitudeRef', tags.get('GPSLongitudeRef', 'Unknown'))
            # try:
            #     gps_longitude_ref = str(gps_longitude_ref.values) if gps_longitude_ref != 'Unknown' else 'Unknown'
            # except Exception as e:
            #     print(f"Error processing file '{filepath}': {e}")
            # gps_longitude_ref = gps_longitude_ref[0]

            # gps_longitude = tags.get('GPS GPSLongitude', tags.get('GPSLongitude', 'Unknown'))

            # try:
            #     gps_longitude = gps_longitude.values if gps_longitude != 'Unknown' else [Fraction(0), Fraction(0), Fraction(0)]
            # except Exception as e:
            #     print(f"Error processing file '{filepath}': {e}")

            # Extraction des informations GPS
            gps_latitude_ref = tags.get('GPSLatitudeRef', 'Unknown')
            gps_latitude_ref = gps_latitude_ref[0]
            gps_latitude = tags.get('GPSLatitude', 'Unknown')
            gps_longitude_ref = tags.get('GPSLongitudeRef', 'Unknown')
            gps_longitude_ref = gps_longitude_ref[0]
            gps_longitude = tags.get('GPSLongitude', 'Unknown')

            if gps_latitude != 'Unknown' and gps_longitude != 'Unknown':
                latitude_dms = DatabaseManager.format_dms(gps_latitude, gps_latitude_ref)
                longitude_dms = DatabaseManager.format_dms(gps_longitude, gps_longitude_ref)
                gps_info = f"Latitude: {latitude_dms}, Longitude: {longitude_dms}"
            else:
                gps_info = "Unknown"


        # Convertir les coordonnées
        latitude_decimal = DatabaseManager.ratio_to_decimal(gps_latitude)
        longitude_decimal = DatabaseManager.ratio_to_decimal(gps_longitude)

        # Stocker les informations dans un dictionnaire
        gps_info = {
            'latitude': latitude_decimal,
            'longitude': longitude_decimal,
            'latitude_ref': gps_latitude_ref,
            'longitude_ref': gps_longitude_ref
        }
        gps_info = (
            f"Latitude: {gps_info['latitude']} {gps_info['latitude_ref']}, "
            f"Longitude: {gps_info['longitude']} {gps_info['longitude_ref']}"
        )
        
        hour_taken = 'Unknown'
        if date_taken != 'Unknown' and ' ' in str(tags.get('EXIF DateTimeOriginal', '')):
            date_parts = str(tags.get('EXIF DateTimeOriginal', '')).split(' ')
            if len(date_parts) > 1:
                hour_taken = date_parts[1]

        try:
            focal_length_value = float(focal_length.values[0].num) / float(focal_length.values[0].den) if focal_length != 'Unknown' else None
        except (AttributeError, TypeError):
            focal_length_value = None

        try:
            aperture_value = float(aperture.values[0].num) / float(aperture.values[0].den) if aperture != 'Unknown' else None
        except (AttributeError, TypeError):
            aperture_value = None

        try:
            shutter_speed_value = float(shutter_speed.values[0].num) / float(shutter_speed.values[0].den) if shutter_speed != 'Unknown' else None
        except (AttributeError, TypeError):
            shutter_speed_value = None

        # Remplacement des valeurs None par des chaînes vides ou valeurs par défaut
        focal_length_value = focal_length_value if focal_length_value is not None else 0.0
        aperture_value = aperture_value if aperture_value is not None else 0.0
        shutter_speed_value = shutter_speed_value if shutter_speed_value is not None else 0.0

        folder_path = os.path.dirname(filepath)

        return (
            filename,
            date_taken,
            hour_taken,
            focal_length_value,
            aperture_value,
            shutter_speed_value,
            brand_name,
            camera_model,
            gps_info,
            folder_path
        )

    raw_extensions = [
        'jpg', 'jpeg', 'heic', 'heif', 'tiff', 'tif', 'arw', 'crw', 'cr2', 'cr3',
        'nef', 'nrw', 'orf', 'ptx', 'pef', 'raf', 'rw2', 'srw'
    ]


    @staticmethod
    def format_dms(dms, ref):
        # Si les valeurs GPS sont déjà sous forme de fraction
        if isinstance(dms, list):
            degrees, minutes, seconds = [float(Fraction(str(part))) for part in dms]
        else:
            # Extraire les parties numériques à partir de la chaîne de caractères DMS
            dms_match = re.match(r"(\d+)\s*deg\s*(\d+)'\s*([\d.]+)\"\s*([NSEW])", dms)
            if dms_match:
                degrees = float(dms_match.group(1))
                minutes = float(dms_match.group(2))
                seconds = float(dms_match.group(3))
                ref = dms_match.group(4)
            else:
                raise ValueError("Invalid DMS format: " + dms)

        # Formater les valeurs numériques en une chaîne DMS
        dms_formatted = f"{int(degrees)} deg {int(minutes)}' {seconds:.2f}\" {ref}"
        return dms_formatted

    @staticmethod
    def ratio_to_decimal(ratio):
        """
        Convertit un ratio GPS en degrés décimaux.
        
        :param ratio: Une liste de fractions [degrés, minutes, secondes]
        :return: La valeur en degrés décimaux
        """
        if isinstance(ratio, list) and len(ratio) == 3:
            degrees, minutes, seconds = ratio
            # Assurer que degrees, minutes, et seconds sont des instances de Fraction
            if not isinstance(degrees, Fraction):
                degrees = Fraction(degrees)
            if not isinstance(minutes, Fraction):
                minutes = Fraction(minutes)
            if not isinstance(seconds, Fraction):
                seconds = Fraction(seconds)
            
            return float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        else:
            raise ValueError("Le ratio doit être une liste de trois valeurs : [degrés, minutes, secondes]")

    def populate_database(self, directory, raw_extensions=None):
        if raw_extensions is None:
            raw_extensions = self.raw_extensions  # Utiliser la liste par défaut

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        processed_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                _, ext = os.path.splitext(file)
                ext = ext.lower().strip('.')
                
                if ext in raw_extensions:
                    filepath = os.path.join(root, file)

                    if root == directory:
                        folder_path = directory
                    else:
                        folder_path = os.path.relpath(root, directory)

                    cursor.execute('SELECT 1 FROM photos WHERE filename = ? AND folder_path = ?', (file, folder_path))
                    if cursor.fetchone() is None:
                        try:
                            photo_data = self.process_image(filepath)
                            cursor.execute('''
                                INSERT INTO photos (filename, date_taken, hour_taken, focal_length, aperture, shutter_speed, 
                                           brand_name, camera_model, gps_info, folder_path)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', photo_data)
                            processed_count += 1
                        except Exception as e:
                            print(f"Error processing file '{filepath}': {e}")
                            continue

        conn.commit()
        conn.close()

        print(f"Total files added to the database: {processed_count}")

    def get_all_photos(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM photos")
            return cursor.fetchall()

    def get_folders(self, directory):
        directory = directory.replace("\\", "/")
        folders_with_images = set()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT folder_path 
                FROM photos 
                WHERE folder_path IS NOT NULL AND folder_path != ''
            ''')
            all_folders = cursor.fetchall()

            for folder in all_folders:
                full_folder_path = os.path.join(directory, folder[0]).replace("\\", "/")
                if os.path.exists(full_folder_path):
                    folders_with_images.add(folder[0])

        return list(folders_with_images)

    def get_photo_data(self, filter_text):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if filter_text == "All":
                cursor.execute("SELECT date_taken, hour_taken FROM photos")
            else:
                cursor.execute("SELECT date_taken, hour_taken FROM photos WHERE folder_path = ?", (filter_text,))
            
            data = cursor.fetchall()
            print(f"Data fetched with filter '{filter_text}': {data}")
            return data

    def get_statistics(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(DISTINCT filename) FROM photos")
            total_images = cursor.fetchone()[0]

            cursor.execute("SELECT MIN(date_taken) FROM photos WHERE date_taken != 'Unknown'")
            earliest_date = cursor.fetchone()[0] or "No valid date found"

            cursor.execute("SELECT MAX(date_taken) FROM photos WHERE date_taken != 'Unknown'")
            latest_date = cursor.fetchone()[0] or "No valid date found"

            cursor.execute("SELECT focal_length FROM photos WHERE focal_length IS NOT NULL")
            focal_lengths = [row[0] for row in cursor.fetchall()]
            avg_focal_length = mean(focal_lengths) if focal_lengths else 'N/A'
            avg_focal_length = round(avg_focal_length, 2) if avg_focal_length != 'N/A' else 'N/A'

            cursor.execute("SELECT aperture FROM photos WHERE aperture IS NOT NULL")
            apertures = [row[0] for row in cursor.fetchall()]
            avg_aperture = mean(apertures) if apertures else 'N/A'
            avg_aperture = round(avg_aperture, 2) if avg_aperture != 'N/A' else 'N/A'

            cursor.execute('SELECT shutter_speed FROM photos WHERE shutter_speed IS NOT NULL')
            shutter_speeds = [row[0] for row in cursor.fetchall()]
            avg_shutter_speed = mean(shutter_speeds) if shutter_speeds else 'N/A'
            avg_shutter_speed = round(avg_shutter_speed, 2) if avg_shutter_speed != 'N/A' else 'N/A'

            inverse_avg_shutter_speed = 1 / avg_shutter_speed if avg_shutter_speed != 'N/A' and avg_shutter_speed != 0 else 'N/A'
            if inverse_avg_shutter_speed != 'N/A':
                inverse_avg_shutter_speed_fraction = Fraction(inverse_avg_shutter_speed).limit_denominator()
                inverse_avg_shutter_speed_fraction = f"1/{inverse_avg_shutter_speed_fraction.numerator}"
            else:
                inverse_avg_shutter_speed_fraction = 'N/A'

            return {
                'total_images': total_images,
                'earliest_date': earliest_date,
                'latest_date': latest_date,
                'avg_focal_length': avg_focal_length,
                'avg_aperture': avg_aperture,
                'avg_shutter_speed': avg_shutter_speed,
                'inverse_avg_shutter_speed': inverse_avg_shutter_speed_fraction,
            }
