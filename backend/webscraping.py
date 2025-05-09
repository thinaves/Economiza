import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuração do Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa sem abrir o navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# URL da nota fiscal (insira automaticamente no código)
url = "https://portalsped.fazenda.mg.gov.br/portalnfce/sistema/qrcode.xhtml?p=31250103083231004434651080000099511264815312%7C2%7C1%7C1%7C56F331339A3E57FEC3DDFC331E9BDFC9557CFD91"
driver.get(url)

# Conectar ao banco de dados SQLite
conn = sqlite3.connect("produtos.db")
cursor = conn.cursor()

# Criar a tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    preco TEXT,
    data_da_compra TEXT,
    numero_nota TEXT,
    url_nota TEXT
)
""")

# Pegando a data da compra e número da nota
try:
    data_elemento = driver.find_element(By.XPATH, "//*[@id=\"collapse4\"]/table[3]/tbody/tr/td[4]")  # Ajuste o XPATH correto
    numero_nota_elemento = driver.find_element(By.XPATH, "//*[@id="collapse4"]/table[3]/tbody/tr/td[3]")  # Ajuste o XPATH correto

    data_da_compra = data_elemento.text.strip()
    numero_nota = numero_nota_elemento.text.strip()
except:
    data_da_compra = datetime.today().strftime('%Y-%m-%d')  # Usa a data atual se não encontrar
    numero_nota = "Desconhecido"

# Pegando a lista de produtos e preços
try:
    linhas = driver.find_elements(By.XPATH, "//table[@class='table table-striped']/tbody/tr")
    
    for linha in linhas:
        try:
            produto = linha.find_element(By.TAG_NAME, "h7").text
            preco = linha.find_elements(By.TAG_NAME, "td")[-1].text  # Última célula da linha
            
            # Inserir no banco de dados
            cursor.execute("INSERT INTO produtos (nome, preco, data_da_compra, numero_nota, url_nota) VALUES (?, ?, ?, ?, ?)",
                           (produto, preco, data_da_compra, numero_nota, url))
            
        except Exception as e:
            continue  # Pula se não encontrar os elementos

    conn.commit()  # Salva os dados no banco

except Exception as e:
    print("Erro ao encontrar os elementos:", e)

# Fechar conexões
driver.quit()
conn.close()

print("Dados armazenados com sucesso!")
