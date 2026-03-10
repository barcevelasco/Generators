from app import load_pub_inst_cemla
import datetime

print("="*50)
print("PRUEBA DE FUNCIÓN CEMLA")
print("="*50)

# Probar con un rango amplio (2023-2026)
df = load_pub_inst_cemla("01.01.2023", "31.12.2026")

print(f"\n📊 RESULTADO: {len(df)} artículos encontrados")

if not df.empty:
    print("\n📋 LISTA DE BOLETINES:")
    for i, row in df.iterrows():
        print(f"{i+1}. {row['Date'].strftime('%B %Y')}: {row['Title'][:100]}...")
        print(f"   Link: {row['Link']}")
        print()
else:
    print("❌ No se encontraron artículos")