# app.py - Orquestrador Principal (VERSÃO FINAL E CORRIGIDA)

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
import traceback

from pages import login, dashboard 
from data_loader import carregar_dados_mes, listar_abas_meses

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard de Leads"

# --- CREDENCIAIS (SIMPLES) ---
VALID_USERNAME_PASSWORD = {'admin': '1234'}

# --- LÓGICA DE NEGÓCIO E AUXILIARES ---
NOME_DA_PLANILHA = "[3P] Controle de Leads - Nicopel"
lista_meses = listar_abas_meses(NOME_DA_PLANILHA)

def get_mes_vigente():
    mapa_meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    mes_atual_num = datetime.datetime.now().month
    mes_atual_nome = mapa_meses.get(mes_atual_num)
    if mes_atual_nome in lista_meses:
        return mes_atual_nome
    elif lista_meses:
        return lista_meses[-1]
    return None

def limpar_dados(df: pd.DataFrame):
    if 'Valor do pedido' not in df.columns: return df
    df['Valor do pedido'] = df['Valor do pedido'].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
    df['Valor do pedido'] = pd.to_numeric(df['Valor do pedido'], errors='coerce').fillna(0)
    return df

def find_column_name(columns, possible_names):
    for name in possible_names:
        if name in columns:
            return name
    return None

# --- LAYOUT PRINCIPAL (ROTEADOR) ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Store(id='theme-store', storage_type='session', data='light'), # Armazena o tema
    html.Div(id='page-content')
])

# --- CALLBACKS DE NAVEGAÇÃO E LOGIN ---
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('session-store', 'data')
)
def display_page(pathname, session_data):
    session_data = session_data or {}
    if pathname == '/dashboard' and session_data.get('authenticated'):
        return dashboard.layout
    else:
        return login.layout

