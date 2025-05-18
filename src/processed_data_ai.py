import time
import csv
import json
import os
import sys
from google import genai

genai_client = genai.Client(api_key="AIzaSyBdGobHm6D5CLDOKkLdg600uHwmbajXAUM")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dir_raw = os.path.join(BASE_DIR, "data", "raw")
dir_processed = os.path.join(BASE_DIR, "data", "processed")

source = "porlalivre"
input_filename = "porlalivre.csv"
output_filename = "processed.csv"
processed_ids_json = os.path.join(dir_processed, "processed_ids.json")
input_path = os.path.join(dir_raw, input_filename)
output_path = os.path.join(dir_processed, output_filename)


if not os.path.exists(input_path):
    print(f"Error: no se encontro '{input_path}'")
    sys.exit(1)

VALID_MUNICIPALITIES = [
    "Arroyo Naranjo",
    "Boyeros",
    "Centro Habana",
    "Cerro",
    "Cotorro",
    "Diez de Octubre",
    "Guanabacoa",
    "Habana del Este",
    "La Habana Vieja",
    "La Lisa",
    "Marianao",
    "Plaza de la Revolución",
    "Playa",
    "Regla",
    "San Miguel del Padrón",
]

json_schema = {
    "type": "object",
    "properties": {
        "ID": {"type": "string"},
        "Titulo": {"type": "string"},
        "Tipo": {
            "type": "string",
            "enum": ["casa", "apartamento", "terreno", "local", "otro"],
        },
        "Categoria": {
            "type": "string",
            "enum": ["venta", "alquiler", "permuta", "compra", "otro"],
        },
        "Precio": {"type": "number"},
        "Moneda": {"type": "string", "enum": ["USD", "CUP", "EUR", "CUC", "otro"]},
        "Nombre": {"type": "string"},
        "Contactos": {"type": "array", "items": {"type": "string"}},
        "Cuartos": {"type": "integer"},
        "Banos": {"type": "integer"},
        "Garaje": {"type": "boolean"},
        "Amenidades": {"type": "array", "items": {"type": "string"}},
        "Ubicacion": {
            "type": "array",
            "items": [
                {"type": "string", "enum": VALID_MUNICIPALITIES},
                {"type": "string", "enum": ["La Habana"]},
            ],
        },
        "Fecha": {"type": "string", "format": "date"},
        "URL": {"type": "string", "format": "uri"},
    },
    "required": [
        "ID",
        "Titulo",
        "Tipo",
        "Categoria",
        "Precio",
        "Moneda",
        "Contactos",
        "Nombre",
        "Cuartos",
        "Banos",
        "Garaje",
        "Amenidades",
        "Ubicacion",
        "Fecha",
        "URL",
    ],
    "additionalProperties": False,
}

processed_ids = set()
if os.path.exists(processed_ids_json):
    with open(processed_ids_json, "r", encoding="utf-8") as f:
        processed_ids = set(json.load(f))



unprocessed_rows = []
with open(input_path, "r", encoding="utf-8", newline='') as fi:
    reader = csv.DictReader(fi, quoting=csv.QUOTE_ALL)
    for row in reader:
        if row["ID"] not in processed_ids:

            row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
            unprocessed_rows.append(row)

