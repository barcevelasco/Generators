# test_cemla_codespaces.py
"""
Script para extraer artículos del Latin American Journal of Central Banking
Funciona en Codespaces con ChromeDriver 146+
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import os
import datetime
import re

def test_cemla_codespaces():
    url = "https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press"
    
    print("=" * 70)
    print("🔬 TEST CEMLA - CODESPACES")
    print("=" * 70)
    print(f"🌐 URL: {url}")
    print("-" * 70)
    
    # Configurar Chrome para Codespaces
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Modo sin cabeza
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Ruta de ChromeDriver (ya verificada)
    chromedriver_path = "/usr/local/bin/chromedriver"
    
    if not os.path.exists(chromedriver_path):
        print(f"❌ No se encontró ChromeDriver en {chromedriver_path}")
        return
    
    print(f"✅ ChromeDriver encontrado: {chromedriver_path}")
    
    driver = None
    try:
        print("🚀 Iniciando Chrome...")
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"📡 Accediendo a {url}...")
        driver.get(url)
        
        # Esperar carga
        print("⏳ Esperando 10 segundos para carga completa...")
        time.sleep(10)
        
        # Obtener HTML
        html = driver.page_source
        driver.quit()
        
        # Guardar HTML para depuración
        with open("cemla_codespaces.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ HTML guardado en 'cemla_codespaces.html'")
        
        # Analizar con BeautifulSoup
        print("\n🔍 Analizando HTML...")
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar artículos
        articulos = soup.find_all('li', class_='js-article-list-item')
        print(f"📚 Artículos encontrados: {len(articulos)}")
        
        if not articulos:
            print("❌ No se encontraron artículos")
            return
        
        # Procesar artículos
        print("\n📄 ARTÍCULOS ENCONTRADOS:")
        print("-" * 70)
        
        meses = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        articulos_marzo = []
        
        for i, articulo in enumerate(articulos[:10], 1):
            print(f"\n--- ARTÍCULO {i} ---")
            
            # Título
            title_elem = articulo.find('a', class_='article-content-title')
            if title_elem:
                titulo = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                if not link.startswith('http'):
                    link = f"https://www.sciencedirect.com{link}"
                print(f"  📌 Título: {titulo[:100]}...")
                print(f"  🔗 Link: {link}")
            else:
                print("  ⚠️ No título")
                continue
            
            # Fecha
            fecha_span = articulo.find('span', class_='js-article-item-aip-date')
            if fecha_span:
                fecha_texto = fecha_span.get_text(strip=True)
                print(f"  📅 Fecha: {fecha_texto}")
                
                # Extraer fecha
                match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', fecha_texto)
                if match:
                    dia = int(match.group(1))
                    mes_str = match.group(2).lower()
                    año = int(match.group(3))
                    
                    mes_num = meses.get(mes_str) or meses.get(mes_str[:3])
                    
                    if mes_num:
                        fecha = datetime.datetime(año, mes_num, dia)
                        print(f"  ✅ Fecha parseada: {fecha.strftime('%d/%m/%Y')}")
                        
                        if año == 2026 and mes_num == 3:
                            print(f"  🎯 ¡ES DE MARZO 2026!")
                            articulos_marzo.append({
                                'titulo': titulo,
                                'fecha': fecha,
                                'link': link,
                                'fecha_texto': fecha_texto
                            })
            
            # Autores
            autor_elem = articulo.find('div', class_='js-article-author-list')
            if autor_elem:
                print(f"  👥 Autores: {autor_elem.get_text(strip=True)[:100]}")
            
            # Tipo
            tipo_elem = articulo.find('span', class_='js-article-subtype')
            if tipo_elem:
                print(f"  📋 Tipo: {tipo_elem.get_text(strip=True)}")
        
        # Resumen
        print("\n" + "=" * 70)
        print("📊 RESUMEN FINAL")
        print("=" * 70)
        print(f"📚 Total artículos procesados: {min(len(articulos), 10)}")
        print(f"📅 Artículos de MARZO 2026: {len(articulos_marzo)}")
        
        if articulos_marzo:
            print("\n✅ ARTÍCULOS DE MARZO 2026 ENCONTRADOS:")
            for art in articulos_marzo:
                print(f"  • {art['fecha'].strftime('%d/%m/%Y')}: {art['titulo'][:80]}...")
                print(f"    🔗 {art['link']}")
        else:
            print("\n❌ No se encontraron artículos de marzo 2026")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n🛑 Navegador cerrado.")

if __name__ == "__main__":
    test_cemla_codespaces()