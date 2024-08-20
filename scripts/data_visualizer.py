import sqlite3
import pyqtgraph as pg
import os
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QComboBox, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from fractions import Fraction
import numpy as np
import datetime

class DataVisualizer(QWidget):
    def __init__(self, db_path, directory):
        super().__init__()
        self.db_path = db_path
        self.directory = directory  # Stockez le répertoire
        self.init_ui()
        # if directory:  # Vérifiez si directory n'est pas None
        self.load_folders()
        self.load_data()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()

        # Liste déroulante pour le filtrage des dossiers
        self.folder_filter = QComboBox(self)
        self.folder_filter.addItem("All")
        main_layout.addWidget(self.folder_filter)

        # Layout horizontal pour séparer 1/3 et 2/3
        content_layout = QHBoxLayout()

        # Layout pour la section gauche (1/3)
        left_layout = QVBoxLayout()

        # Menu déroulant pour choisir le type d'affichage
        self.display_type = QComboBox(self)
        self.display_type.addItem("Date Taken")
        self.display_type.addItem("Aperture")
        self.display_type.addItem("Shutter Speed")
        self.display_type.addItem("Brand Name")
        left_layout.addWidget(self.display_type)

        # Menu déroulant pour choisir le type de graphique
        self.graph_type = QComboBox(self)
        self.graph_type.addItem("Bar Graph")
        self.graph_type.addItem("Line Graph")
        left_layout.addWidget(self.graph_type)

        # Label pour afficher le nombre total de photos
        self.total_photos_label = QLabel("Total Photos: 0", self)
        left_layout.addWidget(self.total_photos_label)

        # Layout pour la section droite (2/3)
        right_layout = QVBoxLayout()

        # Widget pour le graphique
        self.plot_widget = pg.PlotWidget(background='w')
        right_layout.addWidget(self.plot_widget)

        # Ajouter les layouts gauche (1/3) et droite (2/3) au content_layout
        content_layout.addLayout(left_layout, 1)  # 1/3
        content_layout.addLayout(right_layout, 2)  # 2/3

        # Ajouter le layout horizontal au layout principal
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

        # Connexion des signaux
        self.graph_type.currentIndexChanged.connect(self.update_plot)
        self.display_type.currentIndexChanged.connect(self.update_plot)
        self.folder_filter.currentIndexChanged.connect(self.update_plot)

    def load_folders(self):
        data = self.get_folders()
        self.folder_filter.addItems(data['folders_with_images'])

    # def get_folders(self, directory):
    #     directory = directory.replace("\\", "/")
    #     all_images = []
    #     folders_with_images = set()

    #     with sqlite3.connect(self.db_path) as conn:
    #         cursor = conn.cursor()
    #         cursor.execute('SELECT filename, folder_path FROM photos')
    #         all_photos = cursor.fetchall()

    #         for filename, folder_path in all_photos:
    #             full_path = os.path.join(directory, folder_path, filename).replace("\\", "/")
    #             if full_path.startswith(directory):
    #                 all_images.append(full_path)
    #                 folders_with_images.add(folder_path)

    #     return {
    #         'all_images': all_images,
    #         'folders_with_images': list(folders_with_images)
    #     }
    
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

        return {
            'all_images': all_images,
            'folders_with_images': list(folders_with_images)
        }

    def load_data(self):
        # Charger les données depuis la base de données en fonction du filtre de dossier sélectionné
        selected_folder = self.folder_filter.currentText()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
        SELECT date_taken, COUNT(*)
        FROM photos
        WHERE date_taken IS NOT NULL AND date_taken != 'Unknown'
        '''

        if selected_folder != "All":
            query += " AND folder_path = ?"
            cursor.execute(query, (selected_folder,))
        else:
            cursor.execute(query)

        query += " GROUP BY date_taken ORDER BY date_taken"

        data = cursor.fetchall()
        conn.close()

        # Convertir les données en format utilisable
        self.data = {
            'dates': [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() for row in data if row[0] is not None],
            'counts': [row[1] for row in data if row[0] is not None]
        }

        # Mise à jour du total des photos
        self.total_photos_label.setText(f"Total Photos: {sum(self.data['counts'])}")

    def update_plot(self):
        display_type = self.display_type.currentText()
        graph_type = self.graph_type.currentText()
        selected_folder = self.folder_filter.currentText()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Définition de la requête SQL en fonction du type de données affiché et du dossier sélectionné
            if display_type == "Date Taken":
                query = "SELECT date_taken, COUNT(*) FROM photos WHERE date_taken != 'Unknown'"
                if selected_folder != "All":
                    query += " AND folder_path = ? GROUP BY date_taken ORDER BY date_taken"
                    cursor.execute(query, (selected_folder,))
                else:
                    query += " GROUP BY date_taken ORDER BY date_taken"
                    cursor.execute(query)
            elif display_type == "Aperture":
                query = "SELECT aperture, COUNT(*) FROM photos"
                if selected_folder != "All":
                    query += " WHERE folder_path = ? GROUP BY aperture ORDER BY aperture"
                    cursor.execute(query, (selected_folder,))
                else:
                    query += " GROUP BY aperture ORDER BY aperture"
                    cursor.execute(query)
            elif display_type == "Shutter Speed":
                query = "SELECT shutter_speed, COUNT(*) FROM photos"
                if selected_folder != "All":
                    query += " WHERE folder_path = ? GROUP BY shutter_speed ORDER BY shutter_speed"
                    cursor.execute(query, (selected_folder,))
                else:
                    query += " GROUP BY shutter_speed ORDER BY shutter_speed"
                    cursor.execute(query)
            elif display_type == "Brand Name":
                query = "SELECT brand_name, COUNT(*) FROM photos"
                if selected_folder != "All":
                    query += " WHERE folder_path = ? GROUP BY brand_name ORDER BY brand_name"
                    cursor.execute(query, (selected_folder,))
                else:
                    query += " GROUP BY brand_name ORDER BY brand_name"
                    cursor.execute(query)

            data = cursor.fetchall()

            if not data:
                print("No data found for the selected criteria.")
                return

            x_values = []
            y_values = []

            # Traitement spécifique pour chaque type de données
            if display_type == "Date Taken":
                for item in data:
                    date_str = item[0]
                    try:
                        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                        x_values.append(date.strftime('%Y-%m-%d'))
                        y_values.append(item[1])
                    except ValueError:
                        print(f"Invalid date format: {date_str}")
                        continue

                ticks = [(i, date) for i, date in enumerate(x_values)]
                self.plot_widget.getAxis('bottom').setTicks([ticks])
            elif display_type == "Shutter Speed":
                for item in data:
                    speed = item[0]
                    if speed > 0:
                        fraction = Fraction(1, int(1/speed)).limit_denominator()
                        x_values.append(f"1/{fraction.denominator}")
                    else:
                        x_values.append("Unknown")
                    y_values.append(item[1])
            else:
                for item in data:
                    x_values.append(str(item[0]))
                    y_values.append(item[1])

            self.plot_widget.clear()

            # Affichage des graphiques
            if graph_type == "Bar Graph":
                bg = pg.BarGraphItem(x=np.arange(len(x_values)), height=y_values, width=0.6, brush='b')
                self.plot_widget.addItem(bg)
            elif graph_type == "Line Graph":
                self.plot_widget.plot(y=y_values, x=np.arange(len(x_values)), symbol='o', pen='b')

            # Ajout des valeurs au survol
            self.add_hover_values(x_values, y_values)

            # Mise à jour des ticks pour les labels de l'axe des X
            ticks = [(i, x) for i, x in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])

    def add_hover_values(self, x_values, y_values):
        # Implémentation de l'affichage des valeurs au survol des points/barres
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            text = pg.TextItem(f"{y}", anchor=(0.5, -1.5), color='k')
            text.setPos(i, y)
            self.plot_widget.addItem(text)
