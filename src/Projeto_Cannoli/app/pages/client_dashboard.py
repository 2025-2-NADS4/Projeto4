import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output, State
import pandas as pd
from io import StringIO
from datetime import datetime, date

# Importa o nosso cliente Supabase
from app import auth
# --- Importa TODOS os componentes ---
from app.components import kpi_cards
from app.components import revenue_graph
from app.components import heatmap_graph
from app.components import donut_charts
from app.components import client_anomaly_alerts
from app.components import client_acquisition_graph
from app.components import client_age_graph # <--- NOVO

# --- 1. Funções de Busca de Dados ---
def get_data_for_store():
    """
    Busca os dados das tabelas 'orders' E 'customers'
    """
    supabase = auth.get_supabase_client()
    if not supabase:
        print("Erro: Não foi possível obter o cliente Supabase.")
        return {}
    
    try:
        # 1. Busca Pedidos
        orders_resp = supabase.table('orders').select(
            'createdAt', 'totalAmount', 'status', 
            'salesChannel', 'orderType', 'generatedByCampaign', 'customer'
        ).limit(5000).execute()
        
        # 2. Busca Clientes (para o gráfico de idade)
        cust_resp = supabase.table('customers').select(
            'id', 'dateOfBirth' # Pede apenas as colunas que precisamos
        ).limit(10000).execute() # (Assume que temos < 10k clientes)
        
        if not orders_resp.data or not cust_resp.data:
            print("Nenhum dado de pedido ou cliente encontrado.")
            return {}
            
        # Prepara os DataFrames
        df_orders = pd.DataFrame(orders_resp.data)
        df_orders['salesChannel'] = df_orders['salesChannel'].fillna('PDV') 
        df_orders['createdAt'] = pd.to_datetime(df_orders['createdAt']) 
        
        df_customers = pd.DataFrame(cust_resp.data)
        df_customers['dateOfBirth'] = pd.to_datetime(df_customers['dateOfBirth'])
        
        print(f"Dados carregados: {len(df_orders)} pedidos, {len(df_customers)} clientes.")
        
        # Retorna um dicionário de DataFrames
        return {
            'orders': df_orders,
            'customers': df_customers
        }
        
    except Exception as e:
        print(f"Erro ao buscar dados (Cliente): {e}")
        return {}

