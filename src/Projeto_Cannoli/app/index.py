from dash import dcc, html, callback, no_update
from dash.dependencies import Input, Output, State
from flask import session 

from .app import app
from .pages import login
from .pages import client_dashboard
from .pages import admin_dashboard
from . import auth

# --- O layout principal (igual a antes) ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# --- O callback de rotas (MANTIDO) ---
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    
    user_role = session.get('user_role')
    
    if not user_role:
        if pathname == '/login':
            return login.layout
        else:
            return dcc.Location(pathname='/login', id='redirect-to-login')
        
    elif user_role == 'admin':
        if pathname == '/admin':
            return admin_dashboard.layout
        else:
            return dcc.Location(pathname='/admin', id='redirect-admin')
            
    elif user_role == 'client':
        if pathname == '/client':
            return client_dashboard.layout
        else:
            return dcc.Location(pathname='/client', id='redirect-client')
            
    else:
        return login.layout 


# --- CALLBACK DE LOGOUT (CORREÇÃO DE OUTPUT) ---
# Usamos o dcc.Location do layout principal para a saída
@callback(
    Output('url', 'pathname', allow_duplicate=True), # Saída para o dcc.Location do layout principal
    Input('button-logout', 'n_clicks'),
    prevent_initial_call=True
)
def process_logout(n_clicks):
    if n_clicks is None or n_clicks == 0:
        return no_update
        
    if 'user_role' in session:
        del session['user_role']
    
    # Redireciona para a página de login
    return '/login'

# --- O callback de login (CORRIGIDO PARA USAR O NOVO OUTPUT) ---
@callback(
    Output('output-login-error', 'children'),
    Output('url', 'pathname'), # <--- AGORA USA O 'url' COMO OUTPUT
    Input('button-login', 'n_clicks'),
    State('input-email', 'value'),
    State('input-password', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    if n_clicks > 0:
        if not email or not password:
            return "Por favor, insira o email e a password.", no_update
            
        success, message, user_role = auth.sign_in_user(email, password)
        
        if success:
            session['user_role'] = user_role
            return "", f"/{user_role}" 
        else:
            return message, no_update
            
    return no_update, no_update