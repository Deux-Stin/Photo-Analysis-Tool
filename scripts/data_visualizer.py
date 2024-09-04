from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QComboBox, QLabel, QHBoxLayout, QCheckBox,
    QSlider, QDateEdit, QGroupBox, QFormLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
import pyqtgraph as pg
import datetime
import sqlite3
import numpy as np
from scripts.data_loader import DataLoader  
from fractions import Fraction

class RangeSlider(QWidget):
    def __init__(self, min_value, max_value, default_min, default_max, label, factor=1):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.default_min = default_min
        self.default_max = default_max
        self.label_name = label
        self.factor = factor  # Added factor for floating point conversion

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Create a horizontal layout for min and max values
        h_layout = QHBoxLayout()
        
        self.slider_min = QSlider(Qt.Horizontal)
        self.slider_min.setRange(int(self.min_value * self.factor), int(self.max_value * self.factor))
        self.slider_min.setValue(int(self.default_min * self.factor))
        self.slider_min.setTickInterval(1)
        self.slider_min.setTickPosition(QSlider.TicksBelow)
        
        self.slider_max = QSlider(Qt.Horizontal)
        self.slider_max.setRange(int(self.min_value * self.factor), int(self.max_value * self.factor))
        self.slider_max.setValue(int(self.default_max * self.factor))
        self.slider_max.setTickInterval(1)
        self.slider_max.setTickPosition(QSlider.TicksBelow)

        # Labels for min and max values
        self.label_min = QLabel(str(self.default_min))
        self.label_max = QLabel(str(self.default_max))
        
        h_layout.addWidget(self.label_min)
        h_layout.addWidget(self.slider_min)
        h_layout.addWidget(self.slider_max)
        h_layout.addWidget(self.label_max)

        if self.label_name == 'Aperture':
            self.label_range = QLabel(f"max - min:") #  {self.min_value} - {self.max_value}
        else:
            self.label_range = QLabel(f"min - max:") #  {self.min_value} - {self.max_value}
        
        layout.addWidget(self.label_range)
        layout.addLayout(h_layout)

        self.setLayout(layout)

        # Connect sliders to label updates
        self.slider_min.valueChanged.connect(self.updateLabel)
        self.slider_max.valueChanged.connect(self.updateLabel)

    def updateLabel(self):
        min_value = self.slider_min.value() / self.factor
        max_value = self.slider_max.value() / self.factor
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        self.slider_min.setValue(int(min_value * self.factor))
        self.slider_max.setValue(int(max_value * self.factor))
        self.label_min.setText(f"{min_value:.1f}")
        self.label_max.setText(f"{max_value:.1f}")

        if self.label_name == 'Aperture':
            self.label_range.setText(f"max - min:") #  {self.min_value} - {self.max_value}
        else:
            self.label_range.setText(f"min - max:") #  {self.min_value} - {self.max_value}

