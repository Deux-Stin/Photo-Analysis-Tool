# map_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapViewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

    def load_map(self, map_object):
        map_html = map_object._repr_html_()  # Obtenir le HTML de la carte Folium
        self.web_view.setHtml(map_html)
