from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt

class UIEnhancementsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Dark Mode Toggle
        self.dark_mode_button = QPushButton("Toggle Dark Mode", self)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

        # Graph Style Options
        self.graph_style_combo = QComboBox(self)
        self.graph_style_combo.addItems(["Default", "Dark Background", "Custom Colors"])

        # Apply Graph Style Button
        self.apply_graph_style_button = QPushButton("Apply Graph Style", self)
        self.apply_graph_style_button.clicked.connect(self.apply_graph_style)

        # Add widgets to layout
        layout.addWidget(self.dark_mode_button)
        layout.addWidget(self.graph_style_combo)
        layout.addWidget(self.apply_graph_style_button)

        self.setLayout(layout)

    def toggle_dark_mode(self):
        if self.parent().styleSheet() == "":
            self.parent().setStyleSheet("background-color: #2e2e2e; color: #ffffff;")
        else:
            self.parent().setStyleSheet("")

    def apply_graph_style(self):
        style = self.graph_style_combo.currentText()
        # Implement graph style change based on the selection
        self.parent().apply_graph_style(style)
