import sqlite3
import os
import exifread
from app.utils import ExifUtils

class DatabaseManager:
    def __init__(self, db_path='data/photos.db'):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    date_taken TEXT,
                    location TEXT,
                    focal_length REAL,
                    aperture REAL,
                    shutter_speed REAL,
                    hour_taken TEXT
                )
            ''')
            conn.commit()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(photos);")
            columns = [column[1] for column in cursor.fetchall()]
            if 'hour_taken' not in columns:
                cursor.execute("ALTER TABLE photos ADD COLUMN hour_taken TEXT;")
            conn.commit()
        conn.close()

    @staticmethod
    def process_image(filepath):
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f)

        date_taken = tags.get('EXIF DateTimeOriginal', 'Unknown')
        focal_length = tags.get('EXIF FocalLength', 'Unknown')
        aperture = tags.get('EXIF FNumber', 'Unknown')
        shutter_speed = tags.get('EXIF ExposureTime', 'Unknown')

        hour_taken = 'Unknown'
        if date_taken != 'Unknown':
            date_parts = str(date_taken).split(' ')
            if len(date_parts) > 1:
                hour_taken = date_parts[1]

        return (os.path.basename(filepath), str(date_taken), 'Unknown',
                float(focal_length.values[0].num) / float(focal_length.values[0].den) if focal_length != 'Unknown' else None,
                float(aperture.values[0].num) / float(aperture.values[0].den) if aperture != 'Unknown' else None,
                float(shutter_speed.values[0].num) / float(shutter_speed.values[0].den) if shutter_speed != 'Unknown' else None,
                hour_taken)
    
    # Liste des extensions de fichiers photo RAW à gérer
    raw_extensions = [
        'jpg', 'jpeg', 'png', 'tiff', 'tif', 'arw', 'crw', 'cr2', 'cr3',
        'nef', 'nrw', 'orf', 'ptx', 'pef', 'raf', 'rw2', 'srw'
    ]

    def populate_database(self, directory, raw_extensions=None):
        if raw_extensions is None:
            raw_extensions = self.raw_extensions  # Utiliser la liste par défaut

        # Convertir la liste en une chaîne de caractères séparée par des virgules
        extensions_str = ', '.join(raw_extensions)

        # Afficher le message
        print("Following format files can be processed : " + extensions_str)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Initialiser le compteur
        processed_count = 0

        for root, _, files in os.walk(directory):
            for file in files:
                # Obtenir l'extension du fichier
                _, ext = os.path.splitext(file)
                ext = ext.lower().strip('.')
                
                # Vérifier si l'extension est dans la liste des extensions RAW
                if ext in raw_extensions:
                    filepath = os.path.join(root, file)
                    photo_data = self.process_image(filepath)  # Utiliser self.process_image
                    cursor.execute('''
                        INSERT INTO photos (filename, date_taken, location, focal_length, aperture, shutter_speed, hour_taken)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', photo_data)

                    # Incrémenter le compteur
                    processed_count += 1

        conn.commit()
        conn.close()

        # Afficher le nombre total de fichiers traités
        print(f"Total files added to the database: {processed_count}")
