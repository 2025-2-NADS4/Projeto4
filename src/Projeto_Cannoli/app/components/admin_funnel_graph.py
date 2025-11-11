import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from datetime import datetime

from app.app import app

FUNNEL_COLORS = ['#78A28E', '#FFB300', '#FD822A']

layout = html.Div(
    className='dashboard-card',
    children=[
        html.H3("Funil de Engajamento de Campanhas (Filtrado)"),
        dcc.Loading(
            id="loading-funnel",
            type="default",
            children=dcc.Graph(id='graph-admin-funnel')
        )
    ]
)

# CALLBACK: Atualizar o Gráfico de Funil (AGORA COM FILTROS)
@callback(
    Output('graph-admin-funnel', 'figure'),
    Input('store-admin-data', 'data'),
    Input('admin-filter-date-range', 'start_date'),
    Input('admin-filter-date-range', 'end_date'),
    Input('admin-filter-store', 'value') # <-- NOVO INPUT
)
def update_funnel_graph(data, start_date, end_date, stores):
    if not data or not start_date or not end_date:
        return go.Figure().update_layout(
            title="Aguardando filtros...",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )

    # --- Carrega todos os dados ---
    df_queue = pd.read_json(StringIO(data['campaign_queue']), orient='split')
    df_orders = pd.read_json(StringIO(data['orders']), orient='split')

    # Converte datas
    df_queue['createdAt'] = pd.to_datetime(df_queue['createdAt'])
    df_orders['createdAt'] = pd.to_datetime(df_orders['createdAt'])
    
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()
    
    # --- Filtra os dados ---
    df_queue = df_queue[
        (df_queue['createdAt'].dt.date >= start_date_obj) &
        (df_queue['createdAt'].dt.date <= end_date_obj)
    ]
    df_orders = df_orders[
        (df_orders['createdAt'].dt.date >= start_date_obj) &
        (df_orders['createdAt'].dt.date <= end_date_obj)
    ]
    
    if stores:
        df_queue = df_queue[df_queue['storeId'].isin(stores)]
        df_orders = df_orders[df_orders['companyId'].isin(stores)]
        
    # --- Calcula o Funil ---
    enviados = len(df_queue[df_queue['status'] >= 2])
    lidos = len(df_queue[df_queue['status'] == 4])
    convertidos = len(df_orders[df_orders['generatedByCampaign'] == True])
    
    etapas_nomes = ['Enviados', 'Lidos', 'Convertidos']
    etapas_valores = [enviados, lidos, convertidos]

    fig = go.Figure(go.Funnel(
        y = etapas_nomes,
        x = etapas_valores,
        textinfo = "value+percent initial",
        marker = {"color": FUNNEL_COLORS},
        connector = {"line": {"color": "#808080", "dash": "dot", "width": 1}}
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f0f0f0'
    )
    return fig