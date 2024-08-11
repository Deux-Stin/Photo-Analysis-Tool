import numpy as np
import pyqtgraph as pg

class PlotManager:
    def __init__(self, plot_widget):
        if not isinstance(plot_widget, pg.PlotWidget):
            raise TypeError("plot_widget must be an instance of pg.PlotWidget")
        self.plot_widget = plot_widget

    def plot_by_date(self, photos):
        # Assurer que les photos sont des dictionnaires avec 'date_taken'
        dates = [p['date_taken'].split(' ')[0] for p in photos if p['date_taken'] != 'Unknown']
        unique_dates, counts = np.unique(dates, return_counts=True)

        # Efface la vue avant de tracer
        self.plot_widget.clear()

        # Trace les données
        self.plot_widget.plot(unique_dates, counts, stepMode=True, fillLevel=0, pen='r')

    def plot_by_hour(self, photos):
        # Assurer que les photos sont des dictionnaires avec 'hour_taken'
        hours = [int(p['hour_taken'].split(':')[0]) for p in photos if p['hour_taken'] != 'Unknown']
        counts, bins = np.histogram(hours, bins=24, range=(0, 24))
        bins = np.append(bins, bins[-1] + 1)
        
        # Efface la vue avant de tracer
        self.plot_widget.clear()

        # Trace les données
        self.plot_widget.plot(bins, np.append(counts, counts[-1]), stepMode=True, fillLevel=0, pen='g')
