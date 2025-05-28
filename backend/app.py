from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Função para conectar ao banco de dados MySQL
def conectar_banco():
    return mysql.connector.connect(
        host= os.getenv('DB_HOST'),
        database = os.getenv('DB_NAME'),
        password = os.getenv('DB_PASSWORD'),
        user = os.getenv('DB_USER')
    )
# Verificar se a conexão foi bem-sucedida
@app.router('/')

def home():
    return "API está funcionando!"

@app.route('/enviar_nota', methods=['POST'])
def receber_nota():
    dados = request.get_json()
    link = dados.get('link') if dados else None
    if not link:
        return jsonify({"erro": "Link não enviado"}), 400
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS notas_fiscais (id INT AUTO_INCREMENT PRIMARY KEY, link VARCHAR(255))''')
        cursor.execute("INSERT INTO notas_fiscais (link) VALUES (%s)", (link,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Nota fiscal salva com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# Rota de teste
@app.route('/')
def home():
    return "API está funcionando!"

# Rota para receber o link da Nota Fiscal
@app.route('/enviar_nota', methods=['POST'])
def receber_nota():
    dados = request.get_json()  # Corrigido aqui
    link = dados.get('link') if dados else None

    if not link:
        return jsonify({"erro": "Link não enviado"}), 400

    # Conectar e salvar o link no banco de dados
    try:
        conn = sqlite3.connect('dados_nfce.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS notas_fiscais (id INTEGER PRIMARY KEY AUTOINCREMENT, link TEXT)''')
        cursor.execute("INSERT INTO notas_fiscais (link) VALUES (?)", (link,))
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Nota fiscal salva com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rodar o app apenas se for o arquivo principal
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)