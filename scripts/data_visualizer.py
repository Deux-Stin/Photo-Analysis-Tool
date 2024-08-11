import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox
from datetime import datetime
import matplotlib.dates as mdates  # Pour la conversion des dates
import sqlite3  # Supposons que vous utilisez SQLite

class DataVisualizer(QWidget):
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Initialiser le PlotWidget ici
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        # Créer les boutons pour changer le type de graphique
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Line Plot", "Bar Graph"])
        self.graph_type_combo.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(self.graph_type_combo)

        # Créer les boutons pour basculer entre date et heure
        self.time_format_combo = QComboBox()
        self.time_format_combo.addItems(["Date", "Hour"])
        self.time_format_combo.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(self.time_format_combo)

        self.setLayout(layout)

    def load_data(self):
        # Connexion à la base de données
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Exécuter une requête pour obtenir les données des photos
        query = '''
            SELECT date_taken
            FROM photos
        '''
        cursor.execute(query)
        rows = cursor.fetchall()

        # Fermer la connexion
        conn.close()

        # Extraire les dates et les transformer en format approprié
        self.dates = [row[0] for row in rows]
        self.counts = [self.dates.count(date) for date in self.dates]

        # Convertir les dates en timestamps
        date_format = "%Y:%m:%d %H:%M:%S"
        self.dates = [datetime.strptime(date, date_format).strftime('%d-%m-%Y') for date in self.dates]
        self.timestamps = [mdates.date2num(datetime.strptime(date, '%d-%m-%Y')) for date in self.dates]

    def update_plot(self):
        self.plot_widget.clear()
        
        # Obtenir le type de graphique sélectionné
        graph_type = self.graph_type_combo.currentText()
        
        # Obtenir le format de temps sélectionné
        time_format = self.time_format_combo.currentText()
        
        # Mettre à jour le graphique
        if graph_type == "Line Plot":
            self.plot_widget.plot(x=self.timestamps, y=self.counts, pen='b', symbol='o', symbolBrush='r')
        elif graph_type == "Bar Graph":
            bar_width = 0.1
            self.plot_widget.addItem(pg.BarGraphItem(x=self.timestamps, height=self.counts, width=bar_width, brush='b'))

        # Configurer les axes
        self.plot_widget.getAxis('bottom').setLabel('Date' if time_format == "Date" else 'Hour')

        if time_format == "Date":
            ticks = [ (timestamp, date) for timestamp, date in zip(self.timestamps, self.dates) ]
            self.plot_widget.getAxis('bottom').setTicks([ticks])
        elif time_format == "Hour":
            # Assurez-vous que vous avez un format d'heure approprié
            # Par exemple, en convertissant l'heure en format '%H:%M'
            self.plot_widget.getAxis('bottom').setTicks([ (ts, datetime.fromtimestamp(ts).strftime('%H:%M')) for ts in self.timestamps ])
