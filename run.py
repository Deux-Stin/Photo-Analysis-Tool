import sys
from PyQt5.QtWidgets import QApplication
from main_gui import MainWindow  # Assure-toi que ce nom correspond à ton fichier PyQt
from scripts.database_manager import DatabaseManager  # Assure-toi que ce nom est correct
from scripts.generate_uml import generate_uml

def initialize_database():
    db_manager = DatabaseManager()  # Cela va créer la base de données si elle n'existe pas encore
    
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    initialize_database()  # Initialise la base de données avant de lancer l'application PyQt

    print("Don't forget to turn on the uml generation for production.")
    generate_uml()  # Générer les diagrammes UML avant de démarrer l'application Flask

    print("Starting the PyQt application.")
    main()