def process_batch(batch_rows):
    batch_data = []
    for row in batch_rows:
        cleaned_data = {
            "ID": row.get("ID", "").strip(),
            "Titulo": row.get("Titulo", "").strip(),
            "Descripcion": row.get("Descripcion", "").strip(),
            "Precio": row.get("Precio", "").strip(),
            "Nombre": row.get("Nombre", "").strip(),
            "Contactos": row.get("Contactos", "").strip(),
            "Ubicacion": row.get("Ubicacion", "").strip(),
            "Fecha": row.get("Fecha", "").strip(),
            "URL": row.get("URL", "").strip()
        }
        batch_data.append(cleaned_data)
        
        current_date_for_prompt = time.strftime("%Y-%m-%d")
        batch_prompt = f"""Eres un asistente experto en extracción de datos de anuncios inmobiliarios.
Procesa los siguientes {len(batch_data)} anuncios y devuelve un array de objetos JSON que cumplan con este esquema:
{json.dumps(json_schema, indent=2)}

Instrucciones detalladas para la extracción:
0. Devuelve un array JSON con {len(batch_data)} elementos
1.  ID: Utiliza el ID proporcionado.
2.  Titulo: Utiliza el Título proporcionado.
3.  Tipo: Infiere de Título y Descripción. Debe ser uno de: {json_schema['properties']['Tipo']['enum']}. Si no es claro o no encaja, usa "otro".
4.  Categoria: Infiere de Título y Descripción (ej. "venta", "alquiler", "permuta", "compra"). Debe ser uno de: {json_schema['properties']['Categoria']['enum']}. Si no es claro o no encaja, usa "otro".
5.  Precio: Extrae el valor numérico del precio del campo 'Precio' o de la 'Descripcion'. Si el precio es "N/A", no numérico,o no guarda relacion con el de 'Precio', o no se especifica un valor claro, usa 0 como valor numérico.
6.  Moneda: Infiere la moneda del precio (ej: USD, CUP, EUR, CUC). Debe ser una de: {json_schema['properties']['Moneda']['enum']}. Si no se especifica, no es clara, o si el precio es 0 debido a la instrucción anterior, usa "otro".
7.  Nombre: Utiliza el Nombre proporcionado. Si está vacío o es "N/A", intenta extraerlo del texto del anuncio si es posible, de lo contrario usa "No especificado".
8.  Contactos: Extrae todos los números de contacto o correos. Debe ser un array de strings. Si el campo 'Contactos' del anuncio contiene múltiples contactos separados por punto y coma, espacios u otro delimitador, sepáralos en elementos individuales del array. Ejemplo: si 'Contactos' es "555; 666", el JSON debe ser ["555", "666"]. Si no hay contactos claros, usa un array vacío [].
9.  Cuartos: Infiere el número de cuartos/habitaciones de Título y Descripción. Debe ser un entero. Si no se menciona o no está claro, usa 0.
10. Banos: Infiere el número de baños de Título y Descripción. Debe ser un entero. Si no se menciona o no está claro, usa 0.
11. Garaje: Infiere si tiene garaje (true/false) de Título y Descripción. Si no se menciona o no está claro, usa false.
12. Amenidades: Extrae una lista de amenidades o características especiales (ej: "piscina", "amueblado", "planta eléctrica", "nauta hogar", "balcón", "terraza","tanques propios","gas de la calle","telefono fijo") entre otros que puedas asumir por ti  de Título y Descripción. Debe ser un array de strings. Si no hay o no están claras, usa un array vacío [].
13. Ubicacion: Analiza la ubicación proporcionada y extrae el municipio y la provincia. 
    El municipio debe ser uno de: {", ".join(VALID_MUNICIPALITIES)}
    La provincia debe ser "La Habana"
    Si no se puede determinar el municipio específico, usa el municipio más probable según el contexto.
    Devolver como objeto con formato: {"nombre_municipio", "provincia"}
14. Fecha: Utiliza la Fecha proporcionada. Si es una descripción textual (ej: "hace un mes", "ayer"), intenta convertirla al formato YYYY-MM-DD basándote en que la fecha actual es {current_date_for_prompt}. Si ya está en formato fecha válido (YYYY-MM-DD), úsala directamente. Si no se puede determinar una fecha válida, está vacía o es "N/A", usa una cadena vacía "".
15. URL: Utiliza la URL proporcionada. Si está vacía o es "N/A", usa una cadena vacía "".
16. No incluyas explicaciones, solo el array JSON

Asegúrate de que todos los campos marcados como "required" en el esquema estén presentes en tu respuesta JSON. El JSON debe ser completo y válido.

Anuncios a procesar:
{json.dumps(batch_data, indent=2, ensure_ascii=False)}
"""

    try:
        time.sleep(2)
        resp = genai_client.models.generate_content(
            model="gemini-2.0-flash-001", contents=batch_prompt
        )

        raw = resp.text.strip()
        if raw.startswith("```json"):
            raw = "\n".join(raw.splitlines()[1:-1]).strip()
        elif raw.startswith("```"):
            raw = "\n".join(raw.splitlines()[1:-1]).strip()

        processed_data = json.loads(raw)
        return processed_data

    except Exception as e:
        print(f"Error procesando lote: {e}")
        return None

headers = [
    "ID", "Fuente", "Titulo", "Tipo", "Categoria", "Precio", "Moneda",
    "Contactos", "Nombre", "Cuartos", "Banos", "Garaje", "Amenidades",
    "Ubicacion", "Fecha", "URL"
]

BATCH_SIZE = 10
file_exists = os.path.exists(output_path)

mode = "a" if file_exists else "w"
with open(output_path, "a", newline="", encoding="utf-8") as fo:
    writer = csv.DictWriter(
        fo, 
        fieldnames=headers,
        quoting=csv.QUOTE_ALL,
        escapechar='\\'
    )
    
    if not file_exists:
        writer.writeheader()

    for i in range(0, len(unprocessed_rows), BATCH_SIZE):
        batch = unprocessed_rows[i:i + BATCH_SIZE]
        print(f"\nProcesando lote {i//BATCH_SIZE + 1} ({len(batch)} anuncios)")

        processed_batch = process_batch(batch)
        if not processed_batch:
            continue

        for row, processed_data in zip(batch, processed_batch):
            aid = row["ID"]
            try:
                amenidades = processed_data.get("Amenidades", [])
                amenidades_str = ", ".join(str(a).strip() for a in amenidades if a)
                
                out_row = {
                    "ID": processed_data["ID"],
                    "Fuente": source,
                    "Titulo": processed_data["Titulo"],
                    "Tipo": processed_data["Tipo"],
                    "Categoria": processed_data["Categoria"],
                    "Precio": processed_data["Precio"],
                    "Moneda": processed_data["Moneda"],
                    "Ubicacion": json.dumps(processed_data["Ubicacion"], ensure_ascii=False),
                    "Nombre": processed_data["Nombre"],
                    "Contactos": json.dumps(processed_data["Contactos"], ensure_ascii=False),
                    "Cuartos": processed_data["Cuartos"],
                    "Banos": processed_data["Banos"],
                    "Garaje": processed_data["Garaje"],
                    "Amenidades": amenidades_str,
                    "Fecha": processed_data["Fecha"],
                    "URL": processed_data["URL"]
                }
                writer.writerow(out_row)

                processed_ids.add(aid)
                with open(processed_ids_json, "w", encoding="utf-8") as f:
                    json.dump(list(processed_ids), f, indent=2, ensure_ascii=False)

                print(f"Procesado ID {aid}")

            except Exception as e:
                print(f"Error procesando ID {aid}: {e}")
                continue

        print(f"\nCompletado lote {i//BATCH_SIZE + 1}")

print("\nProcesamiento completado")
print(f"Total de IDs procesados: {len(processed_ids)}")