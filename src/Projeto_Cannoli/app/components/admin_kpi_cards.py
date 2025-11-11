import dash
from dash import html, callback, no_update
from dash.dependencies import Input, Output
import pandas as pd
from io import StringIO

from app.app import app

layout = html.Div(
    style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(3, 1fr)',
        'gap': '20px',
    },
    id='admin-kpi-container'
)

# CALLBACK: Atualizar os KPIs do Admin (AGORA COM FILTROS)
@callback(
    Output('admin-kpi-container', 'children'),
    Input('store-admin-data', 'data'),
    Input('admin-filter-date-range', 'start_date'),
    Input('admin-filter-date-range', 'end_date'),
    Input('admin-filter-store', 'value') # <-- NOVO INPUT
)
def update_admin_kpi_cards(data, start_date, end_date, stores):
    """
    Quando os filtros mudam, recalcula os KPIs.
    """
    if not data or not start_date or not end_date:
        # Mostra placeholders se os dados não estiverem prontos
        cards = [
            html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[html.H3("Total de Clientes"), html.H2("...")]),
            html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[html.H3("Total de Campanhas"), html.H2("...")]),
            html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[html.H3("Total de Envios"), html.H2("...")])
        ]
        return cards

    # --- Carrega todos os dados ---
    df_customers = pd.read_json(StringIO(data['customers']), orient='split')
    df_campaigns = pd.read_json(StringIO(data['campaigns']), orient='split')
    df_queue = pd.read_json(StringIO(data['campaign_queue']), orient='split')

    # Converte datas (necessário para filtros)
    df_customers['createdAt'] = pd.to_datetime(df_customers['createdAt'])
    df_campaigns['createdAt'] = pd.to_datetime(df_campaigns['createdAt'])
    df_queue['createdAt'] = pd.to_datetime(df_queue['createdAt'])

    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()

    # --- Filtra os dados ---
    
    # 1. Filtra por Data
    df_customers = df_customers[
        (df_customers['createdAt'].dt.date >= start_date_obj) &
        (df_customers['createdAt'].dt.date <= end_date_obj)
    ]
    df_campaigns = df_campaigns[
        (df_campaigns['createdAt'].dt.date >= start_date_obj) &
        (df_campaigns['createdAt'].dt.date <= end_date_obj)
    ]
    df_queue = df_queue[
        (df_queue['createdAt'].dt.date >= start_date_obj) &
        (df_queue['createdAt'].dt.date <= end_date_obj)
    ]

    # 2. Filtra por Loja (se selecionado)
    if stores:
        df_campaigns = df_campaigns[df_campaigns['storeId'].isin(stores)]
        df_queue = df_queue[df_queue['storeId'].isin(stores)]
        # (Assumindo que clientes não estão ligados a uma loja no registo,
        #  mas sim os pedidos/campanhas)

    # --- Calcula os KPIs ---
    total_clientes = len(df_customers)
    total_campanhas = len(df_campaigns)
    total_envios = len(df_queue[df_queue['status'] >= 2]) # Enviados

    # Formata os valores
    clientes_fmt = f"{total_clientes:,}".replace(',', '.')
    campanhas_fmt = f"{total_campanhas:,}".replace(',', '.')
    envios_fmt = f"{total_envios:,}".replace(',', '.')

    cards = [
        html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[html.H3("Total de Clientes"), html.H2(clientes_fmt)]),
        html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[html.H3("Total de Campanhas"), html.H2(campanhas_fmt)]),
        html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[html.H3("Total de Envios"), html.H2(envios_fmt)])
    ]
    return cards