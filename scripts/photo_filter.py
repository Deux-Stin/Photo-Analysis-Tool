import os
import sqlite3

class PhotoFilter:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_folders_with_images(self, base_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtenir les chemins des dossiers contenant des images depuis la base de données
        cursor.execute("SELECT DISTINCT folder_path FROM photos")
        image_folders = set(row[0] for row in cursor.fetchall())
        
        # Fonction récursive pour parcourir les dossiers
        def find_folders_with_images(current_path):
            folders_with_images = set()
            
            for entry in os.scandir(current_path):
                if entry.is_dir():
                    folder_path = entry.path
                    if folder_path in image_folders:
                        folders_with_images.add(folder_path)
                    # Rechercher dans les sous-dossiers
                    folders_with_images.update(find_folders_with_images(folder_path))
            
            return folders_with_images
        
        # Trouver les dossiers avec images à partir du dossier de base
        folders_with_images = find_folders_with_images(base_path)
        
        conn.close()
        return folders_with_images
    