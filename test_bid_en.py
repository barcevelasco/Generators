# test_bid_en.py
from app import load_investigacion_bid_en
import datetime

print("="*50)
print("PRUEBA BID WORKING PAPERS (INGLÉS)")
print("="*50)

df = load_investigacion_bid_en("01.01.2025", "31.12.2026")
print(f"\n📊 RESULTADO: {len(df)} documentos")

if not df.empty:
    print("\n📋 PRIMEROS 5 DOCUMENTOS:")
    for i, row in df.head().iterrows():
        print(f"{i+1}. {row['Date'].strftime('%Y')}: {row['Title'][:100]}...")
        print(f"   Link: {row['Link']}")
        print()