@app.callback(
    Output('url', 'pathname'),
    Output('login-error-message', 'children'),
    Output('session-store', 'data'),
    Input('btn-login', 'n_clicks'),
    State('input-username', 'value'),
    State('input-password', 'value'),
    State('session-store', 'data')
)
def handle_login(n_clicks, username, password, session_data):
    if n_clicks is None or n_clicks == 0:
        return dash.no_update, "", {}
    session_data = session_data or {}
    if username in VALID_USERNAME_PASSWORD and password == VALID_USERNAME_PASSWORD[username]:
        session_data['authenticated'] = True
        return '/dashboard', "", session_data
    else:
        return dash.no_update, "Usuário ou senha inválidos.", session_data
        
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Output('session-store', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def handle_logout(pathname):
    if pathname == '/logout':
        return '/', {'authenticated': False}
    return dash.no_update, dash.no_update

# --- CALLBACKS DO DASHBOARD ---
@app.callback(
    Output('filtro-mes', 'options'),
    Output('filtro-mes', 'value'),
    Input('page-content', 'children')
)
def populate_dropdown(page_layout):
    return [{'label': mes, 'value': mes} for mes in lista_meses], get_mes_vigente()

# --- LÓGICA DE TEMA CORRIGIDA ---
@app.callback(
    Output('theme-store', 'data'),
    Input('theme-toggle-button', 'n_clicks'),
    State('theme-store', 'data'),
    prevent_initial_call=True
)
def update_theme_store(n_clicks, current_theme):
    return 'dark' if current_theme == 'light' else 'light'

@app.callback(
    Output('main-container', 'className'),
    Output('theme-toggle-button', 'children'),
    Output('logo-img', 'src'),
    Input('theme-store', 'data')
)
def apply_theme_to_ui(theme):
    if theme == 'dark':
        # No tema escuro, mostre o sol para voltar ao claro
        return 'theme-dark', '☀️', '/assets/logo-branca.png'
    else:
        # No tema claro, mostre a lua para ir para o escuro
        return 'theme-light', '🌙', '/assets/logo.png'

# Callback principal de atualização do dashboard
@app.callback(
    Output('kpi-total-leads', 'children'),
    Output('kpi-qualificados', 'children'),
    Output('kpi-vendas', 'children'),
    Output('kpi-clientes-negociacao', 'children'),
    Output('kpi-faturamento', 'children'),
    Output('grafico-origem', 'figure'),
    Output('grafico-seguimento', 'figure'),
    Output('grafico-rd-crm', 'figure'),
    Output('grafico-delegado', 'figure'),
    Input('filtro-mes', 'value'),
    Input('theme-store', 'data')
    
)
def update_dashboard_data(mes_selecionado, theme):
    try:
        if not mes_selecionado:
            raise dash.exceptions.PreventUpdate

        template_visual = 'plotly_dark' if theme == 'dark' else 'seaborn'
        df = carregar_dados_mes(NOME_DA_PLANILHA, mes_selecionado)

        if df.empty:
            empty_figure = go.Figure(layout_title_text="Dados não disponíveis para este mês")
            empty_figure.update_layout(template=template_visual)
            return 0, 0, 0, 0, "R$ 0,00", empty_figure, empty_figure, empty_figure

        df.columns = df.columns.str.strip()
        df = limpar_dados(df)

        # --- Bloco de KPIs com lógica final e consistente ---
        total_leads = len(df)
        qualificados = df[df['Qualificado'].str.strip().str.title() == 'Sim'].shape[0]
        vendas_fechadas = df[df['Venda fechada?'].str.strip().str.title() == 'Sim'].shape[0]
        clientes_em_negociacao = df[df['Qualificado'].str.strip().str.title() == 'Não'].shape[0]
        
        try:
            faturamento = float(df['Valor do pedido'].sum())
        except (ValueError, TypeError):
            faturamento = 0.0
        faturamento_formatado = f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # --- Fim do Bloco de KPIs ---

        df_origem = df['Onde nos encontrou?'].value_counts().reset_index()
        fig_origem = px.pie(df_origem, names='Onde nos encontrou?', values='count', title=f'Origem dos Leads - {mes_selecionado}', template=template_visual)
        
        coluna_seguimento = find_column_name(df.columns, ['Seguimento'])
        if coluna_seguimento:
            df_seguimento = df[coluna_seguimento].value_counts().reset_index()
            fig_seguimento = px.bar(df_seguimento, x=coluna_seguimento, y='count', title=f'Análise por Seguimento - {mes_selecionado}', labels={'count': 'Número de Leads', coluna_seguimento: 'Seguimento'}, template=template_visual)
        else:
            fig_seguimento = go.Figure(layout_title_text=f"Coluna 'Seguimento' não encontrada").update_layout(template=template_visual)
        
        coluna_crm = find_column_name(df.columns, ['RD CRM', 'CRM'])
        if coluna_crm:
            df_crm = df[coluna_crm].value_counts().reset_index()
            fig_crm = px.pie(df_crm, names=coluna_crm, values='count', title=f'CRM vs. Outros - {mes_selecionado}', template=template_visual)
        else:
            fig_crm = go.Figure(layout_title_text=f"Coluna 'CRM' não encontrada").update_layout(template=template_visual)
            
        # Adicione este bloco depois da lógica do gráfico de CRM

    # --- LÓGICA PARA O GRÁFICO DE DELEGAÇÃO ---
        coluna_delegado = find_column_name(df.columns, ['Delegado para'])

        if coluna_delegado:
            # Filtra dados onde o valor do pedido é maior que zero para um gráfico mais limpo
            df_delegado = df[(df[coluna_delegado].notna()) & (df[coluna_delegado] != '') & (df['Valor do pedido'] > 0)]
            fig_delegado = px.strip(
                df_delegado,
                x='Valor do pedido',
                y=coluna_delegado,
                title=f'Distribuição de Leads Delegados - {mes_selecionado}',
                labels={'Valor do pedido': 'Valor do Pedido (R$)', coluna_delegado: 'Delegado Para'},
                template=template_visual,
                color=coluna_delegado # Colore os pontos por pessoa
            )
        else:
            fig_delegado = go.Figure(layout_title_text=f"Coluna 'Delegado para' não encontrada")
            fig_delegado.update_layout(template=template_visual)
        # --- FIM DA LÓGICA ---
            
            for fig in [fig_origem, fig_seguimento, fig_crm, fig_delegado]:
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='darkgrey' if theme == 'dark' else '#343a40')
        
        return (total_leads, qualificados, vendas_fechadas, clientes_em_negociacao, faturamento_formatado, fig_origem, fig_seguimento, fig_crm, fig_delegado)

    except Exception as e:
        print("\n" + "="*50)
        print(f"Ocorreu um ERRO ao processar o mês: '{mes_selecionado}'")
        traceback.print_exc()
        print("="*50 + "\n")
        
        empty_figure = go.Figure(layout_title_text=f"Erro ao carregar dados de {mes_selecionado}")
        return "Erro", "Erro", "Erro", "Erro", "Erro", empty_figure, empty_figure, empty_figure