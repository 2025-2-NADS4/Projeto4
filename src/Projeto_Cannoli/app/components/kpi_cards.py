import dash
from dash import html, callback, no_update
from dash.dependencies import Input, Output
import pandas as pd
from io import StringIO

# Importa o 'app' para registar o callback
from app.app import app




layout = html.Div(
    style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(3, 1fr)',
        'gap': '20px',
    },
    id='kpi-card-container'
)

# CALLBACK: Atualizar KPIs
@callback(
    Output('kpi-card-container', 'children'),
    Input('store-client-data', 'data'),
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_kpi_cards_from_store(data, start_date, end_date, channels):
    if not data or 'orders' not in data or not start_date or not end_date:
        return []

    df = pd.read_json(StringIO(data['orders']), orient='split')
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()

    df_filtered = df[
        (df['createdAt'].dt.date >= start_date_obj) &
        (df['createdAt'].dt.date <= end_date_obj)
    ]
        
    if channels:
        df_filtered = df_filtered[df_filtered['salesChannel'].isin(channels)]
    
    df_concluded = df_filtered[df_filtered['status'] == 'CONCLUDED']
    
    if df_concluded.empty:
        receita_total, total_pedidos, ticket_medio = 0, 0, 0
    else:
        receita_total = df_concluded['totalAmount'].sum()
        total_pedidos = len(df_concluded)
        ticket_medio = receita_total / total_pedidos

    receita_fmt = f"R$ {receita_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pedidos_fmt = f"{total_pedidos}"
    ticket_fmt = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    
    cards = [
        
        html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[
            html.H3("Receita Total"), 
            html.H2(receita_fmt)
        ]),
        html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[
            html.H3("Pedidos Concluídos"), 
            html.H2(pedidos_fmt)
        ]),
        html.Div(className='dashboard-card', style={'textAlign': 'center'}, children=[
            html.H3("Ticket Médio"), 
            html.H2(ticket_fmt)
        ])
    ]

    return cards
