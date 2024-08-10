import os
import sqlite3
import exifread
from statistics import mean
from fractions import Fraction

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
                location TEXT,
                focal_length REAL,
                aperture REAL,
                shutter_speed REAL,
                hour_taken TEXT,
                folder_path TEXT,
                UNIQUE(filename, folder_path) -- Ajoute une contrainte UNIQUE sur filename et folder_path
            )
        ''')
        
        # Vérifier et ajouter la colonne folder_path si elle n'existe pas
        cursor.execute("PRAGMA table_info(photos);")
        columns = [column[1] for column in cursor.fetchall()]
        if 'folder_path' not in columns:
            cursor.execute("ALTER TABLE photos ADD COLUMN folder_path TEXT;")
        
        conn.commit()
        conn.close()
        print("Database initialized and table 'photos' is up-to-date.")

    @staticmethod
    def process_image(filepath):
        _, ext = os.path.splitext(filepath)
        ext = ext.lower().strip('.')
        
        with open(filepath, 'rb') as f:
            tags = exifread.process_file(f)
        
        if ext == 'png':
            return (os.path.basename(filepath), 'Unknown', 'Unknown', None, None, None, 'Unknown')

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

    raw_extensions = [
        'jpg', 'jpeg', 'png', 'tiff', 'tif', 'arw', 'crw', 'cr2', 'cr3',
        'nef', 'nrw', 'orf', 'ptx', 'pef', 'raf', 'rw2', 'srw'
    ]

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

                    # Si root et directory sont identiques, folder_path doit être une chaîne vide ou explicite
                    if root == directory:
                        folder_path = directory  # ou '/' ou 'root' selon ce qui est plus logique pour toi
                    else:
                        folder_path = os.path.relpath(root, directory)  # Chemin relatif du dossier

                    # Vérifier si le fichier existe déjà dans la base de données en fonction du filename + folder_path
                    cursor.execute('SELECT 1 FROM photos WHERE filename = ? AND folder_path = ?', (file, folder_path))
                    if cursor.fetchone() is None:
                        try:
                            photo_data = self.process_image(filepath)
                            cursor.execute('''
                                INSERT INTO photos (filename, date_taken, location, focal_length, aperture, shutter_speed, hour_taken, folder_path)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (*photo_data, folder_path))
                            processed_count += 1
                        except sqlite3.IntegrityError:
                            print(f"File '{file}' already exists in the database with the same folder path. Skipping...")
                        except Exception as e:
                            print(f"Error processing file '{filepath}': {e}")
                            # continue


        conn.commit()
        conn.close()

        print(f"Total files added to the database: {processed_count}")



    def get_photos_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT filename) FROM photos")
            return cursor.fetchone()[0]

    def get_folders(self, directory):
        directory = directory.replace("\\", "/")
        all_images = []
        folders_with_images = set()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT filename, folder_path FROM photos')
            all_photos = cursor.fetchall()

            for filename, folder_path in all_photos:
                full_path = os.path.join(directory, folder_path, filename).replace("\\", "/")
                if full_path.startswith(directory):
                    all_images.append(full_path)
                    folders_with_images.add(folder_path)

        return {
            'all_images': all_images,
            'folders_with_images': list(folders_with_images)
        }

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

            if avg_shutter_speed != 'N/A' and avg_shutter_speed != 0:
                inverse_avg_shutter_speed = 1 / avg_shutter_speed
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
