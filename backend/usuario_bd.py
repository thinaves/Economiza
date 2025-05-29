from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os

app - Flask(__name__)
# Carrega as variáveis de ambiente do arquivo .env (A qual foi criado anteriormente e contém as credenciais do banco de dados)

from dotenv import load_dotenv
load_dotenv()

# Configurações do banco de dados
conn = mysql.connector.connect(
    host = os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cursor = conn.cursor()

@app.router('/')
def home():
    return "API está funcionando!"
# Rota para adicionar um novo usuário
@app.route('/adicionar_usuario', methods=['POST'])
def adicionar_usuario():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    try:
        cursor.execute("INSERT INTO usuarios (email, senha) VALUES (%s, %s)", (email, senha))
        conn.commit()
        return jsonify({"mensagem": "Usuário adicionado com sucesso!"}), 201
    except Error as e:
        return jsonify({"erro": str(e)}), 500
# Dados do novo usuário
novo_usuario = ("novousuario@exemplo.com", "senha123")

# Inserindo no banco
cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", novo_usuario)
conn.commit()

print("Usuário adicionado com sucesso!")

# Fecha a conexão
conn.close()
