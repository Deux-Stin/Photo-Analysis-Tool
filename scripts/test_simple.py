from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel

class ComboBoxWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Select an item")
        self.combo_box = QComboBox()
        
        # Ajouter quelques éléments à la liste déroulante
        self.combo_box.addItems(["Item 1", "Item 2", "Item 3"])
        
        # Connecter le changement de sélection à une méthode de mise à jour
        self.combo_box.currentIndexChanged.connect(self.update_label)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)
        self.setLayout(self.layout)
    
    def update_label(self):
        selected_item = self.combo_box.currentText()
        self.label.setText(f"Selected: {selected_item}")
