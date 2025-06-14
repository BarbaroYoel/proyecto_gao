import cloudscraper
from bs4 import BeautifulSoup
import requests
import json
import time
import csv
import os

URL = "https://www.revolico.com/"
MAX_PAGE = 80
print(f"Se procesarán las primeras {MAX_PAGE} páginas.")

# --- Configuración de rutas (sin cambios) ---
# Se asume que el script está en un subdirectorio, ajusta si es necesario
script_dir = os.path.dirname(os.path.abspath(__file__))
# Si 'gao_dir' no es lo que esperas, puedes definir la ruta directamente
# Ejemplo: output_raw_dir = os.path.join('data', 'raw')
gao_dir = os.path.dirname(os.path.dirname(script_dir))
output_raw_dir = os.path.join(gao_dir, 'data', 'raw')
csv_filepath = os.path.join(output_raw_dir, 'revolico.csv')
processed_ids_filepath = os.path.join(output_raw_dir, 'revolico_raw_ids.json')

os.makedirs(output_raw_dir, exist_ok=True)
print(f"Ruta de salida configurada en: {output_raw_dir}")
print(f"Archivo CSV de salida será: {csv_filepath}")
print(f"Archivo de IDs procesados será: {processed_ids_filepath}")

# --- Configuración de Scraper (sin cambios) ---
scraper_options = {
    'browser': 'chrome',
    'delay': 10
}
session = requests.session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
scraper = cloudscraper.create_scraper(sess=session, **scraper_options)

# --- Carga de IDs procesados (sin cambios) ---
processed_ad_ids = set()
try:
    with open(processed_ids_filepath, 'r') as f:
        processed_ad_ids = set(json.load(f))
    print(f"Se cargaron {len(processed_ad_ids)} IDs de anuncios ya procesados.")
except FileNotFoundError:
    print("No se encontró el archivo de IDs procesados. Se iniciará un nuevo seguimiento.")
except json.JSONDecodeError:
    print("Error al decodificar el archivo de IDs procesados. Se iniciará un nuevo seguimiento.")

# --- Encabezados del CSV (sin cambios) ---
headers = [
    "ID", "Titulo", "Precio", "Ubicacion", "Descripcion",
    "Nombre", "Contactos", "Fecha", "URL"
]

def get_apollo_state(soup):
    """Extrae y parsea el JSON del __APOLLO_STATE__ desde la sopa de BeautifulSoup."""
    script_tag = soup.find('script', id='__NEXT_DATA__')
    if not script_tag:
        print("... No se encontró la etiqueta __NEXT_DATA__. Saltando.")
        return None
    try:
        data = json.loads(script_tag.string)
        return data.get('props', {}).get('pageProps', {}).get('__APOLLO_STATE__', {})
    except (json.JSONDecodeError, TypeError):
        print("... Error al decodificar el JSON de __NEXT_DATA__. Saltando.")
        return None

