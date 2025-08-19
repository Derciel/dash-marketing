# index.py
from app import app

# Este é o ponto de entrada da sua aplicação.
# O comando 'server' é necessário para a implantação em servidores web.
server = app.server

if __name__ == '__main__':
    # Para rodar localmente, use o comando: python index.py
    app.run_server(debug=True)