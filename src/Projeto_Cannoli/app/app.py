
import dash
from dash import dcc, html
from flask import Flask, session 

# Inicializa o servidor Flask
server = Flask(__name__)


server.config["SECRET_KEY"] = "" 
# ------------------------------

# Inicializa a aplicação Dash
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/',
    suppress_callback_exceptions=True
)

app.title = 'Cannoli Dashboard'


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])



from . import index
