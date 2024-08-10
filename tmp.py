def populate_database(self, directory, raw_extensions=None):
    if raw_extensions is None:
        raw_extensions = self.raw_extensions  # Utiliser la liste par défaut

    extensions_str = ', '.join(raw_extensions)
    
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    processed_count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower().strip('.')
            
            if ext in raw_extensions:
                filepath = os.path.join(root, file)
                folder_path = os.path.relpath(root, directory)  # Chemin relatif du dossier

                cursor.execute('SELECT 1 FROM photos WHERE filename = ?', (file,))
                if cursor.fetchone() is None:
                    photo_data = self.process_image(filepath)
                    cursor.execute('''
                        INSERT INTO photos (filename, date_taken, location, focal_length, aperture, shutter_speed, hour_taken, folder_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', photo_data + (folder_path,))
                processed_count += 1

    conn.commit()
    conn.close()
    print(f"Total files added to the database: {processed_count}")
