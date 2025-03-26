numero_nota = input("Digite o número da nota para ver os produtos: ")

conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM produtos WHERE numero_nota = ?", (numero_nota,))
resultados = cursor.fetchall()

for produto in resultados:
    print(produto)

conn.close()
