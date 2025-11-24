# app/pages/login.py (Removido dcc.Location)
import dash
from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output, State
from flask import session
from app import auth

# --- CORES PERSONALIZADAS ---
ACCENT_COLOR = '#6C4549' 
PRIMARY_BG = '#282828' 
CARD_BG = '#3c3c3c' 
TEXT_COLOR = '#f0f0f0' 
CANNOLI_COLOR = '#FFB300' 

# Layout da página de Login
layout = html.Div(
    className='auth-container theme-dark', 
    children=[
        html.Div(
            className='login-card', 
            style={'backgroundColor': CARD_BG, 'color': TEXT_COLOR},
            children=[
                html.H1(
                    style={'marginBottom': '30px', 'textAlign': 'center'},
                    children=[
                        html.Span("FIDELIZE", style={'color': CANNOLI_COLOR}),
                        html.Span(" Plataforma", style={'color': TEXT_COLOR})
                    ]
                ),
                
                dcc.Input(
                    id='input-email', type='email', placeholder='Email (ex: admin@fidelize.com)',
                    style={'width': '100%', 'padding': '10px', 'marginBottom': '15px', 
                           'borderRadius': '5px', 'border': f'1px solid {ACCENT_COLOR}',
                           'backgroundColor': PRIMARY_BG, 'color': TEXT_COLOR}
                ),
                dcc.Input(
                    id='input-password', type='password', placeholder='Password',
                    style={'width': '100%', 'padding': '10px', 'marginBottom': '30px', 
                           'borderRadius': '5px', 'border': f'1px solid {ACCENT_COLOR}',
                           'backgroundColor': PRIMARY_BG, 'color': TEXT_COLOR}
                ),
                
                html.Button(
                    'Login', id='button-login', n_clicks=0,
                    style={'width': '100%', 'padding': '10px', 'backgroundColor': ACCENT_COLOR,
                           'color': 'white', 'border': 'none', 'borderRadius': '5px',
                           'cursor': 'pointer', 'fontWeight': 'bold'}
                ),
                
                html.Div(id='output-login-error', style={'marginTop': '20px', 'textAlign': 'center', 'color': 'red'}),
                
            ]
        ),
    ]
)

