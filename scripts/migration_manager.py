# migration_manager.py

import sqlite3

class MigrationManager:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def check_and_migrate(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(photos);")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'camera_model' not in columns:
                cursor.execute("ALTER TABLE photos ADD COLUMN camera_model TEXT;")
                print("Column 'camera_model' added.")
            if 'gps_info' not in columns:
                cursor.execute("ALTER TABLE photos ADD COLUMN gps_info TEXT;")
                print("Column 'gps_info' added.")
            
            conn.commit()
