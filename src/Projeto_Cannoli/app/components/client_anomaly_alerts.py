import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import pandas as pd
from io import StringIO
import datetime # Importa o datetime para usar o 'date'

# Importa o 'app' para registar o callback
from app.app import app

COLOR_CRITICO = '#FD822A' # Laranja

def create_alert_card(title, text):
    """Função helper para criar o cartão de alerta."""
    return html.Div(
        className='dashboard-card',
        style={
            'borderLeft': f'5px solid {COLOR_CRITICO}',
            'marginBottom': '20px'
        },
        children=[
            html.H3(title, style={'color': COLOR_CRITICO}),
            html.P(text)
        ]
    )

# Layout (contentor vazio)
layout = html.Div(id='alert-container')

# CALLBACK: Gerar Alertas de Anomalia (CORRIGIDO)
@callback(
    Output('alert-container', 'children'),
    Input('store-client-data', 'data'),
    Input('filter-date-range', 'start_date'),
    Input('filter-date-range', 'end_date'),
    Input('filter-sales-channel', 'value')
)
def update_anomaly_alerts(data, start_date, end_date, channels):
    """
    Analisa os dados filtrados e gera alertas.
    """
    if not data or 'orders' not in data or not start_date or not end_date:
        return []

    df = pd.read_json(StringIO(data['orders']), orient='split')
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    
    # --- Aplica os filtros (igual aos outros callbacks) ---
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
        return []
        
    # --- Lógica de Deteção de Anomalia (CORRIGIDA) ---
    # 'end_date_obj' já é um objeto 'date'. Não precisamos de o reconverter.
    
    # Período Recente (últimos 7 dias)
    # 'end_date_obj' (date) - 'Timedelta' = 'date'
    recent_start = end_date_obj - pd.Timedelta(days=6) 
    df_recent = df_concluded[
        # Compara date >= date
        (df_concluded['createdAt'].dt.date >= recent_start) &
        (df_concluded['createdAt'].dt.date <= end_date_obj)
    ]
    recent_revenue = df_recent['totalAmount'].sum()
    
    # Período Anterior (7 dias antes)
    previous_end = recent_start - pd.Timedelta(days=1) # date
    previous_start = previous_end - pd.Timedelta(days=6) # date
    
    df_previous = df_concluded[
        # Compara date >= date
        (df_concluded['createdAt'].dt.date >= previous_start) &
        (df_concluded['createdAt'].dt.date <= previous_end)
    ]
    previous_revenue = df_previous['totalAmount'].sum()
    
    # --- A Regra do Alerta ---
    if previous_revenue > 200:
        percent_change = (recent_revenue - previous_revenue) / previous_revenue
        
        if percent_change < -0.30: # Queda > 30%
            alert_title = f"Alerta de Variação Anômala (Queda de {abs(percent_change):.0%})"
            alert_text = (
                f"A receita dos últimos 7 dias (R$ {recent_revenue:,.2f}) "
                f"foi significativamente menor que a dos 7 dias anteriores (R$ {previous_revenue:,.2f})."
            )
            return [create_alert_card(alert_title, alert_text)]

    return [] # Sem anomalia, retorna vazio