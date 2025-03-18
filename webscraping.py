from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configurando o WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa sem abrir o navegador

# Iniciando o driver do Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Abrindo a página da NFC-e
url = "https://portalsped.fazenda.mg.gov.br/portalnfce/sistema/qrcode.xhtml?p=31250103083231004434651080000099511264815312%7C2%7C1%7C1%7C56F331339A3E57FEC3DDFC331E9BDFC9557CFD91"
driver.get(url)

# Pegando a lista de produtos e preços
try:
    linhas = driver.find_elements(By.XPATH, "//table[@class='table table-striped']/tbody/tr")
    
    for linha in linhas:
        try:
            produto = linha.find_element(By.TAG_NAME, "h7").text
            preco = linha.find_elements(By.TAG_NAME, "td")[-1].text  # Última célula da linha
            print(f"Produto: {produto} - Preço: {preco}")
        except Exception as e:
            continue  # Pula se não encontrar os elementos

except Exception as e:
    print("Erro ao encontrar os elementos:", e)

# Fechando o navegador
driver.quit()
