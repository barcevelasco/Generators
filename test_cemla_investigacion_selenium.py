# test_cemla_investigacion_selenium.py
"""
Script con navegador visible para evitar detección
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def test_cemla_investigacion_selenium():
    url = "https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press"
    
    print("=" * 70)
    print("🔬 TEST DE INVESTIGACIÓN - CEMLA (CON NAVEGADOR VISIBLE)")
    print("=" * 70)
    
    # Configurar Selenium - SIN headless
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # <-- COMENTADO
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Opciones adicionales para parecer más humano
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = None
    try:
        print("🚀 Iniciando Selenium (se abrirá una ventana del navegador)...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Ejecutar script para ocultar que es automatizado
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"📡 Accediendo a {url}...")
        driver.get(url)
        
        # Esperar MUCHO tiempo para que cargue y puedas ver si hay CAPTCHA
        print("⏳ Esperando 30 segundos para carga manual...")
        print("⚠️  Si aparece un CAPTCHA, resuélvelo manualmente en el navegador")
        time.sleep(30)
        
        # Ahora obtener el HTML
        html = driver.page_source
        
        # Guardar HTML
        with open("cemla_exitosa.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML guardado en 'cemla_exitosa.html'")
        
        # Analizar
        soup = BeautifulSoup(html, 'html.parser')
        articulos = soup.find_all('li', class_='js-article-list-item')
        print(f"📚 Artículos encontrados: {len(articulos)}")
        
        if articulos:
            print("\n📄 PRIMER ARTÍCULO:")
            titulo = articulos[0].find('a', class_='article-content-title')
            fecha = articulos[0].find('span', class_='js-article-item-aip-date')
            if titulo and fecha:
                print(f"  Título: {titulo.get_text(strip=True)}")
                print(f"  Fecha: {fecha.get_text(strip=True)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            input("\n⏸️  Presiona ENTER para cerrar el navegador...")
            driver.quit()

if __name__ == "__main__":
    test_cemla_investigacion_selenium()