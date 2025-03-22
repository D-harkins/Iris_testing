import requests
import dash
from dash import dcc, html
import plotly.io as pio

app = dash.Dash(__name__)

API_URL = "http://127.0.0.1:8000/plot-data"

def fetch_plotly_figure():
    response = requests.get(API_URL)

    if response.status_code == 200:
        fig_json = response.json()
        return pio.from_json(fig_json)
    
    return None
fig = fetch_plotly_figure()

app.layout = html.Div([
    html.H1("Petal Length by Sepal Length",
            style={"font-family": "Helvetica"}),
    dcc.Graph(figure=fig) if fig else html.P("Error loading graph.")
])

if __name__ == "__main__":
    app.run_server(debug=True)