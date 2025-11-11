# wsgi.py (Web Server Gateway Interface)
# Este é o ficheiro que o servidor de produção (gunicorn) irá executar.

# Importa o objeto 'server' do Flask, que contém o Dash
from app.app import server as application

# Importa todos os ficheiros necessários para garantir que os callbacks estão registados
from app import index
from app.components import kpi_cards
from app.components import revenue_graph
from app.components import heatmap_graph
from app.components import donut_charts
from app.components import client_anomaly_alerts
from app.components import admin_funnel_graph
from app.components import admin_kpi_cards
from app.components import admin_suggestions_panel
from app.components import admin_simulation_tool

# O servidor Gunicorn irá executar a variável 'application'
if __name__ == "__main__":
    application.run()