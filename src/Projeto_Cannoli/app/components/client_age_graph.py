import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from io import StringIO
import plotly.graph_objects as go
from datetime import datetime

# Importa o 'app' para registar o callback
from app.app import app

# --- A SUA PALETA DE CORES ---
# (#78A28E (Verde), #FFB300 (Amarelo), #6C4549 (Castanho), #FD822A (Laranja), #B4E0C3 (Verde Claro))
AGE_COLORS = ['#B4E0C3', '#78A28E', '#FFB300', '#FD822A', '#6C4549']

# Este é o "layout" que o client_dashboard vai importar
layout = html.Div(
    className='dashboard-card', # Usa o estilo de cartão escuro
    children=[
        html.H3("Receita por Faixa Etária"),
        dcc.Loading(
            id="loading-age-graph",
            type="default",
            children=dcc.Graph(id='graph-age')
        )
    ]
)

# CALLBACK: Atualizar o Gráfico de Faixa Etária
@callback(
    Output('graph-age', 'figure'),
    Input('store-client-data', 'data'), # "Escuta" o store (que agora é um dict)
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_age_graph(data, start_date, end_date, channels):
    if not data or 'orders' not in data or 'customers' not in data:
        return go.Figure().update_layout(
            title="A carregar dados...",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )

    # --- Lê os dados da NOVA estrutura do store ---
    df_orders = pd.read_json(StringIO(data['orders']), orient='split')
    df_customers = pd.read_json(StringIO(data['customers']), orient='split')
    df_orders['createdAt'] = pd.to_datetime(df_orders['createdAt'])
    
    # --- Aplica os Filtros (igual aos outros) ---
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()
    df_filtered = df_orders[
        (df_orders['createdAt'].dt.date >= start_date_obj) &
        (df_orders['createdAt'].dt.date <= end_date_obj)
    ]
    df_filtered['salesChannel'] = df_filtered['salesChannel'].fillna('PDV')
    if channels:
        df_filtered = df_filtered[df_filtered['salesChannel'].isin(channels)]
        
    df_concluded = df_filtered[df_filtered['status'] == 'CONCLUDED']
    
    if df_concluded.empty:
        return go.Figure().update_layout(
            title="Nenhum pedido encontrado para estes filtros",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )
        
    # --- Lógica de Faixa Etária ---
    # 1. Junta os pedidos com os clientes
    df_merged = df_concluded.merge(
        df_customers[['id', 'dateOfBirth']],
        left_on='customer',
        right_on='id'
    )
    if df_merged.empty:
        return go.Figure().update_layout(title="Não foi possível ligar pedidos a clientes")

    # 2. Calcula a Idade
    df_merged['dateOfBirth'] = pd.to_datetime(df_merged['dateOfBirth'])
    df_merged['age'] = (datetime.now() - df_merged['dateOfBirth']).dt.days / 365.25
    
    # 3. Cria as Faixas Etárias
    bins = [0, 18, 25, 35, 45, 65, 100]
    labels = ['< 18', '18-25', '26-35', '36-45', '46-65', '65+']
    df_merged['age_group'] = pd.cut(df_merged['age'], bins=bins, labels=labels, right=False)
    
    # 4. Agrupa por Faixa Etária
    df_grouped = df_merged.groupby('age_group')['totalAmount'].sum().reset_index()

    # --- Criação do Gráfico (Gráfico de Barras) ---
    fig = px.bar(
        df_grouped,
        x='age_group',
        y='totalAmount',
        color='age_group',
        color_discrete_sequence=AGE_COLORS, # <-- USA A PALETA
        title="Receita por Faixa Etária"
    )

    fig.update_layout(
        xaxis_title="Faixa Etária",
        yaxis_title="Receita Total (R$)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f0f0f0',
        showlegend=False
    )

    return fig