# --- 3. Layout do Dashboard  ---
layout = html.Div(
    className='dashboard-container',
    children=[
        
       
        html.Header(
            className='dashboard-header',
            children=[ 
                html.H1("FIDELIZE Dashboard"),
                # --- BOTÃO DE LOGOUT ---
                html.Button(
                    "Logout",
                    id='button-logout',
                    className='export-button', 
                    style={'marginLeft': 'auto'} 
                )
            ]
        ),
        
        html.Div(
            className='dashboard-content',
            children=[
                html.H2("Dashboard do Restaurante"),
                
                # Barra de Filtros 
                html.Div(
                    className='filter-bar dashboard-card', 
                    children=[
                        html.Div(style={'flex': 1}, children=[
                            html.Label("Filtrar por Data:"),
                            dcc.DatePickerRange(id='filter-date-range', display_format='DD/MM/YYYY')
                        ]),
                        html.Div(style={'flex': 1}, children=[
                            html.Label("Filtrar por Canal de Venda:"),
                            dcc.Dropdown(id='filter-sales-channel', multi=True)
                        ])
                    ]
                ),
                
                # Botão de Exportação 
                html.Div(
                    style={'paddingBottom': '20px', 'textAlign': 'right'},
                    children=[
                        html.Button(
                            "Exportar Dados Filtrados (CSV)", 
                            id='button-export', 
                            className='export-button'
                        ),
                        dcc.Download(id='download-csv')
                    ]
                ),
                
                # Alertas 
                client_anomaly_alerts.layout,
                
                # KPIs 
                kpi_cards.layout,
                
                
                html.Div(
                    className='TabsContainer',
                    children=[
                        dcc.Tabs(
                            id='dashboard-tabs',
                            value='tab-1',
                            children=[
                                # Aba 1 
                                dcc.Tab(
                                    label='Visão Geral de Receita', value='tab-1',
                                    className='Tab', selected_className='Tab--selected',
                                    children=[
                                        html.Div(
                                            className='TabContent',
                                            children=[
                                                html.Div(
                                                    className='dashboard-grid-2-col',
                                                    children=[
                                                        revenue_graph.layout,
                                                        heatmap_graph.layout
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                # Aba 2 
                                dcc.Tab(
                                    label='Análise de Pedidos & ROI', value='tab-2',
                                    className='Tab', selected_className='Tab--selected',
                                    children=[
                                        html.Div(
                                            className='TabContent',
                                            children=[ donut_charts.layout ]
                                        )
                                    ]
                                ),
                                
                                # --- ABA 3 ---
                                dcc.Tab(
                                    label='Análise de Clientes', 
                                    value='tab-3',
                                    className='Tab',
                                    selected_className='Tab--selected',
                                    children=[
                                        html.Div(
                                            className='TabContent',
                                            children=[
                                               
                                                html.Div(
                                                    className='dashboard-grid-2-col',
                                                    children=[
                                                        client_acquisition_graph.layout,
                                                        client_age_graph.layout 
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),
                            ],
                            style={'height': '60px'},
                            colors={"border": "none", "primary": "none", "background": "none"}
                        )
                    ]
                )
            ]
        ),
        
        # O Store agora guarda um dicionário
        dcc.Store(id='store-client-data')
    ]
)

# --- 4. Callbacks  ---

# CALLBACK 1: Carregar dados 
@callback(
    Output('store-client-data', 'data'),
    Input('url', 'pathname')
)
def load_data_to_store(pathname):
    if pathname == '/client':
        data_dict = get_data_for_store() 
        if not data_dict:
            return no_update
            
        # Converte os DataFrames para JSON
        json_data = {
            'orders': data_dict['orders'].to_json(date_format='iso', orient='split'),
            'customers': data_dict['customers'].to_json(date_format='iso', orient='split')
        }
        return json_data # Guarda o dicionário de JSONs
    return no_update

# CALLBACK 2: Popular os filtros 
@callback(
    Output('filter-date-range', 'min_date_allowed'),
    Output('filter-date-range', 'max_date_allowed'),
    Output('filter-date-range', 'start_date'),
    Output('filter-date-range', 'end_date'),
    Output('filter-sales-channel', 'options'),
    Input('store-client-data', 'data')
)
def populate_filters(data):
    
    if not data or 'orders' not in data:
        return no_update

    df_orders = pd.read_json(StringIO(data['orders']), orient='split')
    df_orders['createdAt'] = pd.to_datetime(df_orders['createdAt'])

    min_date = df_orders['createdAt'].min().date()
    max_date = df_orders['createdAt'].max().date()
    
    all_channels = df_orders['salesChannel'].fillna('PDV').unique()
    channel_options = [{'label': channel, 'value': channel} for channel in all_channels]

    return min_date, max_date, min_date, max_date, channel_options

# CALLBACK 3: Exportar para CSV (ATUALIZADO)
@callback(
    Output('download-csv', 'data'),
    Input('button-export', 'n_clicks'),
    State('store-client-data', 'data'),
    State('filter-date-range', 'start_date'),
    State('filter-date-range', 'end_date'),
    State('filter-sales-channel', 'value'),
    prevent_initial_call=True
)
def export_csv(n_clicks, data, start_date, end_date, channels):
    # Lê a nova estrutura de dados
    if not data or 'orders' not in data or not start_date or not end_date:
        return no_update

    df = pd.read_json(StringIO(data['orders']), orient='split')
    df['createdAt'] = pd.to_datetime(df['createdAt'])
    
    start_date_obj = pd.to_datetime(start_date).date()
    end_date_obj = pd.to_datetime(end_date).date()

    df_filtered = df[
        (df['createdAt'].dt.date >= start_date_obj) &
        (df['createdAt'].dt.date <= end_date_obj)
    ]
    
    df_filtered['salesChannel'] = df_filtered['salesChannel'].fillna('PDV')
    if channels:
        df_filtered = df_filtered[df_filtered['salesChannel'].isin(channels)]
    
    return dcc.send_data_frame(
        df_filtered.to_csv,
        "cannoli_export_filtrado.csv",
        sep=';',
        index=False

    )
