import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from io import StringIO
import plotly.graph_objects as go # <-- Usaremos 'go' em vez de 'px'

# Importa o 'app' para registar o callback
from app.app import app

# --- A SUA PALETA DE CORES ---
# (#78A28E (Verde = Recorrente), #FFB300 (Amarelo = Novo))
COLORS_ACQUISITION = {
    'Recorrente': '#78A28E',
    'Novo': '#FFB300'
}

# Este é o "layout" que o client_dashboard vai importar
layout = html.Div(
    className='dashboard-card', # Usa o estilo de cartão escuro
    children=[
        html.H3("Receita por Aquisição vs. Retenção"),
        dcc.Loading(
            id="loading-acquisition-graph",
            type="default",
            children=dcc.Graph(id='graph-acquisition')
        )
    ]
)

# --- CALLBACK ATUALIZADO (A SOLUÇÃO) ---
@callback(
    Output('graph-acquisition', 'figure'),
    Input('store-client-data', 'data'),
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_acquisition_graph(data, start_date, end_date, channels):
    if not data or 'orders' not in data or not start_date or not end_date:
        return go.Figure().update_layout(
            title="Aguardando seleção de data...",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )

    df = pd.read_json(StringIO(data['orders']), orient='split')
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    
    # --- Aplica os Filtros (igual aos outros) ---
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()
    df_filtered = df[
        (df['createdAt'].dt.date >= start_date_obj) &
        (df['createdAt'].dt.date <= end_date_obj)
    ]
    df_filtered['salesChannel'] = df_filtered['salesChannel'].fillna('PDV')
    if channels:
        df_filtered = df_filtered[df_filtered['salesChannel'].isin(channels)]
        
    df_concluded = df_filtered[df_filtered['status'] == 'CONCLUDED'].copy()
    
    if df_concluded.empty:
        return go.Figure().update_layout(
            title="Nenhum pedido encontrado para estes filtros",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )
        
    # --- Lógica de Aquisição vs. Retenção (Não muda) ---
    df_concluded = df_concluded.sort_values('createdAt')
    df_concluded['first_order_date'] = df_concluded.groupby('customer')['createdAt'].transform('min')
    df_concluded['customer_type'] = np.where(
        df_concluded['createdAt'] == df_concluded['first_order_date'], 
        'Novo', 
        'Recorrente'
    )
    df_concluded['ano_mes'] = df_concluded['createdAt'].dt.strftime('%Y-%m')
    df_grouped = df_concluded.groupby(
        ['ano_mes', 'customer_type']
    )['totalAmount'].sum().reset_index()

    # --- CORREÇÃO: Criação do Gráfico (usando go.Figure) ---
    # Substituímos o 'px.area()' que estava a falhar
    
    fig = go.Figure()
    
    # Lista dos tipos, garantindo que 'Recorrente' vem primeiro para
    # ficar na base do gráfico de área empilhada.
    customer_types = ['Recorrente', 'Novo']
    
    for c_type in customer_types:
        df_trace = df_grouped[df_grouped['customer_type'] == c_type]
        
        # Se um tipo não tiver dados (ex: só clientes novos), pula
        if df_trace.empty:
            continue
            
        fig.add_trace(go.Scatter(
            x=df_trace['ano_mes'],
            y=df_trace['totalAmount'],
            name=c_type,
            mode='lines',
            fill='tozeroy', # Preenche a área até o eixo Y
            stackgroup='one', # Empilha as áreas
            line=dict(color=COLORS_ACQUISITION.get(c_type)) # Usa a nossa cor
        ))

    # --- Fim da Correção ---

    fig.update_layout(
        title="Receita de Clientes Novos vs. Recorrentes",
        xaxis_title="Mês (Ano-Mês)",
        yaxis_title="Receita Total (R$)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f0f0f0',
        hovermode="x unified",
        legend_title_text='Tipo de Cliente'
    )

    return fig