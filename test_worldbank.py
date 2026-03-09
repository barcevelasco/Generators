import requests
from datetime import datetime
import csv

MES = datetime.now().strftime("%Y-%m")

url = "https://openknowledge.worldbank.org/server/api/discover/search/objects?sort=dc.date.issued,DESC"

r = requests.get(url)
data = r.json()

objects = data["_embedded"]["searchResult"]["_embedded"]["objects"]

with open("data_worldbank.csv", "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow(["tipo", "organismo", "fecha", "titulo", "link"])

    encontrado = False

    for obj in objects:

        indexable = obj["_embedded"]["indexableObject"]

        if "dc.date.issued" not in indexable:
            continue

        fecha = indexable["dc.date.issued"][0]["value"]

        if MES in fecha:

            titulo = indexable["dc.title"][0]["value"]

            link = "https://openknowledge.worldbank.org" + obj["_embedded"]["indexableObject"]["handle"]

            writer.writerow([
                "Publicaciones Institucionales",
                "World Bank",
                fecha,
                titulo,
                link
            ])

            print("World Bank")
            print(fecha)
            print(titulo)
            print(link)
            print()

            encontrado = True

if not encontrado:
    print("No se encontraron documentos para el mes:", MES)