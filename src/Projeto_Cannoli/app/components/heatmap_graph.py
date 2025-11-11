import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from io import StringIO

# Importa o 'app' para registar o callback
from app.app import app

HEATMAP_COLORS = ['#B4E0C3', '#78A28E'] # Verde Claro -> Verde Principal

layout = html.Div(
    className='dashboard-card',
    children=[
        html.H3("Heatmap de Pedidos (Hora vs. Dia da Semana)"),
        dcc.Loading(
            id="loading-heatmap",
            type="default",
            children=dcc.Graph(id='graph-heatmap')
        )
    ]
)

# CALLBACK: Atualizar o Heatmap
@callback(
    Output('graph-heatmap', 'figure'),
    Input('store-client-data', 'data'),
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_heatmap_graph(data, start_date, end_date, channels):
    if not data or 'orders' not in data or not start_date or not end_date:
        return go.Figure().update_layout(
            title="Aguardando seleção de data...",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )

    df = pd.read_json(StringIO(data['orders']), orient='split')
    df['createdAt'] = pd.to_datetime(df['createdAt'])

    # --- Aplicação dos Filtros ---
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()

    df_filtered = df[
        (df['createdAt'].dt.date >= start_date_obj) &
        (df['createdAt'].dt.date <= end_date_obj)
    ]
    
    # --- CORREÇÃO DO FILTRO (para 'Desconhecido') ---
    if channels:
        # Substitui os nulos por 'Desconhecido' ANTES de filtrar
        df_filtered['salesChannel'] = df_filtered['salesChannel'].fillna('Desconhecido')
        df_filtered = df_filtered[df_filtered['salesChannel'].isin(channels)]
    # --- FIM DA CORREÇÃO ---
    
    # --- Lógica Específica do Heatmap ---
    df_filtered['dia_semana'] = df_filtered['createdAt'].dt.day_name()
    df_filtered['hora_dia'] = df_filtered['createdAt'].dt.hour
    
    df_heatmap = df_filtered.groupby(
        ['dia_semana', 'hora_dia']
    ).size().reset_index(name='total_pedidos')
    
    if df_heatmap.empty:
        return go.Figure().update_layout(
            title="Nenhum pedido encontrado para estes filtros",
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f0f0'
        )

    dias_ordenados = [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
        'Friday', 'Saturday', 'Sunday'
    ]
    dias_map_pt = {
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    dias_ordenados_pt = [dias_map_pt[dia] for dia in dias_ordenados]
    
    df_heatmap['dia_semana'] = df_heatmap['dia_semana'].map(dias_map_pt)
    df_heatmap['dia_semana'] = pd.Categorical(
        df_heatmap['dia_semana'], categories=dias_ordenados_pt, ordered=True
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=df_heatmap['total_pedidos'],
        x=df_heatmap['hora_dia'],
        y=df_heatmap['dia_semana'],
        colorscale=HEATMAP_COLORS,
        hoverongaps=False,
        hovertemplate="<b>Dia:</b> %{y}<br><b>Hora:</b> %{x}h<br><b>Pedidos:</b> %{z}<extra></extra>"
    ))

    fig.update_layout(
        title="Volume de Pedidos por Hora e Dia da Semana",
        xaxis_title="Hora do Dia (0-23)",
        yaxis_title="Dia da Semana",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f0f0f0',
        yaxis=dict(
            categoryorder='array', 
            categoryarray=list(reversed(dias_ordenados_pt))
        ),
        xaxis=dict(tickmode='linear', dtick=2) 
    )

    return fig