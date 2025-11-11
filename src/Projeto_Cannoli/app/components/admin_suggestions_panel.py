import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import pandas as pd
from io import StringIO

from app.app import app

COLOR_SUCESSO = '#78A28E'
COLOR_ALERTA = '#FFB300'
COLOR_CRITICO = '#FD822A'

layout = html.Div(
    className='dashboard-card',
    children=[
        html.H3("Sugestões Automáticas (Filtrado)"),
        dcc.Loading(
            id="loading-suggestions",
            type="default",
            children=html.Div(id='admin-suggestions-content')
        )
    ]
)

def create_suggestion_box(title, text, color):
    return html.Div(style={
        'borderLeft': f'5px solid {color}', 'padding': '10px 15px',
        'backgroundColor': '#4a4a4a', 'borderRadius': '5px',
        'marginBottom': '15px'
    }, children=[
        html.H5(title, style={'margin': '0 0 5px 0', 'color': color}),
        html.P(text, style={'margin': '0'})
    ])

# CALLBACK: Gerar as Sugestões (AGORA COM FILTROS)
@callback(
    Output('admin-suggestions-content', 'children'),
    Input('store-admin-data', 'data'),
    Input('admin-filter-date-range', 'start_date'),
    Input('admin-filter-date-range', 'end_date'),
    Input('admin-filter-store', 'value') # <-- NOVO INPUT
)
def update_suggestions(data, start_date, end_date, stores):
    if not data or not start_date or not end_date:
        return html.P("Aguardando filtros...")

    # --- Carrega e Filtra os dados (igual ao Funil) ---
    df_queue = pd.read_json(StringIO(data['campaign_queue']), orient='split')
    df_orders = pd.read_json(StringIO(data['orders']), orient='split')

    df_queue['createdAt'] = pd.to_datetime(df_queue['createdAt'])
    df_orders['createdAt'] = pd.to_datetime(df_orders['createdAt'])
    
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()
    
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
        
    # --- Calcula as taxas (com dados filtrados) ---
    enviados = len(df_queue[df_queue['status'] >= 2])
    lidos = len(df_queue[df_queue['status'] == 4])
    convertidos = len(df_orders[df_orders['generatedByCampaign'] == True])
    
    suggestions_list = []
    
    try:
        taxa_leitura = lidos / enviados
    except ZeroDivisionError:
        taxa_leitura = 0
    try:
        taxa_conversao = convertidos / lidos
    except ZeroDivisionError:
        taxa_conversao = 0

    # --- Gera as Sugestões ---
    if taxa_leitura < 0.30 and enviados > 100:
        suggestions_list.append(create_suggestion_box(
            "Alerta: Taxa de Leitura Baixa",
            f"Apenas {taxa_leitura:.1%} dos clientes leram as mensagens neste período/loja. Otimizar horário.",
            COLOR_ALERTA
        ))
    if taxa_conversao < 0.10 and lidos > 50:
        suggestions_list.append(create_suggestion_box(
            "Alerta: Taxa de Conversão Baixa",
            f"Apenas {taxa_conversao:.1%} dos leitores converteram. Melhorar a oferta.",
            COLOR_CRITICO
        ))
    if not suggestions_list:
        suggestions_list.append(create_suggestion_box(
            "Tudo Certo!",
            "As taxas de leitura e conversão estão saudáveis para este filtro.",
            COLOR_SUCESSO
        ))

    return suggestions_list