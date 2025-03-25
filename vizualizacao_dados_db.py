import sqlite3

conn = sqlite3.connect("dados_nfce.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM produtos")
dados = cursor.fetchall()

for linha in dados:
    print(linha)

conn.close()
