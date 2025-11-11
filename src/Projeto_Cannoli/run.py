# run.py
from app.app import app, server
from app import index 
from werkzeug.serving import run_simple
from flask import redirect, url_for # <--- NOVO

# --- REGISTO DE CALLBACKS (igual a antes) ---
from app.components import kpi_cards
from app.components import revenue_graph
from app.components import heatmap_graph
from app.components import donut_charts
from app.components import client_anomaly_alerts
from app.components import admin_funnel_graph
from app.components import admin_kpi_cards
from app.components import admin_suggestions_panel
from app.components import admin_simulation_tool
# ---------------------------------------------

# --- CORREÇÃO FINAL: Regista a Rota /login no Flask ---
# Esta função garante que o Flask reconhece /dashboard/login
@server.route('/dashboard/login')
def login_route():
    # Apenas redireciona para a raiz do Dash, onde o index.py assume o controlo
    # e renderiza o login.layout.
    return redirect(url_for('dash_app')) 

if __name__ == '__main__':
    # Define o endpoint para a raiz do Dash (OBRIGATÓRIO para url_for)
    app.server.add_url_rule(app.config['requests_pathname_prefix'], 
                            view_func=app.index, 
                            endpoint='dash_app')
    
    # Executa o servidor Flask/Dash
    run_simple(
        '127.0.0.1', 
        8050, 
        server, 
        use_reloader=True, 
        use_debugger=True
    )