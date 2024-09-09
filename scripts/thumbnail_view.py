import os
import rawpy
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy, QScrollArea, QSpacerItem, QSizePolicy, QGridLayout, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
import pillow_heif
from PIL import Image
from io import BytesIO

class ThumbnailViewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_paths = []  # Initialiser l'attribut image_paths
        self.init_ui()

    def init_ui(self):
        # Créer un layout principal
        self.layout = QVBoxLayout()

        # Ajouter un QComboBox pour la sélection de dossier
        self.folder_filter_combo = QComboBox(self)
        self.folder_filter_combo.addItem("All")
        self.folder_filter_combo.currentIndexChanged.connect(self.on_folder_change)
        self.layout.addWidget(self.folder_filter_combo)
        
        # Créer un QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Créer un widget conteneur pour le QScrollArea
        self.container_widget = QWidget()
        
        # Créer un layout de grille pour les miniatures
        self.grid_layout = QGridLayout(self.container_widget)
        self.grid_layout.setSpacing(10)  # Espacement entre les éléments

        # Ajouter le layout de la grille au widget conteneur
        self.container_widget.setLayout(self.grid_layout)
        
        # Ajouter le conteneur au QScrollArea
        self.scroll_area.setWidget(self.container_widget)
        
        # Ajouter le QScrollArea au layout principal
        self.layout.addWidget(self.scroll_area)
        
        self.setLayout(self.layout)

    def set_folders(self, folders):
        # Remplir le QComboBox avec les dossiers disponibles
        self.folder_filter_combo.addItems(folders)

    def on_folder_change(self):
        # Réagir à la sélection de dossier
        selected_folder = self.folder_filter_combo.currentText()
        main_window = self.window()  # Obtenir l'instance de MainWindow
        main_window.update_grid_view(selected_folder)

    def raw_to_qpixmap(self, raw_file_path):
        with rawpy.imread(raw_file_path) as raw:
            # Convertir l'image RAW en une image RGB
            rgb_image = raw.postprocess()

            # Convertir en format compatible avec QPixmap (comme PNG)
            img = Image.fromarray(rgb_image)
            with BytesIO() as buffer:
                img.save(buffer, format="PNG")
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                return pixmap

    def display_thumbnails(self, image_paths):
        self.image_paths = image_paths
        # Filtrer les chemins d'images pour ne garder que ceux avec les extensions .jpg ou .png pour accélérer l'affichage
        self.image_paths = [path for path in image_paths if path.lower().endswith(('.jpg', '.png', 'heif', 'heic'))]

        
        # Vider le layout avant de réafficher les images
        self.clear_layout()

        # Utiliser QTimer pour attendre que le rendu soit terminé
        QTimer.singleShot(0, self.update_grid_layout)

    def clear_layout(self):
        # Nettoyer le layout avant de réafficher les images
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def update_grid_layout(self):
        # Réinitialiser le layout de grille
        self.clear_layout()
        
        container_width = self.scroll_area.viewport().width()
        thumbnail_size = 200  # 200x200 pixels
        spacing = self.grid_layout.spacing()
        
        num_columns = max(1, container_width // (thumbnail_size + spacing))
        num_rows = (len(self.image_paths) + num_columns - 1) // num_columns
        
        for i, image_path in enumerate(self.image_paths):
            label = QLabel()
            
            pixmap = None

            # Charger l'image et gérer les exceptions
            try:
                if image_path.lower().endswith(('.heic', '.heif')):
                    # Ouvrir et convertir les fichiers HEIF avec Pillow et pillow_heif
                    heif_file = pillow_heif.read_heif(image_path)
                    image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
                    with BytesIO() as buffer:
                        image.save(buffer, format="PNG")
                        pixmap = QPixmap()
                        pixmap.loadFromData(buffer.getvalue())
                else:
                    pixmap = QPixmap(image_path)
            except Exception as e:
                print(f"Thumbnail not available for this file {os.path.basename(image_path)}: {e}")
                pixmap = None

            if pixmap is None or pixmap.isNull():
                print('Thumbnail not available for this file : '+os.path.basename(image_path))

            pixmap = pixmap.scaled(thumbnail_size, thumbnail_size, aspectRatioMode=1) 
            label.setPixmap(pixmap)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            row = i // num_columns
            col = i % num_columns
            self.grid_layout.addWidget(label, row, col)

        self.update_spacers(num_columns, num_rows)


    def update_spacers(self, num_columns, num_rows):
        # Ajouter des spacers pour centrer les images
        for i in range(num_rows):
            if i < self.grid_layout.rowCount():
                row_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.grid_layout.addItem(row_spacer, i, num_columns)
        
        col_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.grid_layout.addItem(col_spacer, num_rows, 0, 1, num_columns)

    def resizeEvent(self, event):
        # Appeler update_grid_layout uniquement si image_paths est défini
        if self.image_paths:
            QTimer.singleShot(0, self.update_grid_layout)
        super().resizeEvent(event)
