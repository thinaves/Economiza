from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import hashlib
import re
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# 🥚 EASTER EGG: Comentário secreto para os devs
"""
🎉 PARABÉNS! Você encontrou o Easter Egg no backend! 🎉

    ____                            _            
   |  __|                          (_)           
   | |__   ___  ___  _ __   ___  _ __ ___ __ _ 
   |  __| / __|/ _ \| '_ \ / _ \| '_ ` _ \/ _` |
   | |___| (__| (_) | | | | (_) | | | | | (_| |
   |______\___|\___/|_| |_|\___/|_| |_| |_\__,_|
                                                
Sistema de Economia Inteligente - Versão 2.0
Desenvolvido com 💚 pela equipe mais incrível!

Mensagem secreta: "Bugs são apenas features não documentadas!" 😄
"""

# Função para conectar ao banco de dados
def conectar_banco():
    try:
        return mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'economiza'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

# Função para criar tabelas se não existirem
def criar_tabelas():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        try:
            # Tabela de usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    telefone VARCHAR(15),
                    senha_hash VARCHAR(255) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de notas fiscais
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notas_fiscais (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario_id INT,
                    link VARCHAR(500) NOT NULL,
                    numero_nota VARCHAR(50),
                    data_compra DATE,
                    valor_total DECIMAL(10,2),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            
            # Tabela de produtos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nota_fiscal_id INT,
                    nome VARCHAR(200) NOT NULL,
                    preco DECIMAL(10,2) NOT NULL,
                    quantidade INT DEFAULT 1,
                    categoria VARCHAR(100),
                    FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id)
                )
            """)
            
            conn.commit()
            print("✅ Tabelas criadas com sucesso!")
            
        except Error as e:
            print(f"❌ Erro ao criar tabelas: {e}")
        finally:
            cursor.close()
            conn.close()

# Função para hash de senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função para validar email
def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Função para validar CPF (básico)
def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

# ROTAS
@app.route('/')
def home():
    return jsonify({
        "mensagem": "🎉 API Economiza está funcionando!",
        "versao": "2.0",
        "status": "online",
        "easter_egg": "Procure pelos comentários no código! 🥚"
    })

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    try:
        dados = request.get_json()
        
        # Validação dos dados
        nome = dados.get('nome', '').strip()
        email = dados.get('email', '').strip().lower()
        cpf = dados.get('cpf', '').strip()
        telefone = dados.get('telefone', '').strip()
        senha = dados.get('senha', '').strip()
        
        # Verificações
        if not all([nome, email, cpf, senha]):
            return jsonify({"erro": "Todos os campos obrigatórios devem ser preenchidos"}), 400
        
        if not validar_email(email):
            return jsonify({"erro": "Email inválido"}), 400
        
        if not validar_cpf(cpf):
            return jsonify({"erro": "CPF inválido"}), 400
        
        if len(senha) < 6:
            return jsonify({"erro": "Senha deve ter pelo menos 6 caracteres"}), 400
        
        # Conectar ao banco
        conn = conectar_banco()
        if not conn:
            return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
        cursor = conn.cursor()
        
        # Verificar se usuário já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s OR cpf = %s", (email, cpf))
        if cursor.fetchone():
            return jsonify({"erro": "Usuário já existe com este email ou CPF"}), 409
        
        # Inserir novo usuário
        senha_hash = hash_senha(senha)
        cursor.execute("""
            INSERT INTO usuarios (nome, email, cpf, telefone, senha_hash) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, email, cpf, telefone, senha_hash))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        return jsonify({
            "mensagem": "✅ Usuário cadastrado com sucesso!",
            "user_id": user_id,
            "nome": nome,
            "email": email
        }), 201
        
    except Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    try:
        dados = request.get_json()
        
        login_field = dados.get('login', '').strip().lower()  # pode ser email, cpf ou telefone
        senha = dados.get('senha', '').strip()
        
        if not all([login_field, senha]):
            return jsonify({"erro": "Login e senha são obrigatórios"}), 400
        
        conn = conectar_banco()
        if not conn:
            return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
        cursor = conn.cursor()
        senha_hash = hash_senha(senha)
        
        # Buscar usuário por email, CPF ou telefone
        cursor.execute("""
            SELECT id, nome, email FROM usuarios 
            WHERE (email = %s OR cpf = %s OR telefone = %s) AND senha_hash = %s
        """, (login_field, login_field, login_field, senha_hash))
        
        usuario = cursor.fetchone()
        
        if usuario:
            return jsonify({
                "mensagem": "✅ Login realizado com sucesso!",
                "user_id": usuario[0],
                "nome": usuario[1],
                "email": usuario[2]
            }), 200
        else:
            return jsonify({"erro": "Credenciais inválidas"}), 401
            
    except Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/enviar_nota', methods=['POST'])
