import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, date
from io import StringIO

# Importa o 'app' para registar o callback
from app.app import app

# A sua paleta de cores
PROJECT_COLORS = ['#78A28E', '#FFB300', '#6C4549', '#FD822A', '#B4E0C3']

# Layout, agora usa className
layout = html.Div(
    className='dashboard-card', # <--- USA A CLASSE
    children=[
        html.H3("Receita Mensal por Canal"),
        dcc.Loading(
            id="loading-graph",
            type="default",
            children=dcc.Graph(id='graph-revenue-over-time')
        )
    ]
)

# CALLBACK: Atualizar Gráfico de Receita
@callback(
    Output('graph-revenue-over-time', 'figure'),
    Input('store-client-data', 'data'),
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_revenue_graph_from_store(data, start_date, end_date, channels):
    if not data or 'orders' not in data or not start_date or not end_date:
        return go.Figure().update_layout(title="Aguardando seleção de data...")

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
        return go.Figure().update_layout(title="Nenhum pedido encontrado para estes filtros")
        
    df_concluded['createdAt_str'] = df_concluded['createdAt'].dt.strftime('%Y-%m')
    df_grouped = df_concluded.groupby(['createdAt_str', 'salesChannel'])['totalAmount'].sum().reset_index()

    if df_grouped.empty:
        return go.Figure().update_layout(title="Nenhum dado para agrupar")

    fig = px.line(
        df_grouped,
        x='createdAt_str',
        y='totalAmount',
        color='salesChannel',
        color_discrete_sequence=PROJECT_COLORS, # Usa a paleta
        markers=True,
        title="Receita Mensal por Canal (Filtrada)"
    )
    
    data_contratacao_str = "2025-01"
    
    if start_date_obj <= date(2025, 1, 1) <= end_date_obj:
        max_revenue = df_grouped['totalAmount'].max() * 1.05
        fig.add_shape(
            type="line", x0=data_contratacao_str, y0=0,
            x1=data_contratacao_str, y1=max_revenue,
            line=dict(color="#FD822A", width=2, dash="dash") # Laranja da paleta
        )
        fig.add_annotation(
            x=data_contratacao_str, y=max_revenue,
            text="Início da Cannoli", showarrow=True,
            arrowhead=1, yshift=10, font=dict(color="#FD822A")
        )
    
    # --- MUDANÇA PARA TEMA ESCURO ---
    fig.update_layout(
        xaxis_title="Mês (Ano-Mês)",
        yaxis_title="Receita Total (R$)",
        template="plotly_dark", # <--- USA O TEMPLO ESCURO
        paper_bgcolor='rgba(0,0,0,0)', # Fundo do papel transparente
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        font_color='#f0f0f0', # Cor da fonte clara
        hovermode="x unified"
    )
    
    return fig