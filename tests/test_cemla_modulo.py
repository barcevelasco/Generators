# tests/test_cemla_modulo.py
"""
Test para probar el módulo extractor de CEMLA
"""

import sys
import os

# Añadir el directorio padre al path para poder importar el módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ahora podemos importar nuestro módulo
from extractores.cemla_extractor import extraer_articulos_cemla

def test_extraccion_cemla():
    """Prueba la extracción de artículos de CEMLA"""
    
    print("=" * 70)
    print("🔬 TEST DEL MÓDULO CEMLA EXTRACTOR")
    print("=" * 70)
    
    # Probar diferentes rangos de fecha
    casos_prueba = [
        ("01.03.2026", "31.03.2026", "Marzo 2026"),
        ("01.01.2026", "31.12.2026", "Todo 2026"),
        (None, None, "Sin filtro de fecha")
    ]
    
    for start, end, desc in casos_prueba:
        print(f"\n📅 Caso: {desc}")
        print("-" * 50)
        
        df = extraer_articulos_cemla(
            start_date_str=start, 
            end_date_str=end,
            max_paginas=2  # Limitamos a 2 páginas para la prueba
        )
        
        if not df.empty:
            print(f"\n✅ Se encontraron {len(df)} artículos")
            print("\n📋 PRIMEROS 3 ARTÍCULOS:")
            for i, row in df.head(3).iterrows():
                print(f"\n  {i+1}. {row['Title'][:100]}...")
                print(f"     📅 {row['Date'].strftime('%d/%m/%Y')}")
                print(f"     🔗 {row['Link']}")
        else:
            print("❌ No se encontraron artículos")
        
        print("\n" + "=" * 50)

def test_integracion_simple():
    """Prueba simple para verificar que el módulo funciona"""
    
    print("\n" + "=" * 70)
    print("🔬 TEST DE INTEGRACIÓN SIMPLE")
    print("=" * 70)
    
    # Extraer artículos de marzo 2026
    df = extraer_articulos_cemla("01.03.2026", "31.03.2026")
    
    if not df.empty:
        print(f"\n✅ Módulo funciona correctamente")
        print(f"📊 Artículos de marzo 2026: {len(df)}")
        
        # Verificar que tenemos los artículos esperados
        fechas_esperadas = ['14/03/2026', '12/03/2026', '09/03/2026']
        fechas_encontradas = df['Date'].dt.strftime('%d/%m/%Y').tolist()
        
        print("\n🔍 Verificando fechas de marzo:")
        for fecha in fechas_esperadas:
            if fecha in fechas_encontradas:
                print(f"  ✅ {fecha} - Encontrado")
            else:
                print(f"  ❌ {fecha} - No encontrado")
    else:
        print("❌ El módulo no devolvió resultados")

if __name__ == "__main__":
    test_extraccion_cemla()
    test_integracion_simple()
    