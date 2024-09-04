from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel

class SortingFilteringWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Labels
        self.sort_label = QLabel("Sort by:", self)
        self.filter_label = QLabel("Filter by:", self)

        # Sorting options
        self.sort_combo = QComboBox(self)
        self.sort_combo.addItems(["Date", "Aperture", "Shutter Speed", "Camera Model"])

        # Filtering options
        self.filter_combo = QComboBox(self)
        self.filter_combo.addItems(["All", "Specific Camera Model", "Date Range", "Aperture Range", "Shutter Speed Range"])

        # Buttons
        self.apply_button = QPushButton("Apply", self)
        self.apply_button.clicked.connect(self.apply_sort_filter)

        # Add widgets to layout
        layout.addWidget(self.sort_label)
        layout.addWidget(self.sort_combo)
        layout.addWidget(self.filter_label)
        layout.addWidget(self.filter_combo)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def apply_sort_filter(self):
        sort_by = self.sort_combo.currentText()
        filter_by = self.filter_combo.currentText()

        # Call a method to apply sorting and filtering (to be defined in main logic)
        self.parent().apply_sorting_filtering(sort_by, filter_by)
