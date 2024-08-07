from flask import Flask
from .routes_manager import RoutesManager  # Utilisez le nom correct du fichier
from dash_app import DashApp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    routes_manager = RoutesManager(app)
    app.register_blueprint(routes_manager.main)
    
    DashApp(app)  # Crée et configure l'application Dash

    return app
