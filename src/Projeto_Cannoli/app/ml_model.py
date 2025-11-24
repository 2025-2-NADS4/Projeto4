import pandas as pd
from io import StringIO
import numpy as np


PREDICTED_RATES = {
    'inativos': 11.6, 
    'ativos': 3.0     
}


def get_ml_predictions(target_audience, data):

    if not data or 'customers' not in data or 'orders' not in data:
        print("ML Model: Faltam dados (customers ou orders) no store.")
        return 0, 0, 0 
        
    try:
        df_customers = pd.read_json(StringIO(data['customers']), orient='split')
        df_orders = pd.read_json(StringIO(data['orders']), orient='split')
    except Exception as e:
        print(f"ML Model: Erro ao ler JSON dos dados: {e}")
        return 0, 0, 0

    # --- Lógica de Previsão ---
    
    if target_audience == 'inativos':
        # Clientes Inativos (status=2)
        df_target = df_customers[df_customers['status'] == 2]
        predicted_conversion_rate = PREDICTED_RATES['inativos']
        
    elif target_audience == 'ativos':
        # Clientes Ativos (status=1)
        df_target = df_customers[df_customers['status'] == 1]
        predicted_conversion_rate = PREDICTED_RATES['ativos']
        
    else: # Fallback
        return 0, 0, 0

    # 1. Encontra o Público-Alvo
    audience_count = len(df_target)
    if audience_count == 0:
        return 0, 0, 0
        
    # 2. Encontra o Ticket Médio Real desse público
    target_ids = df_target['id'].unique()
    df_orders_target = df_orders[
        (df_orders['customer'].isin(target_ids)) &
        (df_orders['status'] == 'CONCLUDED')
    ]
    
    if df_orders_target.empty:
        # Se este público não tem pedidos, usa a média global
        avg_ticket = df_orders[
            df_orders['status'] == 'CONCLUDED'
        ]['totalAmount'].mean()
    else:
        avg_ticket = df_orders_target['totalAmount'].mean()

    
    if pd.isna(avg_ticket):
        avg_ticket = 65.0
        

    return audience_count, predicted_conversion_rate, avg_ticket
