# test_cemla_debug.py
"""
Script de depuración para ver qué HTML está recibiendo Selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import os

def debug_cemla():
    url = "https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press"
    
    print("=" * 70)
    print("🔍 DEBUG CEMLA - ANÁLISIS DE HTML")
    print("=" * 70)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    chromedriver_path = "/usr/local/bin/chromedriver"
    
    try:
        print("🚀 Iniciando Chrome...")
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"📡 Accediendo a {url}...")
        driver.get(url)
        
        # Esperar más tiempo
        print("⏳ Esperando 15 segundos...")
        time.sleep(15)
        
        # Obtener HTML y URL actual
        current_url = driver.current_url
        html = driver.page_source
        driver.quit()
        
        print(f"📍 URL actual después de carga: {current_url}")
        
        # Guardar HTML
        with open("cemla_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML guardado en 'cemla_debug.html'")
        
        # Analizar rápidamente
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar pistas en el HTML
        print("\n🔎 BUSCANDO PISTAS EN EL HTML:")
        print("-" * 70)
        
        # 1. Buscar título de la página
        title = soup.find('title')
        if title:
            print(f"📌 Título de la página: {title.get_text()}")
        
        # 2. Buscar elementos comunes de cookie consent
        cookie_texts = soup.find_all(text=lambda t: t and ('cookie' in t.lower() or 'consent' in t.lower()))
        if cookie_texts:
            print(f"🍪 Se encontraron {len(cookie_texts)} menciones de cookies")
            print(f"   Ejemplo: {cookie_texts[0][:200]}...")
        
        # 3. Buscar cualquier cosa que parezca un artículo
        posibles_articulos = soup.find_all(['div', 'li', 'article'], 
                                          class_=lambda c: c and any(x in str(c).lower() for x in ['article', 'result', 'item']))
        print(f"📚 Posibles contenedores de artículos: {len(posibles_articulos)}")
        
        # 4. Buscar texto "Available online"
        fechas = soup.find_all(text=re.compile(r'Available online'))
        print(f"📅 Menciones de 'Available online': {len(fechas)}")
        
        if fechas:
            print("\n📅 PRIMERAS FECHAS ENCONTRADAS:")
            for f in fechas[:3]:
                print(f"  • {f}")
        
        print("\n" + "=" * 70)
        print("📌 SIGUIENTE PASO:")
        print("1. Revisa el archivo 'cemla_debug.html' en el explorador de archivos")
        print("2. Busca manualmente 'Available online' en ese archivo")
        print("3. Comparte lo que encuentres para ajustar los selectores")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import re
    debug_cemla()
