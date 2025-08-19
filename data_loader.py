import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

# --- CONFIGURAÇÃO DA AUTENTICAÇÃO ---
# Define o escopo de permissões. Precisamos de acesso às APIs do Sheets e Drive.
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Carrega as credenciais do arquivo JSON gerado.
# Certifique-se de que o arquivo 'credentials.json' está na mesma pasta.
try:
    CREDS = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', SCOPE)
    CLIENT = gspread.authorize(CREDS)
    print("Autenticação com Google Sheets realizada com sucesso!")
except FileNotFoundError:
    print("Erro: Arquivo 'credentials.json' não encontrado. Siga os passos da Fase 1.")
    exit()
except Exception as e:
    print(f"Ocorreu um erro durante a autenticação: {e}")
    exit()

# --- FUNÇÃO PARA CARREGAR DADOS ---
def carregar_dados_mes(nome_planilha: str, nome_aba: str) -> pd.DataFrame:
    """
    Conecta a uma planilha do Google Sheets, lê os dados de uma aba específica
    e os retorna como um DataFrame do Pandas.
    
    Args:
        nome_planilha (str): O nome exato da sua planilha no Google Sheets.
        nome_aba (str): O nome exato da aba (mês) que deseja carregar.

    Returns:
        pd.DataFrame: Um DataFrame contendo os dados da aba, ou um DataFrame vazio em caso de erro.
    """
    try:
        print(f"Tentando abrir a planilha: '{nome_planilha}'...")
        sheet = CLIENT.open(nome_planilha).worksheet(nome_aba)
        
        print(f"Lendo dados da aba: '{nome_aba}'...")
        dados = sheet.get_all_records()
        
        # Converte os dados para um DataFrame do Pandas para fácil manipulação
        df = pd.DataFrame(dados)
        
        print("Dados carregados com sucesso!")
        return df

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Erro: Planilha '{nome_planilha}' não encontrada. Verifique o nome e o compartilhamento.")
        return pd.DataFrame()
    except gspread.exceptions.WorksheetNotFound:
        print(f"Erro: Aba '{nome_aba}' não encontrada na planilha.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
        return pd.DataFrame()

# --- TESTE DA FUNÇÃO ---
if __name__ == '__main__':
    # !! SUBSTITUA PELO NOME EXATO DA SUA PLANILHA !!
    NOME_DA_PLANILHA = "[3P] Controle de Leads -  Nicopel" 
    
    # Vamos testar carregando a aba de 'Julho'
    df_julho = carregar_dados_mes(NOME_DA_PLANILHA, 'Julho')
    
    if not df_julho.empty:
        print("\n--- Amostra dos Dados Carregados (5 primeiras linhas) ---")
        print(df_julho.head())
        print("\n--- Informações do DataFrame ---")
        df_julho.info()
        
def listar_abas_meses(nome_planilha: str) -> list:
    """
    Lista todas as abas de uma planilha, excluindo 'Leads sem retorno'.
    """
    try:
        abas = CLIENT.open(nome_planilha).worksheets()
        nomes_abas = [aba.title for aba in abas if aba.title != "Leads sem retorno"]
        print(f"Abas de meses encontradas: {nomes_abas}")
        return nomes_abas
    except Exception as e:
        print(f"Ocorreu um erro ao listar as abas: {e}")
        return []