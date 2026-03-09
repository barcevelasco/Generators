import requests

url = "https://openknowledge.worldbank.org/server/api/discover/search/objects?sort=dc.date.issued,DESC"

r = requests.get(url)

data = r.json()

objects = data["_embedded"]["searchResult"]["_embedded"]["objects"]

for obj in objects:

    item = obj["_embedded"]["indexableObject"]

    titulo = item["name"]
    handle = item["handle"]

    metadata = item["metadata"]

    fecha = metadata["dc.date.issued"][0]["value"]

    if fecha.startswith("2026-01"):

        link = f"https://openknowledge.worldbank.org/handle/{handle}"
        print(fecha)
        print(titulo)
        print(link)
        print()