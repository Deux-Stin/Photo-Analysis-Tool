from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import sqlite3
import pandas as pd

class DashApp:
    def __init__(self, flask_app):
        self.dash_app = Dash(__name__, server=flask_app, url_base_pathname='/dash/')
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self):
        self.dash_app.layout = html.Div([
            dcc.Dropdown(
                id='filter-dropdown',
                options=[
                    {'label': 'Date', 'value': 'date_taken'},
                    {'label': 'Location', 'value': 'location'},
                    {'label': 'Focal Length', 'value': 'focal_length'},
                    {'label': 'Aperture', 'value': 'aperture'},
                    {'label': 'Shutter Speed', 'value': 'shutter_speed'}
                ],
                value='date_taken'
            ),
            dcc.Graph(id='filter-graph')
        ])

    def _setup_callbacks(self):
        @self.dash_app.callback(
            Output('filter-graph', 'figure'),
            [Input('filter-dropdown', 'value')]
        )
        def update_graph(selected_filter):
            conn = sqlite3.connect('data/photos.db')
            query = f"SELECT {selected_filter}, COUNT(*) FROM photos GROUP BY {selected_filter}"
            df = pd.read_sql(query, conn)
            conn.close()

            return {
                'data': [{'x': df[selected_filter], 'y': df['COUNT(*)'], 'type': 'bar'}],
                'layout': {'title': f'Photo Analysis by {selected_filter}'}
            }
