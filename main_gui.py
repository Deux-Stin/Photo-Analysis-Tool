import sys
import os
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog, QComboBox, QStackedWidget, QHBoxLayout
import pyqtgraph as pg
from statistics import mean
from fractions import Fraction
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
        directory = directory.replace('/','\\')
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

        self.filter_combobox = QComboBox(self)
        layout.addWidget(self.filter_combobox)
        self.filter_combobox.currentTextChanged.connect(self.update_filter)

        options_layout = QHBoxLayout()
        self.date_button = QPushButton("Display by Date", self)
        self.date_button.clicked.connect(lambda: self.update_plot('date'))
        self.hour_button = QPushButton("Display by Hour", self)
        self.hour_button.clicked.connect(lambda: self.update_plot('hour'))
        options_layout.addWidget(self.date_button)
        options_layout.addWidget(self.hour_button)
        layout.addLayout(options_layout)

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground('w')

        self.setLayout(layout)

    def update_filter(self, text):
        self.parent.apply_filter(text)

    def update_plot(self, mode):
        self.parent.update_plot_mode(mode)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Photo Statistics")
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.home_page = HomePage(self)
        self.analysis_page = AnalysisPage(self)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.analysis_page)

        self.db_manager = DatabaseManager()  # Instancier DatabaseManager ici
        self.data = []

    def analyze_folder(self, directory):
        # Utilisez DatabaseManager pour peupler la base de données
        self.db_manager.populate_database(directory)

        total_photos = self.db_manager.get_photos_count()
        self.home_page.total_photos_label.setText(f"Total Photos: {total_photos}")

        folders_data = self.db_manager.get_folders(directory)
        self.analysis_page.filter_combobox.clear()
        self.analysis_page.filter_combobox.addItem("All")

        # Récupération des images et dossiers du retour de get_folders
        # all_images = folders_data['all_images']
        folders_with_images = folders_data['folders_with_images']
        for folder in folders_with_images:
            self.analysis_page.filter_combobox.addItem(folder)

        self.load_data()

    def load_data(self):
        self.data = self.db_manager.get_photo_data("All")
        self.update_plot_mode('date')

    def apply_filter(self, filter_text):
        self.data = self.db_manager.get_photo_data(filter_text)
        self.update_plot_mode('date')

    def update_plot_mode(self, mode):
        self.analysis_page.plot_widget.clear()

        if mode == 'date':
            dates = [datetime.strptime(d[0], '%Y:%m:%d %H:%M:%S') for d in self.data if d[0] != 'Unknown']
            timestamps = [d.timestamp() for d in dates]
            counts, bins = np.histogram(timestamps, bins=30)
            
            # Ajoute un point supplémentaire pour que len(bins) == len(counts) + 1
            bins = np.append(bins, bins[-1] + (bins[-1] - bins[-2]))
            
            self.analysis_page.plot_widget.plot(bins, np.append(counts, counts[-1]), stepMode=True, fillLevel=0, brush='r')
        elif mode == 'hour':
            hours = [int(h[1].split(':')[0]) for h in self.data if h[1] != 'Unknown']
            counts, bins = np.histogram(hours, bins=24, range=(0, 24))
            
            # Ajoute un point supplémentaire pour que len(bins) == len(counts) + 1
            bins = np.append(bins, bins[-1] + 1)
            
            self.analysis_page.plot_widget.plot(bins, np.append(counts, counts[-1]), stepMode=True, fillLevel=0, brush='g')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
