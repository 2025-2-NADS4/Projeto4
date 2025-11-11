# app/auth.py (Versão Simples)
import os
from supabase import create_client, Client
from dotenv import load_dotenv
# NENHUMA CLASSE UserMixin ou User aqui

# Carrega as variáveis de ambiente
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("ERRO: SUPABASE_URL ou SUPABASE_KEY não encontradas no .env.")
    supabase = None
else:
    try:
        supabase: Client = create_client(url, key)
        print("Conexão com Supabase estabelecida com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar ao Supabase: {e}")
        supabase = None

def get_supabase_client():
    return supabase

def sign_in_user(email, password):
    client = get_supabase_client()
    if not client:
        return False, "Conexão com o Supabase não estabelecida.", None

    try:
        session = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Determina o papel do utilizador para a sessão
        user_role = 'admin' if session.user.email == "admin@cannoli.com" else 'client'

        return True, "", user_role # Retorna o papel
    
    except Exception as e:
        return False, "E-mail ou senha inválidos.", None