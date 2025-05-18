import cloudscraper
from bs4 import BeautifulSoup
import requests
import re
import time
import csv
import json
import os
from datetime import datetime

BASE_URL = "https://habana.porlalivre.com"
LIST_PATH = "/viviendas/"
MAX_PAGE = 20
print(f"Procesaremos las primeras {MAX_PAGE} páginas de Porlalivre.")

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
output_raw_dir = os.path.join(project_dir, "data", "raw")
os.makedirs(output_raw_dir, exist_ok=True)

csv_filepath = os.path.join(output_raw_dir, "porlalivre.csv")
processed_ids_filepath = os.path.join(output_raw_dir, "porlalivre_raw_ids.json")

print(f"CSV de salida: {csv_filepath}")
print(f"JSON de IDs procesados: {processed_ids_filepath}")

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/100.0.4896.127 Safari/537.36"
    )
})
scraper = cloudscraper.create_scraper(sess=session, browser="chrome", delay=5)

if os.path.exists(processed_ids_filepath):
    try:
        with open(processed_ids_filepath, "r", encoding="utf-8") as f:
            processed_ad_ids = set(json.load(f))
        print(f"Cargados {len(processed_ad_ids)} IDs ya procesados.")
    except json.JSONDecodeError:
        processed_ad_ids = set()
        print("JSON corrupto: iniciando lista vacía.")
else:
    processed_ad_ids = set()
    with open(processed_ids_filepath, "w", encoding="utf-8") as f:
        json.dump([], f)
    print("No existía JSON de IDs: creado vacío.")

headers = [
    "ID",
    "Titulo",
    "Precio",
    "Ubicacion",
    "Descripcion",
    "Nombre",
    "Contactos",
    "Fecha",
    "URL",
]

def sanitize_text(text):
    """Reemplaza comas por espacios y recorta."""
    return re.sub(r",", " ", str(text)).strip()

def parse_ad_page(html, url, ad_id):
    """Extrae datos de la página de detalle de un anuncio."""
    soup = BeautifulSoup(html, "html.parser")
    data = dict.fromkeys(headers, "N/A")
    data.update({"URL": url, "ID": ad_id})

    header = soup.find("div", id="classified-header")
    if header:
        h1 = header.find("h1")
        if h1:
            raw_title = h1.get_text(strip=True).split("|")[0]
            data["Titulo"] = sanitize_text(raw_title)
        price_tag = header.find("span", class_="text-primary")
        if price_tag:
            raw_price = price_tag.get_text(strip=True).lstrip("$")
            data["Precio"] = sanitize_text(raw_price)
        lis = header.find_all("li")
        if len(lis) >= 3:
            data["Ubicacion"] = sanitize_text(lis[2].get_text(strip=True))

    desc = soup.select_one(".panel-body.classified-description")
    if desc:
        data["Descripcion"] = sanitize_text(desc.get_text(strip=True))

    contactos = []
    contact = soup.select_one("div.contact-info ul")
    if contact:
        user_li = contact.find("i", class_="fa-user")
        if user_li and user_li.parent:
            data["Nombre"] = sanitize_text(user_li.parent.get_text(strip=True))
        phone_li = contact.find("i", class_="fa-phone")
        if phone_li and phone_li.parent:
            tel = re.sub(r"[^\d+]", "", phone_li.parent.get_text())
            contactos.append(tel)
        email_a = contact.select_one("i.fa-envelope + a")
        if email_a and email_a.get("href", "").startswith("mailto:"):
            mail = email_a["href"].split(":", 1)[1]
            contactos.append(mail)
    data["Contactos"] = "; ".join(contactos) if contactos else "N/A"

    return data

with open(csv_filepath, "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=headers,
        quoting=csv.QUOTE_ALL  
    )
    if os.stat(csv_filepath).st_size == 0:
        writer.writeheader()

    total_new = 0
    for page in range(1, MAX_PAGE + 1):
        print(f"\n[Página {page}] obteniendo listados…")
        try:
            resp = scraper.get(
                BASE_URL + LIST_PATH,
                params={"sort": "price.ASC", "sort": "updated_on", "page": page},
            )
            resp.raise_for_status()
            time.sleep(1.0)
        except Exception as e:
            print(f"  ERROR al cargar página {page}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        wrappers = soup.find_all("div", class_="classified-wrapper")
        print(f"  → {len(wrappers)} anuncios encontrados.")

        for w in wrappers:
            link = w.find("a", class_="classified-link")
            if not link or not link.get("href"):
                continue

            relative = link["href"]
            ad_url = BASE_URL + relative
            ad_id = relative.strip("/").split("-")[-1]

            date_li = w.find("li", class_="hidden-xs")
            raw_date = date_li.get_text(strip=True) if date_li else "N/A"
            formatted_date = "N/A"
            if raw_date != "N/A":
                try:
                    parts = [p.strip(".,") for p in raw_date.split()]
                    date_str = f"{parts[0].capitalize()} {parts[1]} {parts[2]}"
                    date_obj = datetime.strptime(date_str, "%b %d %Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                except:
                    formatted_date = sanitize_text(raw_date)

            if ad_id in processed_ad_ids:
                print(f"    {ad_id} ya procesado, omitiendo.")
                continue

            try:
                print(f"    Procesando {ad_id}... ", end="")
                r2 = scraper.get(ad_url)
                r2.raise_for_status()
                time.sleep(0.5)

                ad_data = parse_ad_page(r2.text, ad_url, ad_id)
                ad_data["Fecha"] = formatted_date

                writer.writerow(ad_data)
                processed_ad_ids.add(ad_id)
                with open(processed_ids_filepath, "w", encoding="utf-8") as f_ids:
                    json.dump(list(processed_ad_ids), f_ids, ensure_ascii=False, indent=2)

                total_new += 1
                print("OK")
            except Exception as e2:
                print(f"ERROR detalle: {e2}")

    print(f"\nTotal de anuncios NUEVOS procesados: {total_new}")

print("¡Scraping completado!")
