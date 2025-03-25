import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configurando o WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa sem abrir o navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Abrindo a página da NFC-e
url = "https://portalsped.fazenda.mg.gov.br/portalnfce/sistema/qrcode.xhtml?p=31250103083231004434651080000099511264815312%7C2%7C1%7C1%7C56F331339A3E57FEC3DDFC331E9BDFC9557CFD91"
driver.get(url)

# Conectar ao banco de dados SQLite
conn = sqlite3.connect("dados_nfce.db")
cursor = conn.cursor()

# Criar a tabela (se não existir)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco TEXT NOT NULL
    )
''')

# Pegando a lista de produtos e preços
try:
    linhas = driver.find_elements(By.XPATH, "//table[@class='table table-striped']/tbody/tr")
    
    for linha in linhas:
        try:
            produto = linha.find_element(By.TAG_NAME, "h7").text
            preco = linha.find_elements(By.TAG_NAME, "td")[-1].text  # Última célula da linha
            
            # Inserindo no banco de dados
            cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (produto, preco))
            conn.commit()
            print(f"Salvo no banco: {produto} - {preco}")
        
        except Exception as e:
            continue  # Pula se não encontrar os elementos

except Exception as e:
    print("Erro ao encontrar os elementos:", e)

# Fechar conexões
conn.close()
driver.quit()
