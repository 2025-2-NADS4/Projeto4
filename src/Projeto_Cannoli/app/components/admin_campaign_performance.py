import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from io import StringIO
import plotly.graph_objects as go

# Importa o 'app' para registar o callback
from app.app import app

# --- A SUA PALETA DE CORES ---
PROJECT_COLORS = ['#78A28E', '#FFB300', '#6C4549', '#FD822A', '#B4E0C3']

# Este é o "layout" que o admin_dashboard vai importar
layout = html.Div(
    className='dashboard-card', # Reutiliza o estilo de cartão escuro
    children=[
        html.H3("Mensagens Lidas por Campanha"), # <--- TÍTULO ATUALIZADO
        dcc.Loading(
            id="loading-campaign-performance",
            type="default",
            children=dcc.Graph(id='graph-campaign-performance')
        )
    ]
)

# CALLBACK: Atualizar o Gráfico de Barras de Desempenho (CORRIGIDO)
@callback(
    Output('graph-campaign-performance', 'figure'),
    Input('store-admin-data', 'data'),
    Input('admin-filter-date-range', 'start_date'),
    Input('admin-filter-date-range', 'end_date'),
    Input('admin-filter-store', 'value')
)
def update_campaign_performance_graph(data, start_date, end_date, stores):
    """
    Quando os filtros mudam, calcula as MENSAGENS LIDAS por campanha.
    """
    if not data or 'campaign_queue' not in data or 'campaigns' not in data:
        return go.Figure().update_layout(
            title="A carregar dados...",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )

    # --- Carrega os dados necessários ---
    # (Não precisamos mais do 'orders' para este gráfico)
    df_queue = pd.read_json(StringIO(data['campaign_queue']), orient='split')
    df_campaigns = pd.read_json(StringIO(data['campaigns']), orient='split')

    # Converte datas
    df_queue['createdAt'] = pd.to_datetime(df_queue['createdAt'])
    
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()
    
    # --- Filtra os dados ---
    df_queue_filtered = df_queue[
        (df_queue['createdAt'].dt.date >= start_date_obj) &
        (df_queue['createdAt'].dt.date <= end_date_obj)
    ]
    if stores:
        df_queue_filtered = df_queue_filtered[df_queue_filtered['storeId'].isin(stores)]
        
    # --- Lógica do Gráfico (CORRIGIDA) ---
    
    # 1. Filtra apenas mensagens que foram 'Lidas' (status=4)
    df_reads = df_queue_filtered[df_queue_filtered['status'] == 4]
    
    if df_reads.empty:
        return go.Figure().update_layout(
            title="Nenhuma mensagem lida encontrada para estes filtros",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )
        
    # 2. Agrupa por 'campaignId' e conta as mensagens
    # (Este groupby VAI funcionar, pois 'campaignId' existe em df_queue)
    df_grouped = df_reads.groupby('campaignId').size().reset_index(name='mensagens_lidas')
    
    # 3. Junta com a tabela de 'campaigns' para obter o NOME da campanha
    df_merged = df_grouped.merge(
        df_campaigns[['id', 'name']],
        left_on='campaignId',
        right_on='id'
    )
    
    # 4. Ordena do maior para o menor
    df_merged = df_merged.sort_values(by='mensagens_lidas', ascending=False)

    # --- Criação do Gráfico (Gráfico de Barras) ---
    fig = px.bar(
        df_merged,
        x='name',
        y='mensagens_lidas',
        title="Total de Mensagens Lidas por Nome da Campanha",
        color='name',
        color_discrete_sequence=PROJECT_COLORS
    )
    
    fig.update_layout(
        xaxis_title="Campanha",
        yaxis_title="Nº de Mensagens Lidas",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f0f0f0',
        showlegend=False
    )

    return fig