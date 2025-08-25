# pages/dashboard.py

from dash import dcc, html

layout = html.Div(id='main-container', children=[
    # O dcc.Store para o tema foi movido para o app.py para melhor controle
    
    html.Div(className='header', children=[
        html.Button('🌙', id='theme-toggle-button', n_clicks=0, className='theme-toggle-button'),
        # Adicionada a className='logout-button'
        dcc.Link('Logout', href='/logout', className='logout-button'),
        
        html.Img(id='logo-img', src='/assets/logo-branca.png', className='logo'),
        html.H1(children='Dashboard de Análise de Leads'),
        html.P(children='Análise de performance de vendas e canais de aquisição.'),
    ]),
    
    html.Div(className='filter-container', children=[
        html.Label('Selecione o Mês:', style={'fontWeight': 'bold'}),
        dcc.Dropdown(id='filtro-mes')
    ]),

    html.Div(className='row kpi-row', children=[ # Adicionada a classe 'kpi-row'
        html.Div(className='card kpi-card', children=["Total de Leads", html.H3(id='kpi-total-leads')]),
        html.Div(className='card kpi-card', children=["Leads Qualificados", html.H3(id='kpi-qualificados')]),
        html.Div(className='card kpi-card', children=["Vendas Fechadas", html.H3(id='kpi-vendas')]),
        html.Div(className='card kpi-card', children=["Leads Desqualificados", html.H3(id='kpi-clientes-negociacao')]),
        html.Div(className='card kpi-card', children=["Faturamento Potencial", html.H3(id='kpi-faturamento')]),
    ]),
    html.Div(className='row', children=[
        html.Div(className='card graph-card', children=[dcc.Graph(id='grafico-origem', config={'displayModeBar': False})]),
        html.Div(className='card graph-card', children=[dcc.Graph(id='grafico-seguimento', config={'displayModeBar': False})]),
    ]),
    html.Div(className='row', children=[
        html.Div(className='card graph-card', children=[dcc.Graph(id='grafico-rd-crm')]),
        html.Div(className='card graph-card', children=[dcc.Graph(id='grafico-delegado')]),
    ]),
])