class DataVisualizer(QWidget):
    def __init__(self, db_path, directory):
        super().__init__()
        self.db_path = db_path
        self.directory = directory
        self.data_loader = DataLoader(db_path)
        self.param_ranges = self.data_loader.get_parameter_ranges()

        self.init_ui()
        self.load_folders()
        # self.load_data()
        self.update_plot()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.folder_filter = QComboBox(self)
        self.folder_filter.addItem("All")
        main_layout.addWidget(self.folder_filter)

        content_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        # Filters section
        self.filters_group = QGroupBox("Filters", self)
        filters_layout = QFormLayout()

        # Brand Filter
        filters_layout.addRow(QLabel("Brands:"))
        self.brand_filter_box = QHBoxLayout()
        self.brand_filters = {}  # Dictionnaire pour stocker les QCheckBox
        filters_layout.addRow(self.brand_filter_box)

        # Charger les marques depuis la base de données
        self.load_brands()

        # Date Filter
        self.date_filter_from = QDateEdit(self)
        self.date_filter_to = QDateEdit(self)
        self.date_filter_from.setCalendarPopup(True)
        self.date_filter_to.setCalendarPopup(True)

        # Set initial date ranges from database
        oldest_date, newest_date = self.param_ranges['date_range']
        self.date_filter_from.setDate(QDate.fromString(oldest_date, "yyyy-MM-dd"))
        self.date_filter_to.setDate(QDate.fromString(newest_date, "yyyy-MM-dd"))

        filters_layout.addRow("Date From:", self.date_filter_from)
        filters_layout.addRow("Date To:", self.date_filter_to)

        # Configuration des sliders d'ouverture avec facteur de conversion
        self.factor = 10  # Conversion factor for aperture

        # Configuration des sliders d'ouverture
        min_aperture = float(self.param_ranges['aperture'][0])
        max_aperture = float(self.param_ranges['aperture'][1])

        # Utilisation de RangeSlider avec les valeurs d'ouverture
        self.aperture_filter = RangeSlider(
            min_aperture,  # min aperture
            max_aperture,  # max aperture
            min_aperture,  # default min aperture
            max_aperture,  # default max aperture
            "Aperture",
            factor=self.factor  # pass factor to the slider
        )
        filters_layout.addRow("Aperture:", self.aperture_filter)

        # Iso Filter
        self.iso_filter = RangeSlider(
            int(self.param_ranges['iso'][0]),  # min 
            int(self.param_ranges['iso'][1]),  # max 
            int(self.param_ranges['iso'][0]),  # default min 
            int(self.param_ranges['iso'][1]),  # default max
            "Iso"
        )
        filters_layout.addRow("Iso:", self.iso_filter)

        # Shutter Speed Filter
        self.shutter_speed_filter = RangeSlider(
            int(1 / self.param_ranges['shutter_speed'][1]),  # min shutter speed as denominator
            int(1 / self.param_ranges['shutter_speed'][0]),  # max shutter speed as denominator
            int(1 / self.param_ranges['shutter_speed'][1]),  # default min shutter speed as denominator
            int(1 / self.param_ranges['shutter_speed'][0]),  # default max shutter speed as denominator
            "Shutter Speed"
        )
        filters_layout.addRow("Shutter Speed:", self.shutter_speed_filter)

        # Focal Length Filter
        self.focal_length_filter = RangeSlider(
            int(self.param_ranges['focal_length'][0]),  # min focal length
            int(self.param_ranges['focal_length'][1]),  # max focal length
            int(self.param_ranges['focal_length'][0]),  # default min focal length
            int(self.param_ranges['focal_length'][1]),  # default max focal length
            "Focal Length"
        )
        filters_layout.addRow("Focal Length:", self.focal_length_filter)

        self.filters_group.setLayout(filters_layout)
        left_layout.addWidget(self.filters_group)

        # Display and Graph Type
        self.display_type = QComboBox(self)
        self.display_type.addItem("Date Taken")
        self.display_type.addItem("Focal length in 35mm")
        self.display_type.addItem("Iso")
        self.display_type.addItem("Aperture")
        self.display_type.addItem("Shutter Speed")
        self.display_type.addItem("Brand Name")
        left_layout.addWidget(self.display_type)

        self.graph_type = QComboBox(self)
        self.graph_type.addItem("Bar Graph")
        self.graph_type.addItem("Line Graph")
        left_layout.addWidget(self.graph_type)

        self.total_photos_label = QLabel("Total Photos: 0", self)
        left_layout.addWidget(self.total_photos_label)

        right_layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget(background='w')
        right_layout.addWidget(self.plot_widget)

        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        main_layout.addLayout(content_layout)

        # Connect signals for the filters
        self.graph_type.currentIndexChanged.connect(self.update_plot)
        self.display_type.currentIndexChanged.connect(self.update_plot)
        self.folder_filter.currentIndexChanged.connect(self.update_brands_and_plot)

        self.date_filter_from.dateChanged.connect(self.update_plot)
        self.date_filter_to.dateChanged.connect(self.update_plot)
        self.aperture_filter.slider_min.valueChanged.connect(self.update_plot)
        self.aperture_filter.slider_max.valueChanged.connect(self.update_plot)
        self.shutter_speed_filter.slider_min.valueChanged.connect(self.update_plot)
        self.shutter_speed_filter.slider_max.valueChanged.connect(self.update_plot)
        self.focal_length_filter.slider_min.valueChanged.connect(self.update_plot)
        self.focal_length_filter.slider_max.valueChanged.connect(self.update_plot)
        self.iso_filter.slider_min.valueChanged.connect(self.update_plot)
        self.iso_filter.slider_max.valueChanged.connect(self.update_plot)
        
        # Connectez les signaux des cases à cocher à la méthode update_plot
        for checkbox in self.brand_filters.values():
            checkbox.stateChanged.connect(self.update_plot)

        self.setLayout(main_layout)

    def load_folders(self):
        data = self.data_loader.get_folders()
        self.folder_filter.addItems(data['folders_with_images'])
        return data
    
    def load_brands(self, folder=None):
        # Efface les cases à cocher existantes
        for i in reversed(range(self.brand_filter_box.count())):
            widget = self.brand_filter_box.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Charge les marques depuis la base de données en fonction du dossier
        brands = self.data_loader.get_brands(folder)
        self.brand_filters.clear()

        for brand in brands:
            checkbox = QCheckBox(brand)
            self.brand_filters[brand] = checkbox
            self.brand_filter_box.addWidget(checkbox)
            checkbox.setChecked(False)  # Toutes les cases décochées par défaut
            checkbox.stateChanged.connect(self.update_plot)

    def update_brands_and_plot(self):
        selected_folder = self.folder_filter.currentText()
        if selected_folder == "All":
            self.load_brands()  # Charger toutes les marques
        else:
            self.load_brands(folder=selected_folder)  # Charger les marques pour le dossier sélectionné

        self.update_plot()

    def update_plot(self):
        display_type = self.display_type.currentText()
        graph_type = self.graph_type.currentText()
        selected_folder = self.folder_filter.currentText()
        selected_brands = [brand for brand, checkbox in self.brand_filters.items() if checkbox.isChecked()]

        # Si aucune marque n'est cochée ou si toutes les cases sont cochées, on affiche toutes les marques
        if not selected_brands or len(selected_brands) == len(self.brand_filters):
            selected_brands = list(self.brand_filters.keys())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Correspondance des types d'affichage avec les colonnes de la base de données
            column_mapping = {
                "Date Taken": "date_taken",
                "Focal length in 35mm": "focal_length_in_35mm",
                "Iso": "iso",
                "Aperture": "aperture",
                "Shutter Speed": "shutter_speed",
                "Brand Name": "brand_name"
            }
            
            # Validation du type d'affichage
            if display_type not in column_mapping:
                print("Invalid display type selected.")
                self.plot_widget.clear()
                return
            
            column_name = column_mapping[display_type]
            base_query = f"SELECT {column_name}, COUNT(*) FROM photos WHERE 1=1"
            params = []

            # Application du filtre de dossier
            if selected_folder != "All":
                base_query += " AND folder_path = ?"
                params.append(selected_folder)

            # Application du filtre de marques
            if selected_brands:
                placeholders = ', '.join('?' for _ in selected_brands)
                base_query += f" AND brand_name IN ({placeholders})"
                params.extend(selected_brands)
            
            # Filtre par date
            min_date = self.date_filter_from.date().toString("yyyy-MM-dd")
            max_date = self.date_filter_to.date().toString("yyyy-MM-dd")

            max_date += " 23:59:59" #test
            base_query += " AND date_taken BETWEEN ? AND ?"
            params.extend([min_date, max_date])

            # Filtre par ouverture
            # Lors de l'utilisation des valeurs des sliders, divisez par le facteur pour obtenir des valeurs flottantes
            min_aperture = self.aperture_filter.slider_min.value() / self.factor
            max_aperture = self.aperture_filter.slider_max.value() / self.factor

            # Utilisez <= et >= pour les filtres exacts
            base_query += " AND aperture >= ? AND aperture <= ?"
            params.extend([min_aperture, max_aperture])

            # Filtre par ISO
            min_iso = self.iso_filter.slider_min.value()
            max_iso = self.iso_filter.slider_max.value()
            base_query += " AND iso BETWEEN ? AND ?"
            params.extend([min_iso, max_iso])

            # Filtre par vitesse d'obturation
            min_shutter_speed = 1 / self.shutter_speed_filter.slider_max.value()
            max_shutter_speed = 1 / self.shutter_speed_filter.slider_min.value()
            base_query += " AND shutter_speed BETWEEN ? AND ?"
            params.extend([min_shutter_speed, max_shutter_speed])

            # Filtre par longueur focale
            min_focal_length = self.focal_length_filter.slider_min.value()
            max_focal_length = self.focal_length_filter.slider_max.value()
            base_query += " AND focal_length_in_35mm BETWEEN ? AND ?"
            params.extend([min_focal_length, max_focal_length])

            # Finalisation de la requête
            base_query += f" GROUP BY {column_name} ORDER BY {column_name}"
                
            # Application de la requête
            cursor.execute(base_query, params)
            data = cursor.fetchall()

            # Mise à jour du dénombrement
            self.total_photos_label.setText(f"Total Photos: {sum(x[1] for x in data)}")

            if not data:
                print("No data found for the selected criteria.")
                print(base_query)
                self.plot_widget.clear()
                return

            x_values = []
            y_values = []

            # Traitement des données en fonction du type d'affichage
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

            # Vidage de la zone de graphique avant d'ajouter de nouvelles données
            self.plot_widget.clear()

            # Affichage des données selon le type de graphique sélectionné
            if graph_type == "Bar Graph":
                bg = pg.BarGraphItem(x=np.arange(len(x_values)), height=y_values, width=0.6, brush='b')
                self.plot_widget.addItem(bg)
            elif graph_type == "Line Graph":
                self.plot_widget.plot(y=y_values, x=np.arange(len(x_values)), symbol='o', pen='b')

            # Affichage des valeurs de survol
            self.add_hover_values(x_values, y_values)

            # Mise à jour des ticks des axes
            ticks = [(i, x) for i, x in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])


    def add_hover_values(self, x_values, y_values):
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            text = pg.TextItem(f"{y}", anchor=(0.5, 1), color='k')
            text.setPos(i, y)
            self.plot_widget.addItem(text)

