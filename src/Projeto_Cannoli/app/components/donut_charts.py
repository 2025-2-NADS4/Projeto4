import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
from datetime import datetime

# Importa o 'app' para registar os callbacks
from app.app import app


COLORS_ORDER_TYPE = {
    'DELIVERY': '#FFB300', 
    'INDOOR': '#FD822A',   
    'TAKEOUT': '#B4E0C3'   
}
COLORS_ROI = {
    'Gerado por Campanha': '#78A28E', 
    'Orgânico': '#6C4549'          
}

# Layout (Container)
layout = html.Div(
    className='dashboard-grid-2-col',
    children=[
        html.Div(
            className='dashboard-card',
            children=[
                html.H3("Pedidos por Tipo (Delivery, Indoor, etc.)"),
                dcc.Loading(
                    id="loading-donut-type",
                    type="default",
                    children=dcc.Graph(id='graph-donut-type')
                )
            ]
        ),
        html.Div(
            className='dashboard-card',
            children=[
                html.H3("Pedidos Pós-FIDELIZE (Orgânico vs. Campanha)"),
                dcc.Loading(
                    id="loading-donut-roi",
                    type="default",
                    children=dcc.Graph(id='graph-donut-roi')
                )
            ]
        )
    ]
)

# --- Funções de Filtragem ---
def filter_data(data, start_date, end_date, channels):
    """Função helper que aplica os filtros globais."""
    if not data or 'orders' not in data:
        return pd.DataFrame()

    df = pd.read_json(StringIO(data['orders']), orient='split')
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    
    # 1. Aplicar filtros de Data
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()

    df_filtered = df[
        (df['createdAt'].dt.date >= start_date_obj) &
        (df['createdAt'].dt.date <= end_date_obj)
    ]
    
    # 
    if df_filtered.empty:
        return df_filtered.copy() 

    # 2. Aplicar filtro de Canal
    df_filtered['salesChannel'] = df_filtered['salesChannel'].fillna('PDV')
    if channels:
        df_filtered = df_filtered[df_filtered['salesChannel'].isin(channels)]
        
    return df_filtered[df_filtered['status'] == 'CONCLUDED'].copy()

# --- Callbacks para os Gráficos de Rosca ---

# CALLBACK 1: Atualizar Gráfico de TIPO DE PEDIDO
@callback(
    Output('graph-donut-type', 'figure'),
    Input('store-client-data', 'data'),
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_donut_order_type(data, start_date, end_date, channels):
    df_filtered = filter_data(data, start_date, end_date, channels)
    
    # Se o DataFrame estiver VAZIO, retorna figura de erro
    if df_filtered.empty:
        return go.Figure().update_layout(
            title="Nenhum pedido encontrado para estes filtros",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )

    df_grouped = df_filtered['orderType'].value_counts().reset_index(name='count')
    
    fig = px.pie(
        df_grouped,
        names='orderType',
        values='count',
        hole=0.4, 
        color='orderType',
        color_discrete_map=COLORS_ORDER_TYPE 
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f0f0f0',
        legend_title_text='Tipo de Pedido'
    )
    
    return fig

# CALLBACK 2: Atualizar Gráfico de ROI (Campanha)
@callback(
    Output('graph-donut-roi', 'figure'),
    Input('store-client-data', 'data'),
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_donut_roi(data, start_date, end_date, channels):
    df_filtered = filter_data(data, start_date, end_date, channels)
    
    # Se o DataFrame estiver VAZIO, retorna figura de erro
    if df_filtered.empty:
        return go.Figure().update_layout(
            title="Nenhum pedido encontrado para estes filtros",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )
        
    # --- Lógica Específica do ROI ---
    data_contratacao = pd.to_datetime('2025-01-01T00:00:00Z').date()
    # Filtra apenas por pedidos "Pós-FIDELIZE" (que agora funciona em um DF não-vazio)
    df_pos_cannoli = df_filtered[df_filtered['createdAt'].dt.date >= data_contratacao]
    
    if df_pos_cannoli.empty:
        return go.Figure().update_layout(
            title="Nenhum dado Pós-FIDELIZE para estes filtros",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )
        
    df_pos_cannoli['roi_label'] = df_pos_cannoli['generatedByCampaign'].map({
        True: 'Gerado por Campanha',
        False: 'Orgânico'
    })
    
    df_grouped = df_pos_cannoli['roi_label'].value_counts().reset_index(name='count')

    fig = px.pie(
        df_grouped,
        names='roi_label',
        values='count',
        hole=0.4,
        color='roi_label',
        color_discrete_map=COLORS_ROI 
    )
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f0f0f0',
        legend_title_text='Origem do Pedido'
    )
    

    return fig
