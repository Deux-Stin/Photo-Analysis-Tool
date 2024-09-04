# database_optimizer.py

import sqlite3

class DatabaseOptimizer:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def add_index(self, column_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            index_name = f'idx_{column_name}'
            cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON photos ({column_name})')
            conn.commit()
            print(f"Index on column '{column_name}' created or already exists.")
            
    # def optimize(self):
    #     self.add_index('date_taken')
    #     self.add_index('folder_path')
    #     self.add_index('camera_model')
