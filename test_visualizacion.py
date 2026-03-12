# test_visualizacion.py
from app import load_investigacion_bid
import pandas as pd
import streamlit as st

# Obtener datos
df = load_investigacion_bid("01.01.2025", "31.12.2026")

print("\n" + "="*50)
print("PRUEBA DE VISUALIZACIÓN")
print("="*50)

# Simular lo que pasa en la app
f_df = df.copy()
f_df['Categoría'] = "Investigación"
f_df = f_df[['Categoría', 'Organismo', 'Title', 'Link']]
f_df = f_df.rename(columns={"Categoría": "Tipo de Documento", "Title": "Nombre de Documento"})

print("\n🔍 DataFrame después de renombrar:")
print(f_df.head())
print("\n🔍 Columnas:", f_df.columns.tolist())
print("\n🔍 Tipos de datos:", f_df.dtypes)

print("\n🔍 TÍTULOS REALES:")
print(f_df['Nombre de Documento'].head(5).tolist())

# Probar la lambda
print("\n🔍 Probando lambda en títulos reales:")
for titulo in f_df['Nombre de Documento'].head(3):
    print(f"  Original: '{titulo}'")
    print(f"  Con lambda: '[{titulo}](enlace)'")