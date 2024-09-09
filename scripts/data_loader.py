import sqlite3
import os
import datetime
from PyQt5.QtCore import QDate

class DataLoader:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_folders(self):
        all_images = []
        folders_with_images = set()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT filename, folder_path FROM photos')
            all_photos = cursor.fetchall()

            for filename, folder_path in all_photos:
                full_path = os.path.join(folder_path, filename).replace("\\", "/")
                all_images.append(full_path)
                folders_with_images.add(folder_path)

        folder_images = {folder: [] for folder in folders_with_images}
        for image in all_images:
            folder = os.path.dirname(image)
            folder_images.setdefault(folder, []).append(image)

        return {
            'all_images': all_images,
            'folders_with_images': list(folders_with_images),
            'folder_images': folder_images
        }
    
    def get_brands(self, folder=None):
        # Récupère les marques d'appareils photo depuis la base de données
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if folder and folder != "All":
                cursor.execute("SELECT DISTINCT brand_name FROM photos WHERE folder_path = ? ORDER BY brand_name", (folder,))
            else:
                cursor.execute("SELECT DISTINCT brand_name FROM photos ORDER BY brand_name")

            brands = [row[0] for row in cursor.fetchall()]
        return brands

    def load_data(self, selected_folder, date_from, date_to,
                aperture_min, aperture_max,
                shutter_speed_min, shutter_speed_max,
                focal_length_min, focal_length_max,
                iso_min, iso_max):
        query = '''
        SELECT date_taken, COUNT(*)
        FROM photos
        WHERE date_taken IS NOT NULL AND date_taken != 'Unknown'
        '''
        params = []

        if selected_folder != "All":
            query += " AND folder_path = ?"
            params.append(selected_folder)
        if date_from and date_to:
            query += " AND date_taken BETWEEN ? AND ?"
            params.extend([date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d')])
        if aperture_min is not None and aperture_max is not None:
            query += " AND aperture BETWEEN ? AND ?"
            params.extend([aperture_min, aperture_max])

        if iso_min is not None and iso_max is not None:
            query += " AND iso BETWEEN ? AND ?"
            params.extend([iso_min, iso_max])
        if focal_length_min is not None and focal_length_max is not None:
            query += " AND focal_length_in_35mm BETWEEN ? AND ?"
            params.extend([focal_length_min, focal_length_max])

        if shutter_speed_min is not None and shutter_speed_max is not None:
            query += " AND shutter_speed BETWEEN ? AND ?"
            params.extend([shutter_speed_min, shutter_speed_max])

        query += " GROUP BY date_taken ORDER BY date_taken"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            data = cursor.fetchall()

        return {
            'dates': [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() for row in data if row[0] is not None],
            'counts': [row[1] for row in data if row[0] is not None]
        }


    def get_parameter_ranges(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query to get min and max values for each parameter
            query = """
            SELECT 
                MIN(iso), MAX(iso),
                MIN(shutter_speed), MAX(shutter_speed),
                MIN(aperture), MAX(aperture),
                MIN(focal_length_in_35mm), MAX(focal_length_in_35mm),
                MIN(date_taken), MAX(date_taken)
            FROM photos
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            return {
                "iso": (result[0], result[1]),
                "shutter_speed": (result[2], result[3]),
                "aperture": (result[4], result[5]),
                "focal_length": (result[6], result[7]),
                "date_range": (result[8], result[9])
            }