# test_cemla_investigacion.py
"""
Script de prueba para extraer artículos de investigación del 
Latin American Journal of Central Banking (CEMLA) desde ScienceDirect
"""

import requests
from bs4 import BeautifulSoup
import datetime
import re
import time

def test_cemla_investigacion():
    """
    Prueba específica para la sección de investigación de CEMLA
    (Latin American Journal of Central Banking)
    """
    
    url = "https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("=" * 70)
    print("🔬 TEST DE INVESTIGACIÓN - CEMLA (Latin American Journal)")
    print("=" * 70)
    print(f"📌 Tipo: Artículos de investigación / working papers")
    print(f"🌐 URL: {url}")
    print("-" * 70)
    
    try:
        # 1. HACER PETICIÓN
        print("📡 Paso 1: Solicitando página...")
        res = requests.get(url, headers=headers, timeout=20)
        print(f"   → Status code: {res.status_code}")
        
        if res.status_code != 200:
            print(f"❌ Error: No se pudo acceder a la página")
            return
        
        # 2. GUARDAR HTML
        filename = "cemla_investigacion_debug.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(res.text)
        print(f"💾 Paso 2: HTML guardado en '{filename}'")
        
        # 3. ANALIZAR CON BEAUTIFUL SOUP
        print("🔧 Paso 3: Analizando estructura HTML...")
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 4. BUSCAR ARTÍCULOS
        print("\n🔍 Paso 4: Buscando artículos...")
        print("-" * 70)
        
        # Estrategias de búsqueda
        articulos = soup.find_all('li', class_='js-article-list-item')
        print(f"📊 Estrategia 1 (clase específica): {len(articulos)} artículos")
        
        if not articulos:
            articulos = soup.find_all('li', class_=lambda c: c and 'article' in c)
            print(f"📊 Estrategia 2 (li con 'article'): {len(articulos)} artículos")
        
        if not articulos:
            articulos = soup.find_all('div', class_=lambda c: c and 'article' in c)
            print(f"📊 Estrategia 3 (div con 'article'): {len(articulos)} artículos")
        
        if not articulos:
            print("❌ No se encontraron artículos con ninguna estrategia")
            return
        
        # 5. PROCESAR ARTÍCULOS ENCONTRADOS
        print(f"\n📄 Paso 5: Procesando {len(articulos)} artículos encontrados")
        print("-" * 70)
        
        # Diccionario de meses
        meses = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        # Contadores
        total_articulos = 0
        articulos_marzo = 0
        articulos_filtrados = []
        
        for i, articulo in enumerate(articulos[:10]):  # Primeros 10 para prueba
            print(f"\n--- ARTÍCULO {i+1} ---")
            
            # TÍTULO
            title_elem = (articulo.find('a', class_='article-content-title') or 
                         articulo.find('a', class_='anchor article-content-title') or
                         articulo.find('a', href=True))
            
            if not title_elem:
                print("  ⚠️ No se encontró título")
                continue
            
            titulo = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if not link.startswith('http'):
                link = f"https://www.sciencedirect.com{link}"
            
            print(f"  📌 Título: {titulo[:80]}...")
            print(f"  🔗 Link: {link[:60]}...")
            
            # FECHA
            fecha_elem = (articulo.find('span', class_='js-article-item-aip-date') or
                         articulo.find('span', string=re.compile(r'Available online')))
            
            if not fecha_elem:
                # Buscar en cualquier elemento
                for elem in articulo.find_all(['span', 'div', 'p']):
                    if 'Available online' in elem.get_text():
                        fecha_elem = elem
                        break
            
            if not fecha_elem:
                print("  ⚠️ No se encontró fecha")
                continue
            
            fecha_texto = fecha_elem.get_text(strip=True)
            print(f"  📅 Fecha raw: '{fecha_texto}'")
            
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
                    
                    # Verificar si es marzo 2026
                    if año == 2026 and mes_num == 3:
                        articulos_marzo += 1
                        print(f"  🎯 ¡ES DE MARZO 2026!")
                        
                        # AUTORES
                        autor_elem = articulo.find('div', class_='js-article-author-list')
                        autores = autor_elem.get_text(strip=True) if autor_elem else "No disponible"
                        print(f"  👥 Autores: {autores[:80]}...")
                        
                        # TIPO
                        tipo_elem = articulo.find('span', class_='js-article-subtype')
                        tipo = tipo_elem.get_text(strip=True) if tipo_elem else "No especificado"
                        print(f"  📋 Tipo: {tipo}")
                        
                        articulos_filtrados.append({
                            'titulo': titulo,
                            'fecha': fecha,
                            'link': link,
                            'autores': autores,
                            'tipo': tipo
                        })
                else:
                    print(f"  ⚠️ Mes no reconocido: '{mes_str}'")
            else:
                print("  ⚠️ No se pudo extraer fecha con regex")
            
            total_articulos += 1
        
        # 6. RESUMEN FINAL
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE EXTRACCIÓN")
        print("=" * 70)
        print(f"📊 Total artículos procesados: {total_articulos}")
        print(f"📅 Artículos de MARZO 2026: {articulos_marzo}")
        
        if articulos_filtrados:
            print("\n✅ ARTÍCULOS DE MARZO 2026 ENCONTRADOS:")
            print("-" * 70)
            for i, art in enumerate(articulos_filtrados, 1):
                print(f"\n{i}. {art['titulo']}")
                print(f"   📅 Fecha: {art['fecha'].strftime('%d/%m/%Y')}")
                print(f"   📋 Tipo: {art['tipo']}")
                print(f"   👥 {art['autores']}")
                print(f"   🔗 {art['link']}")
        else:
            print("\n❌ NO se encontraron artículos de marzo 2026")
            print("\nPosibles causas:")
            print("1. La página no tiene artículos de marzo todavía")
            print("   → Verifica manualmente: https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press")
            print("2. El selector CSS no está funcionando correctamente")
            print("3. Los artículos están en otra sección (ej. 'Latest articles' no 'Articles in Press')")
            
            # Mostrar primeras fechas encontradas
            print("\n📅 Fechas encontradas en la página (primeras 5):")
            fechas_encontradas = set()
            for articulo in articulos[:10]:
                fecha_elem = articulo.find('span', class_='js-article-item-aip-date')
                if fecha_elem:
                    fecha_texto = fecha_elem.get_text(strip=True)
                    match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', fecha_texto)
                    if match:
                        fechas_encontradas.add(f"{match.group(2)} {match.group(3)}")
            
            for fecha in list(fechas_encontradas)[:5]:
                print(f"   • {fecha}")
        
        print("\n" + "=" * 70)
        print(f"💡 Para más detalles, abre '{filename}' en tu navegador")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()

def verificar_url_manual():
    """Función auxiliar para verificar si la URL es accesible"""
    import webbrowser
    url = "https://www.sciencedirect.com/journal/latin-american-journal-of-central-banking/articles-in-press"
    print(f"\n🌐 Abriendo URL en navegador para verificación manual...")
    print(f"   {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    test_cemla_investigacion()
    
    print("\n" + "=" * 70)
    respuesta = input("¿Quieres abrir la URL en el navegador? (s/n): ")
    if respuesta.lower() == 's':
        verificar_url_manual()