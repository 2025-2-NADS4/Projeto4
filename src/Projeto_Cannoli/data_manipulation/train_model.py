import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from datetime import timedelta

print("--- Iniciando Script de Treino do Modelo de Propensão (v3 - Corrigido) ---")

# --- 1. Carregar os Dados (COM OS NOVOS NOMES) ---
try:
    df_orders = pd.read_csv("Order_FIXED.csv", sep=';')
    df_customers = pd.read_csv("Customer_FIXED.csv", sep=';')
    df_queue = pd.read_csv("CampaignQueue_v_FINAL.csv", sep=';')
    print("Dados (FIXED/FINAL) carregados com sucesso.")
except FileNotFoundError:
    print("Erro: Verifique se os ficheiros (Order_FIXED, Customer_FIXED, CampaignQueue_v_FINAL) estão no mesmo diretório.")
    exit()

# --- 2. Engenharia de Features ---
print("Iniciando engenharia de features...")

# Converte datas para datetime
df_orders['createdAt'] = pd.to_datetime(df_orders['createdAt'])
df_queue['sendAt'] = pd.to_datetime(df_queue['sendAt'])

# 2.1. Identificar o público-alvo (Apenas quem 'Leu')
df_target_audience = df_queue[df_queue['status'] == 4]
print(f"Total de mensagens lidas (público-alvo): {len(df_target_audience)}")

# 2.2. Definir a "Janela de Conversão"
conversion_window = timedelta(days=7)

# 2.3. Verificar a Conversão (Label = 'converted')
conversion_list = []
for index, row in df_target_audience.iterrows():
    customer_id = row['customerId']
    read_date = row['sendAt']
    
    if pd.isna(read_date):
        conversion_list.append(0)
        continue

    conversion = df_orders[
        (df_orders['customer'] == customer_id) &
        (df_orders['createdAt'] > read_date) &
        (df_orders['createdAt'] <= read_date + conversion_window)
    ]
    
    if not conversion.empty:
        conversion_list.append(1)
    else:
        conversion_list.append(0)

df_target_audience['converted'] = conversion_list
print(f"Total de conversões encontradas: {sum(conversion_list)}")

# 2.4. Juntar com os dados do Cliente
# (Causa a colisão 'status' -> 'status_x', 'status_y')
df_model_data = df_target_audience.merge(
    df_customers[['id', 'status']],
    left_on='customerId',
    right_on='id'
)

# --- 3. Preparar Dados para o Modelo ---
print("Preparando dados para o scikit-learn...")

# 3.1. Correção do KeyError (usando 'status_y')
df_model_data = df_model_data[['status_y', 'converted']]
df_model_data = df_model_data.rename(columns={'status_y': 'status'})

# 3.2. Criar Dummies
X = pd.get_dummies(df_model_data['status'], prefix='status', drop_first=True)
y = df_model_data['converted']

# (Verifica se a coluna 'status_2' foi criada. Se só houver status 1, ela não existirá)
if 2 not in df_model_data['status'].unique():
    print("AVISO: Os seus dados de treino só contêm clientes com 'status=1'.")
    # Adiciona a coluna 'status_2' preenchida com 0
    X['status_2'] = 0
else:
    # Renomeia 'status_2.0' para 'status_2' se o Pandas a criar assim
    if 'status_2.0' in X.columns:
        X = X.rename(columns={'status_2.0': 'status_2'})

print(f"Colunas de treino (Features): {X.columns.to_list()}")

# 3.3. Dividir em Treino/Teste
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# --- 4. Treinar o Modelo de Regressão Logística ---
print("Treinando o modelo de Regressão Logística...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression(random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"Acurácia do modelo nos dados de teste: {accuracy * 100:.2f}%")

# --- 5. Gerar as Previsões (O Insight da IA) ---
print("\n--- Previsões do Modelo de Propensão (Resultados Finais) ---")

# 5.1. Criar os "novos dados" para prever
# --- A CORREÇÃO DO ValueError ESTÁ AQUI ---
# 0 = Cliente Ativo (status_2 = 0)
# 1 = Cliente Inativo (status_2 = 1)
# O nome da coluna deve ser 'status_2', e não 'status_2.0'
X_predict = pd.DataFrame({'status_2': [0, 1]})
# --- FIM DA CORREÇÃO ---

try:
    X_predict_scaled = scaler.transform(X_predict)
    
    # 5.2. Prever as probabilidades
    probabilities = model.predict_proba(X_predict_scaled)
    
    prob_ativo = probabilities[0][1] # Probabilidade de 'status_2' = 0 (Ativo)
    prob_inativo = probabilities[1][1] # Probabilidade de 'status_2' = 1 (Inativo)
    
    print(f"Probabilidade de Conversão (Clientes Ativos): {prob_ativo * 100:.1f}%")
    print(f"Probabilidade de Conversão (Clientes Inativos): {prob_inativo * 100:.1f}%")

except Exception as e:
    print(f"\nERRO AO TENTAR PREVER: {e}")
    print("Verifique se as colunas em 'X_predict' (status_2) correspondem às colunas de treino.")