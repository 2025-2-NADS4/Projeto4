import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd

# Importa o 'app' e o nosso novo 'modelo'
from app.app import app
from app import ml_model # <--- NOVO

# --- A SUA PALETA DE CORES ---
COLOR_VERDE = '#78A28E'
COLOR_AMARELO = '#FFB300'
COLOR_LARANJA = '#FD822A'
COLOR_VINHO = '#6C4549'

# --- Estilos ---
input_style = {
    'width': '100%', 'padding': '10px', 'marginBottom': '10px',
    'backgroundColor': '#555', 'border': '1px solid #777',
    'color': 'white', 'borderRadius': '4px'
}
result_card_style = {
    'backgroundColor': '#4a4a4a', 'padding': '15px',
    'borderRadius': '5px', 'textAlign': 'center'
}

# Este é o "layout" que o admin_dashboard vai importar
layout = html.Div(
    className='dashboard-grid-2-col', # Grelha de 2 colunas
    children=[
        
        # --- Coluna 1: Entradas da Simulação (ATUALIZADA) ---
        html.Div(
            className='dashboard-card',
            children=[
                html.H3("Simulação de Campanha (com IA)"),
                
                html.Label("1. Selecione o Segmento-Alvo:"),
                dcc.Dropdown(
                    id='sim-target-audience',
                    options=[
                        {'label': 'Clientes Inativos (Status 2)', 'value': 'inativos'},
                        {'label': 'Clientes Ativos (Status 1)', 'value': 'ativos'}
                    ],
                    value='inativos', # Valor padrão
                    clearable=False
                ),
                
                html.Label("2. Custo por Mensagem (R$)", style={'marginTop': '20px'}),
                dcc.Input(id='sim-cost-msg', type='number', value=0.10, style=input_style),

                # --- Campos que agora são preenchidos por IA ---
                html.Hr(),
                html.H5("Previsões do Modelo (Auto-preenchido):"),
                html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
                    html.Div(style={'flex': 1}, children=[
                        html.Label("Público Encontrado:"),
                        html.H4(id='sim-out-audience', children="...")
                    ]),
                    html.Div(style={'flex': 1}, children=[
                        html.Label("Conversão Prevista (ML):"),
                        html.H4(id='sim-out-conv-rate', children="...")
                    ]),
                    html.Div(style={'flex': 1}, children=[
                        html.Label("Ticket Médio Previsto:"),
                        html.H4(id='sim-out-avg-ticket', children="...")
                    ]),
                ])
            ]
        ),
        
        # --- Coluna 2: Resultados da Simulação ---
        html.Div(
            className='dashboard-card',
            children=[
                html.H3("Impacto Previsto"),
                html.Div(
                    style={
                        'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                        'gap': '15px', 'marginTop': '20px'
                    },
                    children=[
                        # Custo Total
                        html.Div(style=result_card_style, children=[
                            html.H5("Custo Total", style={'color': COLOR_LARANJA}),
                            html.H3(id='sim-out-cost', children="R$ 0,00")
                        ]),
                        # Receita Prevista
                        html.Div(style=result_card_style, children=[
                            html.H5("Receita Prevista", style={'color': COLOR_VERDE}),
                            html.H3(id='sim-out-revenue', children="R$ 0,00")
                        ]),
                        # Lucro Previsto
                        html.Div(style=result_card_style, children=[
                            html.H5("Lucro Previsto", style={'color': 'white'}),
                            html.H3(id='sim-out-profit', children="R$ 0,00")
                        ]),
                        # ROI
                        html.Div(style=result_card_style, children=[
                            html.H5("ROI", style={'color': COLOR_AMARELO}),
                            html.H3(id='sim-out-roi', children="0%")
                        ])
                    ]
                )
            ]
        )
    ]
)

# CALLBACK: Calcular a Simulação (ATUALIZADO)
@callback(
    # Saídas dos resultados
    Output('sim-out-cost', 'children'),
    Output('sim-out-revenue', 'children'),
    Output('sim-out-profit', 'children'),
    Output('sim-out-roi', 'children'),
    # Saídas dos campos auto-preenchidos
    Output('sim-out-audience', 'children'),
    Output('sim-out-conv-rate', 'children'),
    Output('sim-out-avg-ticket', 'children'),
    # Entradas
    Input('sim-target-audience', 'value'),
    Input('sim-cost-msg', 'value'),
    State('store-admin-data', 'data') # <-- Lê o store com TODOS os dados
)
def update_simulation_outputs(target_audience, cost_msg, data):
    """
    Usa o modelo de ML para prever e calcular o impacto.
    """
    if not data or not cost_msg or not target_audience:
        return (no_update,) * 7 # Não atualiza nada

    try:
        # --- 1. Chama o "Modelo de ML" ---
        audience_count, conv_rate, avg_ticket = ml_model.get_ml_predictions(
            target_audience, data
        )
        
        if audience_count == 0:
            return "R$ 0,00", "R$ 0,00", "R$ 0,00", "0%", "0", "0%", "R$ 0,00"

        # --- 2. Cálculo do Impacto ---
        total_cost = audience_count * cost_msg
        total_conversions = audience_count * (conv_rate / 100.0)
        total_revenue = total_conversions * avg_ticket
        total_profit = total_revenue - total_cost
        
        if total_cost > 0:
            roi = (total_profit / total_cost) * 100
        else:
            roi = 0

        # --- 3. Formatação ---
        cost_fmt = f"R$ {total_cost:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        revenue_fmt = f"R$ {total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        profit_fmt = f"R$ {total_profit:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        roi_fmt = f"{roi:,.1f}%"
        
        # Formatação dos campos de previsão
        audience_fmt = f"{audience_count:,}".replace(',', '.')
        conv_rate_fmt = f"{conv_rate:.1f}%"
        avg_ticket_fmt = f"R$ {avg_ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return cost_fmt, revenue_fmt, profit_fmt, roi_fmt, \
               audience_fmt, conv_rate_fmt, avg_ticket_fmt
        
    except Exception as e:
        print(f"Erro na simulação de ML: {e}")
        return "Erro", "Erro", "Erro", "Erro", "Erro", "Erro", "Erro"