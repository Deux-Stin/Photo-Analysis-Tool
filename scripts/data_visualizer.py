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
        self.directory = directory
        self.init_ui()
        self.load_folders()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.folder_filter = QComboBox(self)
        self.folder_filter.addItem("All")
        main_layout.addWidget(self.folder_filter)

        content_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        self.display_type = QComboBox(self)
        self.display_type.addItem("Date Taken")
        self.display_type.addItem("focal_length_in_35mm")
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

        self.setLayout(main_layout)

        self.graph_type.currentIndexChanged.connect(self.update_plot)
        self.display_type.currentIndexChanged.connect(self.update_plot)
        self.folder_filter.currentIndexChanged.connect(self.update_plot)

    def load_folders(self):
        data = self.get_folders()
        self.folder_filter.addItems(data['folders_with_images'])

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

        folder_images = {folder: [] for folder in folders_with_images}
        for image in all_images:
            folder = os.path.dirname(image)
            folder_images.setdefault(folder, []).append(image)

        return {
            'all_images': all_images,
            'folders_with_images': list(folders_with_images),
            'folder_images': folder_images
        }

    def load_data(self):
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

        self.data = {
            'dates': [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() for row in data if row[0] is not None],
            'counts': [row[1] for row in data if row[0] is not None]
        }

        self.total_photos_label.setText(f"Total Photos: {sum(self.data['counts'])}")

    def update_plot(self):
        display_type = self.display_type.currentText()
        graph_type = self.graph_type.currentText()
        selected_folder = self.folder_filter.currentText()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            if display_type == "Date Taken":
                query = "SELECT date_taken, COUNT(*) FROM photos WHERE date_taken != 'Unknown'"
                if selected_folder != "All":
                    query += " AND folder_path = ? GROUP BY date_taken ORDER BY date_taken"
                    cursor.execute(query, (selected_folder,))
                else:
                    query += " GROUP BY date_taken ORDER BY date_taken"
                    cursor.execute(query)

            elif display_type == "focal_length_in_35mm":
                query = "SELECT focal_length_in_35mm, COUNT(*) FROM photos"
                if selected_folder != "All":
                    query += " WHERE folder_path = ? GROUP BY focal_length_in_35mm ORDER BY focal_length_in_35mm"
                    cursor.execute(query, (selected_folder,))
                else:
                    query += " GROUP BY focal_length_in_35mm ORDER BY focal_length_in_35mm"
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

            if graph_type == "Bar Graph":
                bg = pg.BarGraphItem(x=np.arange(len(x_values)), height=y_values, width=0.6, brush='b')
                self.plot_widget.addItem(bg)
            elif graph_type == "Line Graph":
                self.plot_widget.plot(y=y_values, x=np.arange(len(x_values)), symbol='o', pen='b')

            self.add_hover_values(x_values, y_values)

            ticks = [(i, x) for i, x in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])

    def apply_sorting_filtering(self, sort_by, filter_by):
        pass

    def apply_graph_style(self, style):
        pass

    def add_hover_values(self, x_values, y_values):
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            text = pg.TextItem(f"{y}", anchor=(0.5, 1), color='k')
            text.setPos(i, y)
            self.plot_widget.addItem(text)
