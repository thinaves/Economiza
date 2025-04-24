import sqlite3

# Conecta ao banco de dados
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Dados do novo usuário
novo_usuario = ("novousuario@exemplo.com", "senha123")

# Inserindo no banco
cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", novo_usuario)
conn.commit()

print("Usuário adicionado com sucesso!")

# Fecha a conexão
conn.close()
