import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()

# Pedir o número da nota fiscal
numero_nota = input("Digite o número da nota para ver os produtos: ")

# Buscar produtos no banco de dados
cursor.execute("SELECT * FROM produtos WHERE numero_nota = ?", (numero_nota,))
resultados = cursor.fetchall()

# Exibir os produtos encontrados
if resultados:
    print("\nProdutos encontrados:")
    for produto in resultados:
        print(f"ID: {produto[0]}, Nome: {produto[1]}, Preço: {produto[2]}, Data: {produto[3]}, Nota: {produto[4]}")
else:
    print("Nenhum produto encontrado para essa nota fiscal.")

# Fechar a conexão
conn.close()