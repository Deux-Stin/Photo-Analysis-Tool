import pyqtgraph as pg
from fractions import Fraction
import numpy as np
import datetime

class PlotUpdater:
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget

    def update_plot(self, display_type, graph_type, data):
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
                shutter_speed_value = float(item[0])
                fraction_value = Fraction(1, shutter_speed_value).limit_denominator(1000)
                x_values.append(str(fraction_value))
                y_values.append(item[1])

            ticks = [(i, str(speed)) for i, speed in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])

        elif display_type == "Aperture":
            for item in data:
                aperture_value = float(item[0])
                x_values.append(str(aperture_value))
                y_values.append(item[1])

            ticks = [(i, str(aperture)) for i, aperture in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])
        
        elif display_type == "Iso":
            for item in data:
                iso_value = float(item[0])
                x_values.append(str(iso_value))
                y_values.append(item[1])

            ticks = [(i, str(iso)) for i, iso in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])

        elif display_type == "focal_length_in_35mm":
            for item in data:
                focal_length_value = float(item[0])
                x_values.append(str(focal_length_value))
                y_values.append(item[1])

            ticks = [(i, str(focal_length)) for i, focal_length in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])
            
        elif display_type == "Brand Name":
            x_values, y_values = zip(*data)

            ticks = [(i, brand) for i, brand in enumerate(x_values)]
            self.plot_widget.getAxis('bottom').setTicks([ticks])

        x_indices = list(range(len(x_values)))

        self.plot_widget.clear()
        if graph_type == "Bar Graph":
            bg = pg.BarGraphItem(x=x_indices, height=y_values, width=0.6, brush='b')
            self.plot_widget.addItem(bg)
        elif graph_type == "Line Graph":
            self.plot_widget.plot(x_indices, y_values, pen='b', symbol='o')
