import requests
import json

url = "https://www.imf.org/_next/data/OPXKbpp2La91iW-gTVkBX/en/publications.json"

r = requests.get(url)
data = r.json()

texto = json.dumps(data)

partes = texto.split("finance and development")

print("Coincidencias encontradas:", len(partes)-1)
print()

for p in partes[1:6]:
    print(p[:300])
    print("\n---\n")