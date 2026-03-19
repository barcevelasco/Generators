# test_bid_annual.py
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.getcwd())

try:
    from app import load_reportes_bid_en
    print("✅ Función importada correctamente")
except Exception as e:
    print(f"❌ Error al importar: {e}")
    sys.exit(1)

import datetime

print("="*60)
print("🔍 PRUEBA: BID ANNUAL REPORTS")
print("="*60)

# Probar con marzo 2026
df = load_reportes_bid_en("01.03.2026", "31.03.2026")

print(f"\n📊 RESULTADO: {len(df)} documentos encontrados")

if not df.empty:
    print("\n📋 DOCUMENTOS:")
    for i, row in df.iterrows():
        print(f"{i+1}. {row['Date'].strftime('%Y-%m')}: {row['Title'][:80]}...")
        print(f"   Link: {row['Link']}")
        print()
else:
    print("❌ No se encontraron documentos")

print("="*60)
