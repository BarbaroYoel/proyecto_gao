import pandas as pd
import ast
import numpy as np

def cleaning_data_frame_by_category(
    df: pd.DataFrame, category: str, min_outliner: int, max_outliner: int) -> pd.DataFrame:
    df=cleaning_data_frame(df)
   
    if category == "venta" or category == "alquiler" or category=="permuta":
        df = df[(df["Categoria"] == category)].copy()
    elif category == "alquiler":
        df = df[(df["Categoria"] == category)].copy()
    elif category=="permuta":
        df = df[(df["Categoria"] == category)].copy()
    else:
        raise ValueError(f"Categoría '{category}' no encontrada")
    df = remove_outliers(df, min_outliner, max_outliner)
    return df


def cleaning_data_frame(df:pd.DataFrame)->pd.DataFrame :
    df=clean_price(df)
    df=clean_amenities(df)
    df=clean_locations(df)
    df=clean_date(df)
    return df


def remove_outliers(df: pd.DataFrame, min_value: int, max_value: int) -> pd.DataFrame:
    return df[(df["Precio"] > min_value) & (df["Precio"] < max_value)].copy()


def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce")
    
    df = df[(df["Moneda"] == "USD") |(df["Moneda"] == "EUR") | (df["Moneda"] == "CUP") | (df["Moneda"] == "CUC")].copy()
    
    conditions=[(df["Moneda"] == "EUR") , 
                (df["Moneda"] == "CUP") , 
                (df["Moneda"] == "CUC")]
    
    values=[ df["Precio"]*1.1,
             df["Precio"]/360,
             df["Precio"]*1.1
            ]
    df.loc[:,"Precio"]=np.select(conditions,values,df["Precio"])
    
    df["Moneda"] = "USD"
    return df


def clean_amenities(df: pd.DataFrame) -> pd.DataFrame:
    normalization_map = {
        'parqueo': 'Estacionamiento',
        'garaje': 'Estacionamiento',
        'cochera': 'Estacionamiento',
        'aire': 'Aire Acondicionado',
        'balcon': 'Balcón',
        "telefono fijo": "Teléfono fijo",
        "teléfono": "Teléfono fijo",
        "tanque instalado": "Tanque elevado",
        "placa libre": "Terraza",
        "tanques propios": "Tanque elevado",
        "split": "Aire Acondicionado",
        "motor": "Planta eléctrica",
        "generador": "Planta eléctrica",
        "planta electrica": "Planta eléctrica",
        "planta eléctrica": "Planta eléctrica",
        "cisterna": "Tanque elevado",
        "alberca": "Piscina",
        "lavadora": "Lavadora",
        "lavarropa": "Lavadora",
        "tv": "Televisor",
        "television": "Televisor",
        "ventilador": "Ventilador",
        "abanico": "Ventilador",
        "wifi": "Internet",
        "internet": "Internet",
        "nauta": "Internet",
        "camaras de seguridad": "Cámaras seguridad",
        "seguridad": "Cámaras seguridad",
        "cámaras seguridad": "Cámaras seguridad",
        "jacuzzi": "Jacuzzi",
        "hidromasaje": "Jacuzzi",
        "jardin": "Jardín",
        "patio": "Jardín",
        "caja fuerte": "Caja fuerte",
        "seguro": "Caja fuerte",
        "amueblado": "Amueblado",
        "muebles": "Amueblado"
    }

    amenities_raw = (
        df["Amenidades"]
        .fillna("")
        .astype(str)
        .str.lower()
        .apply(lambda x: x.split(',') if x != "" else [])
    )

    def normalize_amenities(amenities_list):
        normalized = set()
        for amenity in amenities_list:
            clean_amenity = amenity.strip().replace('"', '').replace("'", "")
            if clean_amenity in normalization_map:
                normalized.add(normalization_map[clean_amenity])
            else:
                found = False
                for key, value in normalization_map.items():
                    if key in clean_amenity:
                        normalized.add(value)
                        found = True
                        break
                if not found and clean_amenity:
                    normalized.add(clean_amenity.title())
        return sorted(normalized)

    # Use direct column assignment so pandas can safely switch dtype to object (lists).
    df["Amenidades"] = amenities_raw.apply(normalize_amenities)
    return df

    
def clean_locations(df:pd.DataFrame)->pd.DataFrame:
    def _clean_locations(x:str):
        try:
            cleaned = x.replace('[""', '"').replace('""]', '"')
            return ast.literal_eval(cleaned)
        except (ValueError, SyntaxError, TypeError):
            return []
    
    df["Ubicacion"] = df["Ubicacion"].apply(_clean_locations)
    df["Municipio"] = df["Ubicacion"].apply(lambda x: x[0] if len(x) > 1 else None)
    df["Provincia"] = df["Ubicacion"].apply(lambda x: x[1] if len(x) > 2 else None)

    df.drop(columns=["Ubicacion"], inplace=True)
    NORMALIZACION_MUNICIPIOS = {
        "Plaza": "Plaza de la Revolución",
        "Habana Vieja": "La Habana Vieja"
    }
    df["Municipio"] = df["Municipio"].replace(NORMALIZACION_MUNICIPIOS)
    return df


def clean_date(df :pd.DataFrame)->pd.DataFrame:
    if 'Fecha' in df:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    return df