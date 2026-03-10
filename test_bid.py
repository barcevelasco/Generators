from app import load_investigacion_bid
import datetime

print("="*50)
print("PRUEBA BID WORKING PAPERS")
print("="*50)

df = load_investigacion_bid("01.01.2025", "31.12.2026")
print(f"\n📊 RESULTADO: {len(df)} documentos")