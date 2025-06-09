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
             df["Precio"]*1
            ]
    
    df.loc[:,"Precio"]=np.select(conditions,values,df["Precio"])
    
    df["Moneda"] = "USD"
    
    return df


def clean_amenities(df:pd.DataFrame)->pd.DataFrame:
    df.loc[:,"Amenidades"]=df["Amenidades"].str.lower()
    df.loc[:,"Amenidades"]=df["Amenidades"].str.split(',')
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
    return df