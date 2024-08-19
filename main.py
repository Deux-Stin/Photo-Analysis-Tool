import sys
<<<<<<< HEAD
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QFileDialog, QPushButton, QComboBox, QTabWidget, QMessageBox
=======
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QFileDialog, QPushButton, QComboBox
>>>>>>> f8c319bfb1144cdeb962d32391ab0397e9996d80
from scripts.data_visualizer import DataVisualizer
from scripts.database_manager import DatabaseManager

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.folder_button = QPushButton("Select Folder to Analyze", self)
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        self.setLayout(layout)

    def select_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        directory = directory.replace("/", "\\")
        if directory:
            self.parent.analyze_folder(directory)
            self.parent.stacked_widget.setCurrentIndex(1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
<<<<<<< HEAD
=======

>>>>>>> f8c319bfb1144cdeb962d32391ab0397e9996d80
        self.setWindowTitle("Photo Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Initialiser les gestionnaires
        self.db_manager = DatabaseManager()
<<<<<<< HEAD
        self.selected_directory = None  # Ajouter cette ligne
=======
>>>>>>> f8c319bfb1144cdeb962d32391ab0397e9996d80

        # StackedWidget pour basculer entre les pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

<<<<<<< HEAD
        # Ajouter la page d'accueil
        self.home_page = HomePage(self)
        self.stacked_widget.addWidget(self.home_page)

    def analyze_folder(self, directory):
        self.selected_directory = directory  # Enregistrer le répertoire sélectionné
        if directory:  # Vérifiez si directory n'est pas None
            self.db_manager.populate_database(directory)
            self.analysis_page = AnalysisPage(self)  # Initialisez AnalysisPage après avoir défini selected_directory
            self.stacked_widget.addWidget(self.analysis_page)
            self.stacked_widget.setCurrentWidget(self.analysis_page)
        else:
            # Gérer le cas où aucun répertoire n'a été sélectionné
            QMessageBox.warning(self, "Erreur", "Aucun répertoire n'a été sélectionné.")

=======
        # Ajouter la page d'accueil et la page d'analyse
        self.home_page = HomePage(self)
        self.analysis_page = AnalysisPage(self)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.analysis_page)

    def analyze_folder(self, directory):
        self.db_manager.populate_database(directory)
        self.analysis_page.data_visualizer.load_data()
>>>>>>> f8c319bfb1144cdeb962d32391ab0397e9996d80

class AnalysisPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

<<<<<<< HEAD
        # Passer le chemin du dossier sélectionné à DataVisualizer
        self.data_visualizer = DataVisualizer(self.parent.db_manager.db_path, self.parent.selected_directory)
=======

        # Visualisation des données (la gestion du 1/3, 2/3 est dans DataVisualizer)
        self.data_visualizer = DataVisualizer(self.parent.db_manager.db_path)
>>>>>>> f8c319bfb1144cdeb962d32391ab0397e9996d80
        layout.addWidget(self.data_visualizer)

        self.setLayout(layout)

    def update_plot(self):
        self.data_visualizer.set_plot_type(self.graph_type_combo.currentText())
        self.data_visualizer.set_info_type(self.info_type_combo.currentText())
        self.data_visualizer.update_plot()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
