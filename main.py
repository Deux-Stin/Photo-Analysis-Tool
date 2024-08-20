import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QFileDialog, QPushButton, QComboBox, QTabWidget, QMessageBox
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
        self.setWindowTitle("Photo Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Initialiser les gestionnaires
        self.db_manager = DatabaseManager()
        self.selected_directory = None  # Ajouter cette ligne

        # StackedWidget pour basculer entre les pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

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


class AnalysisPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Passer le chemin du dossier sélectionné à DataVisualizer
        self.data_visualizer = DataVisualizer(self.parent.db_manager.db_path, self.parent.selected_directory)
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
