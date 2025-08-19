# pages/login.py

from dash import dcc, html

layout = html.Div(className='login-background', children=[
    html.Div(className='login-container', children=[
        html.Img(src='/assets/logo.png', className='login-logo'),
        html.H2('Acesso ao Dashboard'),
        html.P('Insira suas credenciais para continuar.'),
        
        dcc.Input(
            id='input-username',
            type='text',
            placeholder='Usuário',
            className='login-input'
        ),
        dcc.Input(
            id='input-password',
            type='password',
            placeholder='Senha',
            className='login-input'
        ),
        
        html.Button('Login', id='btn-login', n_clicks=0, className='login-button'),
        
        # Div para exibir mensagens de erro
        html.Div(id='login-error-message', className='login-error')
    ])
])