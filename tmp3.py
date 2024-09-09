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
    def __init__(self, min_value, max_value, default_min, default_max, label):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.default_min = default_min
        self.default_max = default_max
        self.label_name = label
        self.factor = 10  # Facteur de conversion pour afficher les flottants

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Crée un layout horizontal pour les valeurs min et max
        h_layout = QHBoxLayout()
        
        # Sliders pour les valeurs min et max
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

        # Labels pour afficher les valeurs min et max
        self.label_min = QLabel(f"{self.default_min:.1f}")
        self.label_max = QLabel(f"{self.default_max:.1f}")
        
        h_layout.addWidget(self.label_min)
        h_layout.addWidget(self.slider_min)
        h_layout.addWidget(self.slider_max)
        h_layout.addWidget(self.label_max)
        
        self.label_range = QLabel(f"{self.label_name} Range: {self.default_min} - {self.default_max}")
        layout.addWidget(self.label_range)
        layout.addLayout(h_layout)

        self.setLayout(layout)

        # Connecte les sliders aux mises à jour de labels
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

        self.label_range.setText(f"{self.label_name} Range: {min_value:.1f} - {max_value:.1f}")

class DataVisualizer(QWidget):
    def __init__(self, db_path, directory):
        super().__init__()
        self.db_path = db_path
        self.directory = directory
        self.data_loader = DataLoader(db_path)
        self.param_ranges = self.data_loader.get_parameter_ranges()

        self.init_ui()
        self.load_folders()
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
        self.brand_filters = {}
        filters_layout.addRow(QLabel("Brands:"))
        self.brand_filter_box = QVBoxLayout()
        filters_layout.addRow(self.brand_filter_box)

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

        # Facteur de conversion pour les valeurs flottantes
        self.factor = 10

        # Configuration des sliders d'ouverture
        min_aperture = float(self.param_ranges['aperture'][0])
        max_aperture = float(self.param_ranges['aperture'][1])

        # Utilisation de RangeSlider avec des valeurs flottantes
        self.aperture_filter = RangeSlider(
            min_aperture,  # min aperture
            max_aperture,  # max aperture
            min_aperture,  # default min aperture
            max_aperture,  # default max aperture
            "Aperture"
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
        self.folder_filter.currentIndexChanged.connect(self.update_plot)

        self.date_filter_from.dateChanged.connect(self.update_plot)
        self.date_filter_to.dateChanged.connect(self.update_plot)
        self.aperture_filter.slider_min.valueChanged.connect(self.update_plot)
        self.aperture_filter.slider_max.valueChanged.connect(self.update_plot)
        self.shutter_speed_filter.slider_min.valueChanged.connect(self.update_plot)
        self.shutter_speed_filter.slider_max.valueChanged.connect(self.update_plot)
        self.iso_filter.slider_min.valueChanged.connect(self.update_plot)
        self.iso_filter.slider_max.valueChanged.connect(self.update_plot)
        self.focal_length_filter.slider_min.valueChanged.connect(self.update_plot)
        self.focal_length_filter.slider_max.valueChanged.connect(self.update_plot)

        self.setLayout(main_layout)

    def load_folders(self):
        # Load folders from the specified directory
        folders = self.data_loader.get_folder_names()
        for folder in folders:
            self.folder_filter.addItem(folder)

        # Load brand names from the database
        brands = self.data_loader.get_brands()
        for brand in brands:
            checkbox = QCheckBox(brand)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_plot)
            self.brand_filters[brand] = checkbox
            self.brand_filter_box.addWidget(checkbox)

        self.brand_filter_box.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

    def update_plot(self):
        selected_folder = self.folder_filter.currentText()
        selected_display_type = self.display_type.currentText()
        selected_graph_type = self.graph_type.currentText()

        date_from = self.date_filter_from.date().toPyDate()
        date_to = self.date_filter_to.date().toPyDate()

        selected_brands = [brand for brand, checkbox in self.brand_filters.items() if checkbox.isChecked()]

        aperture_min = self.aperture_filter.slider_min.value() / self.aperture_filter.factor
        aperture_max = self.aperture_filter.slider_max.value() / self.aperture_filter.factor

        shutter_speed_min = 1 / self.shutter_speed_filter.slider_max.value()
        shutter_speed_max = 1 / self.shutter_speed_filter.slider_min.value()

        iso_min = self.iso_filter.slider_min.value()
        iso_max = self.iso_filter.slider_max.value()

        focal_length_min = self.focal_length_filter.slider_min.value()
        focal_length_max = self.focal_length_filter.slider_max.value()

        # Apply filtering logic and update plot
        filtered_data = self.data_loader.filter_data(
            folder=selected_folder,
            date_from=date_from,
            date_to=date_to,
            brands=selected_brands,
            aperture_range=(aperture_min, aperture_max),
            shutter_speed_range=(shutter_speed_min, shutter_speed_max),
            iso_range=(iso_min, iso_max),
            focal_length_range=(focal_length_min, focal_length_max)
        )

        # Update the total photos label
        self.total_photos_label.setText(f"Total Photos: {len(filtered_data)}")

        # Update the plot
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

