from app import load_pub_inst_imf
import datetime

print("="*50)
print("PRUEBA DE FUNCIÓN FMI CON SELENIUM (DESDE APP.PY)")
print("="*50)

# Probar marzo 2026
df = load_pub_inst_imf("01.03.2026", "31.03.2026")

print(f"\n📊 RESULTADO: {len(df)} artículos encontrados")

if not df.empty:
    print("\n📋 PRIMEROS ARTÍCULOS:")
    for i, row in df.head().iterrows():
        print(f"{i+1}. {row['Title']}")
        print(f"   Fecha: {row['Date'].strftime('%B %Y')}")
        print(f"   Link: {row['Link']}")
        print()
else:
    print("❌ No se encontraron artículos")