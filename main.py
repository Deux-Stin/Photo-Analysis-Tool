import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QPushButton, QTabWidget, QMessageBox, QTextEdit, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon
from scripts.data_visualizer import DataVisualizer
from scripts.database_manager import DatabaseManager
from scripts.sorting_filtering import SortingFilteringWidget
from scripts.thumbnail_view import ThumbnailViewWidget
from scripts.export_data import ExportDataWidget
from scripts.ui_enhancements import UIEnhancementsWidget
from scripts.map_view import MapViewWidget  # Importer la classe MapViewWidget
from scripts.data_loader import DataLoader
import sqlite3
import folium
import re, os
from PyQt5.QtCore import Qt

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Création d'un QTextEdit pour afficher le contenu du README.md
        self.readme_display = QTextEdit(self)
        self.readme_display.setReadOnly(True)
        self.readme_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Permet au QTextEdit de s'étendre


        # Chargement du contenu du README.md
        self.load_readme_content()

        # Ajout du QTextEdit au layout
        layout.addWidget(self.readme_display)

        self.folder_button = QPushButton("Select Folder to Analyze", self)
        self.folder_button.clicked.connect(self.select_folder)

        # Appliquer des styles pour rendre le bouton plus visible tout en maintenant la taille du conteneur
        self.folder_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;  /* Couleur de fond bleu */
                color: white;  /* Couleur du texte en blanc */
                font-size: 16px;  /* Taille de la police */
                padding: 15px 30px;  /* Ajouter du padding pour une taille de bouton adéquate */
                border-radius: 8px;  /* Arrondir les coins */
                border: 2px solid #2980b9;  /* Ajouter une bordure bleue foncée */
                min-width: 200px;  /* Largeur minimale du bouton */
                min-height: 50px;  /* Hauteur minimale du bouton */
            }
            QPushButton:hover {
                background-color: #2980b9;  /* Couleur de fond plus foncée au survol */
            }
            QPushButton:pressed {
                background-color: #1f6391;  /* Couleur de fond encore plus foncée lors du clic */
            }
        """)

        # Ajouter le bouton avec un alignement central
        layout.addWidget(self.folder_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def select_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        directory = directory.replace("/", "\\")
        if directory:
            self.parent.analyze_folder(directory)
            self.parent.tabs.setCurrentIndex(1)  # Basculer vers l'onglet "Analysis"

    def load_readme_content(self):
        readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as file:
                content = file.read()
                self.readme_display.setPlainText(content)
        else:
            self.readme_display.setPlainText("README.md file not found.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('images/favicon.ico'))

        # Initialiser les gestionnaires
        self.db_manager = DatabaseManager()
        self.selected_directory = None

        # Création des onglets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Ajouter la page d'accueil
        self.home_page = HomePage(self)
        self.tabs.addTab(self.home_page, "Home")

        # Placeholder pour la page d'analyse
        self.analysis_page = QWidget()
        self.tabs.addTab(self.analysis_page, "Analysis")
        
        # Ajouter la vue en mosaïque (Grid View)
        self.grid_view_page = ThumbnailViewWidget(self)
        self.tabs.addTab(self.grid_view_page, "Grid View")

        # Ajouter le widget de la carte
        self.map_view_page = MapViewWidget(self)
        self.tabs.addTab(self.map_view_page, "Map View")

        # Ajouter le widget de tri et filtrage
        self.sorting_filtering_widget = SortingFilteringWidget(self)
        self.tabs.addTab(self.sorting_filtering_widget, "Sorting & Filtering")

        # Ajouter le widget d'exportation de données
        self.export_data_widget = ExportDataWidget(self, data=[])
        self.tabs.addTab(self.export_data_widget, "Export Data")
        
        # Ajouter le widget d'amélioration de l'interface utilisateur
        self.ui_enhancements_widget = UIEnhancementsWidget(self)
        self.tabs.addTab(self.ui_enhancements_widget, "UI Enhancements")

        # Connecter les changements d'onglet
        self.tabs.currentChanged.connect(self.on_tab_change)
        
    def analyze_folder(self, directory):
        self.selected_directory = directory
        if directory:
            self.db_manager.populate_database(directory)
            
            # Initialiser et mettre à jour la page d'analyse
            self.analysis_page = AnalysisPage(self)
            self.tabs.removeTab(1)  # Supprimer le placeholder "Analysis"
            self.tabs.insertTab(1, self.analysis_page, "Analysis")
            
            # Synchroniser les folders entre DataVisualizer et ThumbnailViewWidget
            data_loader = DataLoader(self.db_manager.db_path)  # Crée une instance de DataLoader
            folders_data = data_loader.get_folders()  # Utilise DataLoader pour obtenir les dossiers
            self.grid_view_page.set_folders(folders_data['folders_with_images'])

            # Connecter les signaux pour la mise à jour de la vue en mosaïque
            self.analysis_page.data_visualizer.folder_filter.currentIndexChanged.connect(self.grid_view_page.folder_filter_combo.setCurrentIndex)
            self.grid_view_page.folder_filter_combo.currentIndexChanged.connect(self.analysis_page.data_visualizer.folder_filter.setCurrentIndex)
            
            # Initialiser la vue en mosaïque
            self.update_grid_view()
        else:
            QMessageBox.warning(self, "Erreur", "Aucun répertoire n'a été sélectionné.")

    def update_grid_view(self, selected_folder="All"):
        # Mise à jour des images affichées dans la vue en mosaïque
        data_loader = DataLoader(self.db_manager.db_path)  # Crée une instance de DataLoader
        folders_data = data_loader.get_folders()  # Utilise DataLoader pour obtenir les dossiers
        if selected_folder != "All" and selected_folder in folders_data['folder_images']:
            selected_folder = selected_folder.replace('\\','/')
            selected_images = folders_data['folder_images'][selected_folder]
            self.grid_view_page.display_thumbnails(selected_images)
        else:
            if selected_folder == "All":
                self.grid_view_page.display_thumbnails(folders_data['all_images'])
            else:
                self.grid_view_page.display_thumbnails([])

    def update_map_view(self):
        gps_data = self.get_images_with_gps(self.db_manager.db_path)
        map_object = self.create_map_with_gps_data(gps_data)
        if map_object:
            self.map_view_page.load_map(map_object)

    def parse_gps_info(self, gps_info):
        """
        Parse the GPS information string to extract latitude and longitude.
        """
        # Regex patterns to match latitude and longitude
        lat_pattern = re.compile(r'Latitude: ([\d.]+) ([NS])')
        lon_pattern = re.compile(r'Longitude: ([\d.]+) ([EW])')

        # Find latitude
        lat_match = lat_pattern.search(gps_info)
        if lat_match:
            latitude = float(lat_match.group(1))
            if lat_match.group(2) == 'S':
                latitude = -latitude  # Convert to negative if South

        # Find longitude
        lon_match = lon_pattern.search(gps_info)
        if lon_match:
            longitude = float(lon_match.group(1))
            if lon_match.group(2) == 'W':
                longitude = -longitude  # Convert to negative if West

        return latitude, longitude

    def get_images_with_gps(self, database_path):
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Query to select the image path and GPS info
        query = "SELECT folder_path, filename, gps_info FROM photos WHERE gps_info IS NOT NULL AND gps_info != 'Latitude: 0.0 Unknown, Longitude: 0.0 Unknown'"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        images_with_gps = []
        for folder_path, filename, gps_info in results:
            latitude, longitude = self.parse_gps_info(gps_info)
            image_path = f"{folder_path}/{filename}"
            images_with_gps.append((image_path, latitude, longitude))
        
        return images_with_gps

    def create_map_with_gps_data(self, gps_data):
        if not gps_data:
            return None

        # On suppose que gps_data est une liste de tuples (image_path, latitude, longitude)
        coordinates = [(lat, lon) for _, lat, lon in gps_data if lat and lon]

        if not coordinates:
            return None

        avg_lat = sum(lat for lat, lon in coordinates) / len(coordinates)
        avg_lon = sum(lon for lat, lon in coordinates) / len(coordinates)

        map_object = folium.Map(location=[avg_lat, avg_lon], zoom_start=2)

        for image_path, lat, lon in gps_data:
            if lat and lon:  # Assurez-vous que latitude et longitude sont valides
                folium.Marker(
                    location=[lat, lon],
                    popup=f"<img src='{image_path}' width='100'>",
                    tooltip=image_path
                ).add_to(map_object)

        return map_object

    def on_tab_change(self, index):
        if self.tabs.tabText(index) == "Map View":
            self.update_map_view()

class AnalysisPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.data_visualizer = DataVisualizer(self.parent.db_manager.db_path, self.parent.selected_directory)
        layout.addWidget(self.data_visualizer)

        self.setLayout(layout)

    def apply_sorting_filtering(self, sort_by, filter_by):
        self.data_visualizer.apply_sorting_filtering(sort_by, filter_by)

    def apply_graph_style(self, style):
        self.data_visualizer.apply_graph_style(style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
