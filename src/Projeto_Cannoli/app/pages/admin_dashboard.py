import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output
import pandas as pd
from io import StringIO
from datetime import datetime, date

# Importa o nosso cliente Supabase
from app import auth
# --- Importa os componentes do Admin ---
from app.components import admin_funnel_graph
from app.components import admin_kpi_cards
from app.components import admin_suggestions_panel
from app.components import admin_simulation_tool
from app.components import admin_campaign_performance # <--- NOVO

# --- 1. Funções de Busca de Dados ---

def get_admin_data():
    supabase = auth.get_supabase_client()
    if not supabase:
        print("Erro: Admin não conseguiu obter o cliente Supabase.")
        return {}
    
    try:
        # 1. Busca Pedidos (orders)
        print("Admin: Buscando dados de 'orders'...")
        orders_resp = supabase.table('orders').select('*').limit(5000).execute()
        
        # 2. Busca Fila (campaign_queue)
        print("Admin: Buscando dados de 'campaign_queue'...")
        queue_resp = supabase.table('campaign_queue').select('*').limit(10000).execute()
        
        # 3. Busca Clientes (customers)
        print("Admin: Buscando dados de 'customers'...")
        customer_resp = supabase.table('customers').select('*').limit(10000).execute()
        
        # 4. Busca Campanhas (campaigns)
        print("Admin: Buscando dados de 'campaigns'...")
        campaign_resp = supabase.table('campaigns').select('*').limit(5000).execute()
        
        # Converte para JSON pronto para o dcc.Store
        data = {
            'orders': pd.DataFrame(orders_resp.data).to_json(date_format='iso', orient='split'),
            'customers': pd.DataFrame(customer_resp.data).to_json(date_format='iso', orient='split'),
            'campaign_queue': pd.DataFrame(queue_resp.data).to_json(date_format='iso', orient='split'),
            'campaigns': pd.DataFrame(campaign_resp.data).to_json(date_format='iso', orient='split')
        }
        return data

    except Exception as e:
        print(f"Erro ao buscar dados do Admin: {e}")
        return {}

# --- 3. Layout do Dashboard do Admin ---
layout = html.Div(
    className='dashboard-container',
    children=[
        
        html.Header(
            className='dashboard-header',
            children=[ 
                html.H1("FIDELIZE Dashboard - Painel Admin"),
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
                
                html.H2("Visão Geral da Plataforma"),
                
                
                html.Div(
                    className='filter-bar dashboard-card', 
                    children=[
                        html.Div(style={'flex': 1}, children=[
                            html.Label("Filtrar por Data:"),
                            dcc.DatePickerRange(
                                id='admin-filter-date-range',
                                display_format='DD/MM/YYYY',
                            )
                        ]),
                        html.Div(style={'flex': 1}, children=[
                            html.Label("Filtrar por Loja (Store ID):"),
                            dcc.Dropdown(
                                id='admin-filter-store',
                                multi=True
                            )
                        ])
                    ]
                ),
                
                admin_kpi_cards.layout,

               
                html.Div(
                    className='TabsContainer',
                    children=[
                        dcc.Tabs(
                            id='admin-tabs',
                            value='tab-campaigns',
                            children=[
                                
                                # --- Aba 1: Desempenho  ---
                                dcc.Tab(
                                    label='Desempenho de Campanhas', 
                                    value='tab-campaigns',
                                    className='Tab',
                                    selected_className='Tab--selected',
                                    children=[
                                        html.Div(
                                            className='TabContent',
                                            children=[
                                                # Grelha 1
                                                html.Div(
                                                    className='dashboard-grid-2-col',
                                                    children=[
                                                        admin_funnel_graph.layout,
                                                        admin_suggestions_panel.layout
                                                    ]
                                                ),
                                                # Novo Gráfico (abaixo da grelha)
                                                admin_campaign_performance.layout 
                                            ]
                                        )
                                    ]
                                ),
                                
                                # --- Aba 2: Simulações (igual a antes) ---
                                dcc.Tab(
                                    label='Simulação de Campanhas', 
                                    value='tab-simulations',
                                    className='Tab',
                                    selected_className='Tab--selected',
                                    children=[
                                        html.Div(
                                            className='TabContent',
                                            children=[
                                                admin_simulation_tool.layout
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
        
        dcc.Store(id='store-admin-data')
    ]
)

# --- 4. Callbacks (Callback de carregamento e filtros) ---

@callback(
    Output('store-admin-data', 'data'),
    Input('url', 'pathname') 
)
def load_admin_data_to_store(pathname):
    if pathname == '/admin':
        data = get_admin_data()
        if not data:
            return no_update
        return data
    return no_update

@callback(
    Output('admin-filter-date-range', 'min_date_allowed'),
    Output('admin-filter-date-range', 'max_date_allowed'),
    Output('admin-filter-date-range', 'start_date'),
    Output('admin-filter-date-range', 'end_date'),
    Output('admin-filter-store', 'options'),
    Input('store-admin-data', 'data')
)
def populate_admin_filters(data):
    if not data or 'orders' not in data or 'campaigns' not in data:
        return no_update

    df_orders = pd.read_json(StringIO(data['orders']), orient='split')
    df_orders['createdAt'] = pd.to_datetime(df_orders['createdAt'])
    df_campaigns = pd.read_json(StringIO(data['campaigns']), orient='split')

    min_date = df_orders['createdAt'].min().date()
    max_date = df_orders['createdAt'].max().date()
    
    all_stores = df_campaigns['storeId'].fillna('Loja Desconhecida').unique()
    store_options = [{'label': store, 'value': store} for store in all_stores]


    return min_date, max_date, min_date, max_date, store_options
