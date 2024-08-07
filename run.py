from flask import Flask
from app.routes_manager import RoutesManager  # Assurez-vous que ce nom est correct
from dash_app import DashApp
import generate_uml  # Importer le script de génération UML

def create_app():
    app = Flask(__name__, template_folder='app/templates')  # Spécifiez le répertoire des templates
    routes_manager = RoutesManager()
    app.register_blueprint(routes_manager.main)
    DashApp(app)  # Crée et configure l'application Dash
    return app

if __name__ == '__main__':
    generate_uml.generate_uml()  # Générer les diagrammes UML avant de démarrer l'application Flask

    app = create_app()
    app.run(debug=True)

