import csv
from fpdf import FPDF
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog

class ExportDataWidget(QWidget):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Buttons for exporting
        self.export_csv_button = QPushButton("Export as CSV", self)
        self.export_pdf_button = QPushButton("Export as PDF", self)

        # Connect buttons to functions
        self.export_csv_button.clicked.connect(self.export_csv)
        self.export_pdf_button.clicked.connect(self.export_pdf)

        # Add widgets to layout
        layout.addWidget(self.export_csv_button)
        layout.addWidget(self.export_pdf_button)

        self.setLayout(layout)

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Aperture", "Shutter Speed", "Camera Model"])  # Example headers
                for row in self.data:
                    writer.writerow(row)

    def export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for row in self.data:
                pdf.cell(200, 10, txt=", ".join(row), ln=True)
            pdf.output(file_path)
