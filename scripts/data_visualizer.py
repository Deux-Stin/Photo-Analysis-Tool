from PyQt5.QtWidgets import (
    QVBoxLayout, QWidget, QComboBox, QLabel, QHBoxLayout, QCheckBox,
    QSlider, QDateEdit, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QDate
import pyqtgraph as pg
import datetime
import sqlite3
import numpy as np
from scripts.data_loader import DataLoader  
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

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

        # Y-axis Selection
        self.y_axis_type = QComboBox(self)
        left_layout.addWidget(self.y_axis_type)
        self.update_y_options()

        # Graph type
        self.graph_type = QComboBox(self)
        self.graph_type.addItem("Bar Graph")
        self.graph_type.addItem("Line Graph")
        self.graph_type.addItem("Scatter Plot")
        left_layout.addWidget(self.graph_type)

        self.total_photos_label = QLabel("Total Photos: 0", self)
        left_layout.addWidget(self.total_photos_label)

        # Emplacement du graph
        right_layout = QVBoxLayout()

        # Matplotlib graph
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Ajout de la barre d'outils de navigation Matplotlib
        self.toolbar = NavigationToolbar(self.canvas, self)  # Barre d'outils Matplotlib
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)

        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        main_layout.addLayout(content_layout)

        # Connect signals for the filters
        self.graph_type.currentIndexChanged.connect(self.update_plot)
        self.display_type.currentIndexChanged.connect(self.update_plot)
        self.folder_filter.currentIndexChanged.connect(self.update_brands_and_plot)
        self.y_axis_type.currentIndexChanged.connect(self.update_plot)

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

        # Appel initial pour afficher un graphique
        self.update_plot()

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

    def update_y_options(self):
        selected_x = self.display_type.currentText()
        y_options = ["Date Taken", "Focal length in 35mm", "Iso", "Aperture", "Shutter Speed", "Brand Name"]

        # Supprimer la valeur sélectionnée pour X de la liste des options Y
        if selected_x in y_options:
            y_options.remove(selected_x)

        self.y_axis_type.clear()
        self.y_axis_type.addItems(y_options)

    def update_brands_and_plot(self):
        selected_folder = self.folder_filter.currentText()
        if selected_folder == "All":
            self.load_brands()  # Charger toutes les marques
        else:
            self.load_brands(folder=selected_folder)  # Charger les marques pour le dossier sélectionné

        self.update_plot()

    def update_plot(self):
        display_type = self.display_type.currentText()
        y_axis_type = self.y_axis_type.currentText()
        graph_type = self.graph_type.currentText()
        selected_folder = self.folder_filter.currentText()
        selected_brands = [brand for brand, checkbox in self.brand_filters.items() if checkbox.isChecked()]

        if not selected_brands or len(selected_brands) == len(self.brand_filters):
            selected_brands = list(self.brand_filters.keys())

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            column_mapping = {
                "Date Taken": "date_taken",
                "Focal length in 35mm": "focal_length_in_35mm",
                "Iso": "iso",
                "Aperture": "aperture",
                "Shutter Speed": "shutter_speed",
                "Brand Name": "brand_name"
            }

            if display_type not in column_mapping or y_axis_type not in column_mapping:
                self.ax.clear()
                self.canvas.draw()
                return

            x_column = column_mapping[display_type]
            y_column = column_mapping[y_axis_type]

            base_query = f"SELECT {x_column}, {y_column} FROM photos WHERE 1=1"
            params = []

            if selected_folder != "All":
                base_query += " AND folder_path = ?"
                params.append(selected_folder)

            if selected_brands:
                placeholders = ', '.join('?' for _ in selected_brands)
                base_query += f" AND brand_name IN ({placeholders})"
                params.extend(selected_brands)

            min_date = self.date_filter_from.date().toString("yyyy-MM-dd")
            max_date = self.date_filter_to.date().toString("yyyy-MM-dd") + " 23:59:59"
            base_query += " AND date_taken BETWEEN ? AND ?"
            params.extend([min_date, max_date])

            min_aperture = self.aperture_filter.slider_min.value() / self.factor
            max_aperture = self.aperture_filter.slider_max.value() / self.factor
            base_query += " AND aperture >= ? AND aperture <= ?"
            params.extend([min_aperture, max_aperture])

            min_iso = self.iso_filter.slider_min.value()
            max_iso = self.iso_filter.slider_max.value()
            base_query += " AND iso BETWEEN ? AND ?"
            params.extend([min_iso, max_iso])

            min_shutter_speed = 1 / self.shutter_speed_filter.slider_max.value()
            max_shutter_speed = 1 / self.shutter_speed_filter.slider_min.value()
            base_query += " AND shutter_speed BETWEEN ? AND ?"
            params.extend([min_shutter_speed, max_shutter_speed])

            min_focal_length = self.focal_length_filter.slider_min.value()
            max_focal_length = self.focal_length_filter.slider_max.value()
            base_query += " AND focal_length_in_35mm BETWEEN ? AND ?"
            params.extend([min_focal_length, max_focal_length])

            base_query += f" ORDER BY {x_column}, {y_column}"
            cursor.execute(base_query, params)
            data = cursor.fetchall()

            if not data:
                self.ax.clear()
                self.ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center')
                self.canvas.draw()
                return

            x_values = []
            y_values = []
            x_ticks = []

            counts = len(data)
            self.total_photos_label.setText(f"Total Photos: {counts}")

            if display_type == "Date Taken":
                for i, (x_value, y_value) in enumerate(data):
                    try:
                        date = datetime.datetime.strptime(x_value, "%Y-%m-%d").date()
                        x_values.append(date)
                        y_values.append(y_value)
                        x_ticks.append(date.strftime('%Y-%m-%d'))
                    except ValueError:
                        print(f"Invalid date format: {x_value}")
                        continue
            elif display_type == "Brand Name":
                unique_x_values = {v[0] for v in data}
                x_mapping = {val: i for i, val in enumerate(unique_x_values)}
                for x_value, y_value in data:
                    x_values.append(x_mapping[x_value])
                    y_values.append(y_value)
                    x_ticks.append(x_value)
            else:
                for x_value, y_value in data:
                    x_values.append(float(x_value))
                    y_values.append(y_value)

            self.ax.clear()  # Clear the previous plot

            if graph_type == "Scatter Plot":
                self.ax.scatter(x_values, y_values, color='red')
            elif graph_type == "Bar Graph":
                self.ax.bar(x_values, y_values, color='blue')
            elif graph_type == "Line Graph":
                self.ax.plot(x_values, y_values, marker='o', color='blue')

            # Rotation des labels de l'axe X si c'est une date
            if display_type == "Date Taken":
                self.ax.set_xticks(x_values)
                self.ax.set_xticklabels(x_ticks, rotation=90)

            self.ax.set_xlabel(display_type)
            self.ax.set_ylabel(y_axis_type)
            self.figure.tight_layout()
            self.canvas.draw()  # Redessiner le canvas

            
    def add_hover_values(self, x_values, y_values):
        # Réinitialiser les éléments de texte
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            text = pg.TextItem(f"{y}", anchor=(0.5, 1), color='k')
            # Placer le texte directement sur les valeurs réelles de x et y
            text.setPos(x, y)
            self.plot_widget.addItem(text)
