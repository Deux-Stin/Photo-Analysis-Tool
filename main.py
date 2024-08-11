import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QStackedWidget
import pyqtgraph as pg  # Importer pyqtgraph pour PlotWidget

# Importer les classes personnalisées
from scripts.photo_filter import PhotoFilter
from scripts.data_visualizer import DataVisualizer
from scripts.exif_manager import ExifManager
from scripts.database_manager import DatabaseManager

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.folder_button = QPushButton("Select Folder to Analyze", self)
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        self.total_photos_label = QLabel("Total Photos: 0", self)
        layout.addWidget(self.total_photos_label)

        self.setLayout(layout)

    def select_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        directory = directory.replace("/", "\\")
        if directory:
            self.parent.analyze_folder(directory)
            self.parent.stacked_widget.setCurrentIndex(1)


class AnalysisPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.data_visualizer = DataVisualizer(self.parent.db_manager.db_path, self)
        layout.addWidget(self.data_visualizer)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Photo Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Initialiser les gestionnaires
        self.db_manager = DatabaseManager()
        self.exif_manager = ExifManager()
        self.photo_filter = PhotoFilter(self.db_manager.db_path)  # Passer le chemin de la DB

        self.home_page = HomePage(self)
        self.analysis_page = AnalysisPage(self)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.analysis_page)

        # Initialiser data_visualizer après l'initialisation de analysis_page
        self.data_visualizer = self.analysis_page.data_visualizer
    
    def analyze_folder(self, directory):
        self.db_manager.populate_database(directory)
        
        # Utiliser une méthode existante pour obtenir les données des photos
        all_photos = self.db_manager.get_folders(directory)['all_images']
        self.photo_filter = PhotoFilter(self.db_manager.db_path)  # Réinitialiser avec le bon chemin
        filtered_photos = self.photo_filter.get_folders_with_images(directory)
        
        # Afficher le nombre total de photos
        self.home_page.total_photos_label.setText(f"Total Photos: {len(all_photos)}")
        
        # Mettre à jour les graphiques
        self.data_visualizer.update_plot()

# Lancer l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