def enviar_nota():
    try:
        dados = request.get_json()
        
        user_id = dados.get('user_id')
        link = dados.get('link', '').strip()
        numero_nota = dados.get('numero_nota', '').strip()
        data_compra = dados.get('data_compra')
        valor_total = dados.get('valor_total')
        
        if not all([user_id, link]):
            return jsonify({"erro": "User ID e link são obrigatórios"}), 400
        
        # Validar se o link parece ser uma URL válida
        if not link.startswith(('http://', 'https://')):
            return jsonify({"erro": "Link deve ser uma URL válida"}), 400
        
        conn = conectar_banco()
        if not conn:
            return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
        cursor = conn.cursor()
        
        # Verificar se usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Inserir nota fiscal
        cursor.execute("""
            INSERT INTO notas_fiscais (usuario_id, link, numero_nota, data_compra, valor_total) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, link, numero_nota, data_compra, valor_total))
        
        conn.commit()
        nota_id = cursor.lastrowid
        
        return jsonify({
            "mensagem": "✅ Nota fiscal salva com sucesso!",
            "nota_id": nota_id,
            "link": link
        }), 201
        
    except Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/listar_notas/<int:user_id>', methods=['GET'])
def listar_notas(user_id):
    try:
        conn = conectar_banco()
        if not conn:
            return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, link, numero_nota, data_compra, valor_total, data_criacao
            FROM notas_fiscais 
            WHERE usuario_id = %s 
            ORDER BY data_criacao DESC
        """, (user_id,))
        
        notas = cursor.fetchall()
        
        notas_formatadas = []
        for nota in notas:
            notas_formatadas.append({
                "id": nota[0],
                "link": nota[1],
                "numero_nota": nota[2],
                "data_compra": nota[3].strftime('%Y-%m-%d') if nota[3] else None,
                "valor_total": float(nota[4]) if nota[4] else None,
                "data_criacao": nota[5].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            "notas": notas_formatadas,
            "total": len(notas_formatadas)
        }), 200
        
    except Error as e:
        return jsonify({"erro": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# 🥚 EASTER EGG: Rota secreta para desenvolvedores
@app.route('/dev_secret', methods=['GET'])
def dev_secret():
    return jsonify({
        "🎉": "EASTER EGG ENCONTRADO!",
        "mensagem": "Parabéns, dev! Você encontrou a rota secreta!",
        "equipe": ["Desenvolvedor 1", "Desenvolvedor 2", "Desenvolvedor 3"],
        "dica": "Há mais Easter Eggs escondidos no código... 🔍",
        "ascii_art": """
        ╔══════════════════════════════════════╗
        ║           ECONOMIZA 2.0              ║
        ║      Sistema de Economia Inteligente ║
        ║                                      ║
        ║    Desenvolvido com 💚 pela equipe   ║
        ║           mais incrível!             ║
        ╚══════════════════════════════════════╝
        """
    })

# Handler de erro personalizado
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "erro": "Endpoint não encontrado",
        "dica": "Verifique a documentação da API",
        "easter_egg": "Tente acessar /dev_secret 😉"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "erro": "Erro interno do servidor",
        "mensagem": "Entre em contato com a equipe de desenvolvimento"
    }), 500

# Inicializar aplicação
if __name__ == '__main__':
    print("🚀 Iniciando o Economiza Backend...")
    criar_tabelas()
    print("🎯 Sistema pronto para uso!")
    app.run(debug=True, host='0.0.0.0', port=5000)
