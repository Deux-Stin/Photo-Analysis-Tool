from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
import sys
from test_simple import ComboBoxWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Duplicate Widget with ComboBox Example")

        # Création du widget principal et du QTabWidget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.tab_widget = QTabWidget()
        
        # Créer et ajouter le premier widget
        self.widget1 = ComboBoxWidget()
        self.tab_widget.addTab(self.widget1, "Tab 1")
        
        # Dupliquer le widget et ajouter à un nouvel onglet
        self.widget2 = ComboBoxWidget()
        self.tab_widget.addTab(self.widget2, "Tab 2")
        
        # Synchroniser les listes déroulantes entre les widgets
        self.sync_combo_boxes([self.widget1, self.widget2])
        
        # Mise en place du layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(layout)

    def sync_combo_boxes(self, widgets):
        """ Synchroniser les listes déroulantes entre les widgets """
        for widget in widgets:
            widget.combo_box.currentIndexChanged.connect(self.on_combobox_index_changed)
    
    def on_combobox_index_changed(self, index):
        """ Gérer la synchronisation des sélections """
        sender = self.sender()  # Le widget qui a envoyé le signal
        selected_text = sender.currentText()

        # Mettre à jour toutes les autres ComboBox
        for widget in self.findChildren(ComboBoxWidget):
            if widget.combo_box != sender:
                widget.combo_box.setCurrentText(selected_text)

# Création de l'application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
