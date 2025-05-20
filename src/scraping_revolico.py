import cloudscraper 
from bs4 import BeautifulSoup
import requests
import re
import time
import csv
import json
import os

URL = "https://www.revolico.com/"
MAX_PAGE = 15
print(f"Se procesarán las primeras {MAX_PAGE} páginas.")

script_dir = os.path.dirname(os.path.abspath(__file__))
gao_dir = os.path.dirname(script_dir)
output_raw_dir = os.path.join(gao_dir, 'data', 'raw')
csv_filename = 'revolico.csv'
csv_filepath = os.path.join(output_raw_dir, csv_filename)
processed_ids_filename = 'revolico_raw_ids.json'
processed_ids_filepath = os.path.join(output_raw_dir, processed_ids_filename)

os.makedirs(output_raw_dir, exist_ok=True)
print(f"Ruta de salida configurada en: {output_raw_dir}")
print(f"Archivo CSV de salida será: {csv_filepath}")
print(f"Archivo de IDs procesados será: {processed_ids_filepath}")

scraper_options = {
    'browser': 'chrome',
    'delay': 10
}
session = requests.session()
session.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
scraper = cloudscraper.create_scraper(sess=session, **scraper_options)

processed_ad_ids = set()
try:
    with open(processed_ids_filepath, 'r') as f:
        processed_ad_ids = set(json.load(f))
    print(f"Se cargaron {len(processed_ad_ids)} IDs de anuncios ya procesados.")
except FileNotFoundError:
    print("No se encontró el archivo de IDs procesados. Se iniciará un nuevo seguimiento.")
except json.JSONDecodeError:
    print("Error al decodificar el archivo de IDs procesados. Se iniciará un nuevo seguimiento.")

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

try:
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if os.stat(csv_filepath).st_size == 0:
            writer.writeheader()
        total_ads_processed = 0
        newly_processed_count = 0

        for page in range(1,MAX_PAGE + 1):
            print(f"Procesando página {page}/{MAX_PAGE}...")
            full_url = f"{URL}search?order=date&page={page}&category=vivienda&province=la-habana"
            try:
                response = scraper.get(url=full_url)
                response.raise_for_status()
                time.sleep(0.2)
            except cloudscraper.exceptions.CloudflareException as e:
                print(f"Error de Cloudflare en página {page}: {e}. Saltando página.")
                time.sleep(10)
                continue
            except requests.exceptions.RequestException as e:
                print(f"Error de red en página {page}: {e}. Saltando página.")
                time.sleep(5)
                continue
            except Exception as e:
                print(f"Error inesperado en página {page}: {e}. Saltando página.")
                time.sleep(5)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            new_links = soup.find_all("a", class_="sc-f2ab0e3a-1 sc-f2ab0e3a-8 hyLyPh")
            print(f"Encontrados {len(new_links)} anuncios en página {page}.")

            if not new_links and page > 1:
                print(f"Advertencia: No se encontraron anuncios en la página {page}. Puede ser un error temporal.")

            for index, link in enumerate(new_links):
                ad_relative_url = link.get("href")
                if not ad_relative_url or not ad_relative_url.startswith('/item/'):
                    continue

                ad_url = URL.rstrip('/') + ad_relative_url
                print(f"  Procesando Ad #{total_ads_processed + 1} (Pag {page}, Idx {index + 1}) -> {ad_url[-20:]}", end=" ")

                try:
                    response2 = scraper.get(url=ad_url)
                    response2.raise_for_status()
                    time.sleep(0.1)
                except cloudscraper.exceptions.CloudflareException:
                    print("... Error Cloudflare Ad. Skip.")
                    time.sleep(10)
                    continue
                except requests.exceptions.RequestException:
                    print("... Error Red Ad. Skip.")
                    continue
                except Exception as e:
                    print(f"... Error Ad: {e}. Skip.")
                    continue

                soup2 = BeautifulSoup(response2.text, "html.parser")
                ad_data = {'ID': "N/A"}

                try:
                    ad_id_element = soup2.select_one("div.sc-af4a0d21-10.buzTPQ p[data-cy='adId']")
                    if ad_id_element:
                        match = re.search(r'ID anuncio:\s*(\d+)', ad_id_element.text)
                        ad_id = match.group(1) if match else None
                    else:
                        ad_id = None

                    if ad_id and ad_id in processed_ad_ids:
                        print("... Anuncio ya procesado. Saltando.")
                        continue

                    if ad_id:
                        ad_data['ID'] = ad_id
                        title_el = soup2.find("h1", class_="sc-6aedc804-0 ddbmCp")
                        ad_data['Titulo'] = title_el.text.strip() if title_el else "Sin título"

                        price_el = soup2.find("span", class_="sc-6aedc804-2 hxIhEw")
                        ad_data['Precio'] = price_el.text.strip().split()[0].replace(",", "") if price_el else "N/A"

                        contact_div = soup2.find("div", class_="sc-8c587eb8-1 bCmlyu")
                        contactos = []
                        if contact_div:
                            call_link = contact_div.select_one("a[href^='tel:']")
                            if call_link:
                                num = call_link.get('href', '').replace('tel:', '')
                                contactos.append(num)
                            wa_link = contact_div.select_one("a[href^='https://wa.me/']")
                            if wa_link:
                                num_wa = wa_link.get('href').split('/')[-1].split('?')[0]
                                contactos.append(num_wa)
                        ad_data['Contactos'] = "; ".join(contactos) if contactos else "N/A"

                        desc_el = soup2.find("p", class_="sc-f0f0ca2b-1 hAoMGF")
                        ad_data['Descripcion'] = desc_el.text.strip() if desc_el else "N/A"
                        name_el = soup2.select_one("div.sc-8c587eb8-2.idzKqV p[data-cy='adName']")
                        ad_data['Nombre'] = name_el.text.strip() if name_el else "N/A"
                        loc_el = soup2.select_one('p[data-cy="adLocation"]')
                        ad_data['Ubicacion'] = loc_el.text.strip() if loc_el else "N/A"
                        ad_data['Fecha'] = "N/A"
                        
                        try:
                            script_tag = soup2.find('script', id='__NEXT_DATA__')
                            if script_tag:
                                data = json.loads(script_tag.string)
                                key = f"AdType:{ad_data['ID']}"
                                state = data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})
                                upd = state.get(key, {}).get('updatedOnByUser')
                                if upd: ad_data['Fecha'] = upd.split('T')[0]
                        except Exception:
                            pass
                        ad_data['URL'] = ad_url

                        writer.writerow(ad_data)
                        processed_ad_ids.add(ad_id)
                        newly_processed_count += 1
                        print("... OK")
                    else:
                        print("... No se pudo extraer el ID del anuncio. Saltando.")
                except Exception as e_inner:
                    print(f"\n  Error procesando detalles del anuncio: {e_inner}. Skip.")
                    continue
            print(f"\nTerminada página {page}. Anuncios procesados en esta página: {newly_processed_count}")
            total_ads_processed += len(new_links)
            newly_processed_count = 0

except IOError as e:
    print(f"\nError al escribir en el archivo CSV '{csv_filepath}': {e}")
    print("Verifica que tienes permisos de escritura.")

finally:
    try:
        with open(processed_ids_filepath, 'w') as f:
            json.dump(list(processed_ad_ids), f)
        print(f"\nSe guardaron {len(processed_ad_ids)} IDs procesados en {processed_ids_filepath}.")
    except Exception as e:
        print(f"\nError guardando IDs procesados: {e}")

print(f"\n¡Proceso completado! Se intentaron procesar {total_ads_processed} anuncios.")
print(f"Datos guardados en: {csv_filepath}")
