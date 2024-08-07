from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import os
import zipfile
import sqlite3
from scripts.database_manager import DatabaseManager  # Assurez-vous que ce nom est correct

class RoutesManager:
    def __init__(self):
        self.main = Blueprint('main', __name__)
        self._register_routes()

        # Création d'une instance de DatabaseManager
        self.db_manager = DatabaseManager()  # Utilisez db_manager, pas DatabaseManager

    def _register_routes(self):
        @self.main.route('/')
        def index():
            return render_template('index.html')

        @self.main.route('/photos', methods=['GET'])
        def get_photos():
            try:
                conn = sqlite3.connect('data/photos.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM photos")
                photos = cursor.fetchall()
                conn.close()
                return jsonify(photos)
            except sqlite3.OperationalError as e:
                return jsonify({"error": str(e)}), 500

        @self.main.route('/upload', methods=['GET', 'POST'])
        def upload():
            if request.method == 'POST':
                file = request.files['file']
                if file and file.filename.endswith('.zip'):
                    zip_path = os.path.join('data', file.filename)
                    file.save(zip_path)

                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall('data/images')

                    self.db_manager.populate_database('data/images')  # Utilisez self.db_manager

                    return redirect(url_for('main.index'))
            return render_template('upload.html')

        @self.main.route('/process_directory', methods=['GET', 'POST'])
        def process_directory():
            if request.method == 'POST':
                directory = request.form['directory']
                if os.path.isdir(directory):
                    print(directory)
                    self.db_manager.populate_database(directory)  # Utilisez self.db_manager
                    return redirect(url_for('main.index'))
            return render_template('enter_directory.html')
