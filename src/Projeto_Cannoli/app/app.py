# app/app.py (Configuração Mínima)
import dash
from dash import dcc, html
from flask import Flask, session # Apenas 'session' do Flask

# Inicializa o servidor Flask
server = Flask(__name__)

# --- CONFIGURAÇÃO DA SESSÃO ---
# Apenas a chave secreta é necessária para as sessões nativas do Flask
server.config["SECRET_KEY"] = "SUA_CHAVE_SECRETA_MUITO_SEGURA_AQUI" 
# ------------------------------

# Inicializa a aplicação Dash
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/',
    suppress_callback_exceptions=True
)

app.title = 'Cannoli Dashboard'

# Layout principal: VAZIO para ser preenchido pelo callback
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Importa o controlador de rotas
from . import index