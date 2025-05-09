from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

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
    app.run(debug=True, host='127.0.0.1', port=5000)