try:
    with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if os.stat(csv_filepath).st_size == 0:
            writer.writeheader()
        
        total_ads_processed_session = 0

        for page in range(63, MAX_PAGE + 1):
            print(f"Procesando página de resultados {page}/{MAX_PAGE}...")
            full_url = f"{URL}search?order=date&page={page}&category=vivienda&province=la-habana"
            
            try:
                response = scraper.get(url=full_url)
                response.raise_for_status()
                time.sleep(0.5) # Un pequeño delay para no saturar
            except (cloudscraper.exceptions.CloudflareException, requests.exceptions.RequestException) as e:
                print(f"Error de red o Cloudflare en página {page}: {e}. Saltando página.")
                time.sleep(10)
                continue
            except Exception as e:
                print(f"Error inesperado en página {page}: {e}. Saltando página.")
                continue

            soup_list = BeautifulSoup(response.text, "html.parser")
            apollo_state_list = get_apollo_state(soup_list)

            if not apollo_state_list:
                print(f"No se pudo obtener el estado de Apollo para la página {page}. Saltando.")
                continue

            # Extraer los permalinks y IDs de la página de resultados
            ads_on_page = [v for v in apollo_state_list.values() if v.get('__typename') == 'AdType']
            print(f"Encontrados {len(ads_on_page)} anuncios en la página {page}.")

            if not ads_on_page and page > 1:
                 print(f"Advertencia: No se encontraron anuncios en la página {page}. Puede ser el final o un error.")

            for ad_summary in ads_on_page:
                ad_id = ad_summary.get('id')
                ad_permalink = ad_summary.get('permalink')

                if not ad_id or not ad_permalink:
                    continue

                if ad_id in processed_ad_ids:
                    print(f"  Anuncio ID {ad_id} ya procesado. Saltando.")
                    continue
                
                ad_url = URL.rstrip('/') + ad_permalink
                print(f"  Procesando Ad ID {ad_id} -> {ad_url[-20:]}", end=" ")

                try:
                    response2 = scraper.get(url=ad_url)
                    response2.raise_for_status()
                    time.sleep(0.2) # Delay
                except (cloudscraper.exceptions.CloudflareException, requests.exceptions.RequestException) as e:
                    print(f"... Error de red o Cloudflare en Ad: {e}. Skip.")
                    time.sleep(10)
                    continue
                except Exception as e:
                    print(f"... Error Ad: {e}. Skip.")
                    continue

                soup2 = BeautifulSoup(response2.text, "html.parser")
                apollo_state_ad = get_apollo_state(soup2)

                if not apollo_state_ad:
                    print(f"... No se pudo obtener el estado de Apollo para el anuncio {ad_id}. Skip.")
                    continue
                
                # Buscar los datos del anuncio en el estado de Apollo
                key = f"AdType:{ad_id}"
                ad_details = apollo_state_ad.get(key)

                if not ad_details:
                    print(f"... No se encontraron detalles para el Ad ID {ad_id} en Apollo State. Skip.")
                    continue

                try:
                    ad_data = {}
                    ad_data['ID'] = ad_id
                    ad_data['Titulo'] = ad_details.get('title', 'N/A').strip()
                    ad_data['Precio'] = ad_details.get('price', 'N/A')
                    ad_data['Descripcion'] = ad_details.get('description', 'N/A').strip()
                    
                    # Extraer Ubicacion
                    province_ref = ad_details.get('province', {}).get('__ref')
                    municipality_ref = ad_details.get('municipality', {}).get('__ref')
                    province_name = apollo_state_ad.get(province_ref, {}).get('name', '')
                    municipality_name = apollo_state_ad.get(municipality_ref, {}).get('name', '')
                    ad_data['Ubicacion'] = f"{municipality_name}, {province_name}".strip(', ')

                    # Extraer Nombre del contacto
                    user_ref = ad_details.get('user({\"mask\":true})', {}).get('__ref')
                    ad_data['Nombre'] = apollo_state_ad.get(user_ref, {}).get('name', 'N/A')

                    # Extraer Contactos
                    phone_info = ad_details.get('phoneInfo', {})
                    contactos = []
                    if phone_info:
                        first_phone = phone_info.get('firstPhone')
                        second_phone = phone_info.get('secondPhone')
                        if first_phone and first_phone.get('number'):
                            contactos.append(first_phone.get('number'))
                        if second_phone and second_phone.get('number'):
                            contactos.append(second_phone.get('number'))
                    ad_data['Contactos'] = "; ".join(contactos) if contactos else "N/A"

                    ad_data['Fecha'] = ad_details.get('updatedOnByUser', 'N/A').split('T')[0]
                    ad_data['URL'] = ad_url
                    
                    writer.writerow(ad_data)
                    processed_ad_ids.add(ad_id)
                    total_ads_processed_session += 1
                    print("... OK")

                except Exception as e_inner:
                    print(f"\n  Error procesando detalles del anuncio JSON {ad_id}: {e_inner}. Skip.")
                    continue
        
        print(f"\nTerminadas {MAX_PAGE} páginas.")

except IOError as e:
    print(f"\nError al escribir en el archivo CSV '{csv_filepath}': {e}")
    print("Verifica que tienes permisos de escritura y que el archivo no está abierto.")
finally:
    try:
        with open(processed_ids_filepath, 'w') as f:
            json.dump(list(processed_ad_ids), f)
        print(f"\nSe guardaron {len(processed_ad_ids)} IDs procesados en {processed_ids_filepath}.")
    except Exception as e:
        print(f"\nError guardando IDs procesados: {e}")

print(f"\n¡Proceso completado! Se procesaron {total_ads_processed_session} anuncios nuevos en esta sesión.")
print(f"Total de anuncios en el archivo: {len(processed_ad_ids)}.")
print(f"Datos guardados en: {csv_filepath}")