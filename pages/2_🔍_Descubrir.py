import os 
import sys
import Inicio as inicio
import streamlit as st
import pandas as pd
import plotly.express as px


parent_directory=os.getcwd()
print(parent_directory)
path=os.path.join(parent_directory,'src')
print(path)
sys.path.append(parent_directory)

import src.cleaning_data as cln

@st.cache_data
def load_data(category:str)-> pd.DataFrame :
    path =os.getcwd()
    data_file=os.path.join(path,"data","processed","processed.csv")
    df=pd.read_csv(data_file).copy()
    
    if category=="Alquileres":
      df= cln.cleaning_data_frame_by_category(df,"alquiler",min_outliner=10,max_outliner=1500)

    elif category=="Ventas" :
      df = cln.cleaning_data_frame_by_category(df,"venta",min_outliner=1000,max_outliner=1500000)
    
    return df


def show_kpis(df:pd.DataFrame)->pd.DataFrame :
     # Validaciones
    if 'Fecha' not in df.columns:
        st.warning("No se encontró la columna 'Fecha'.")
        return
    if 'Precio' not in df.columns or 'Municipio' not in df.columns:
        st.warning("Faltan columnas esenciales ('Precio' o 'Municipio').")
        return
    if df.empty:
        st.warning("No hay datos tras los filtros.")
        return

    df = df.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    now = pd.Timestamp.now()
    inicio_6m = now - pd.DateOffset(months=6)
    df_6m = df[df['Fecha'] >= inicio_6m]

    # 1) Conteo de anuncios
    total_all = len(df)
    total_6m = len(df_6m)
    # Para delta: diferencia directa 6m - overall
    delta_count = total_6m - total_all if total_all is not None else None

    # Grupos para conteo por municipio
    grp_cnt_all = df['Municipio'].dropna().value_counts()
    grp_cnt_6m = df_6m['Municipio'].dropna().value_counts()
    # Top y bottom overall
    if not grp_cnt_all.empty:
        top_cnt_all = (grp_cnt_all.idxmax(), int(grp_cnt_all.max()))
        # Para bottom: considerar sólo municipios presentes; si hay varios, toma el mínimo positivo
        bottom_cnt_all = (grp_cnt_all.idxmin(), int(grp_cnt_all.min()))
    else:
        top_cnt_all = (None, None)
        bottom_cnt_all = (None, None)
    # Top y bottom 6m
    if not grp_cnt_6m.empty:
        top_cnt_6m = (grp_cnt_6m.idxmax(), int(grp_cnt_6m.max()))
        bottom_cnt_6m = (grp_cnt_6m.idxmin(), int(grp_cnt_6m.min()))
    else:
        top_cnt_6m = (None, None)
        bottom_cnt_6m = (None, None)

    # 2) Precio medio
    precio_all = df['Precio'].dropna()
    mean_all = precio_all.mean() if not precio_all.empty else None
    precio_6 = df_6m['Precio'].dropna()
    mean_6m = precio_6.mean() if not precio_6.empty else None
    delta_mean = None
    if mean_all is not None and mean_6m is not None:
        delta_mean = mean_6m - mean_all

    # Grupos para media por municipio
    grp_mean_all = df.dropna(subset=['Precio','Municipio']).groupby('Municipio')['Precio'].mean()
    grp_mean_6m = df_6m.dropna(subset=['Precio','Municipio']).groupby('Municipio')['Precio'].mean()
    if not grp_mean_all.empty:
        top_mean_all = (grp_mean_all.idxmax(), grp_mean_all.max())
        bottom_mean_all = (grp_mean_all.idxmin(), grp_mean_all.min())
    else:
        top_mean_all = (None, None)
        bottom_mean_all = (None, None)
    if not grp_mean_6m.empty:
        top_mean_6m = (grp_mean_6m.idxmax(), grp_mean_6m.max())
        bottom_mean_6m = (grp_mean_6m.idxmin(), grp_mean_6m.min())
    else:
        top_mean_6m = (None, None)
        bottom_mean_6m = (None, None)

    # 3) Precio mediano
    median_all = precio_all.median() if not precio_all.empty else None
    median_6m = precio_6.median() if not precio_6.empty else None
    delta_median = None
    if median_all is not None and median_6m is not None:
        delta_median = median_6m - median_all

    # Grupos para mediana por municipio
    grp_med_all = df.dropna(subset=['Precio','Municipio']).groupby('Municipio')['Precio'].median()
    grp_med_6m = df_6m.dropna(subset=['Precio','Municipio']).groupby('Municipio')['Precio'].median()
    if not grp_med_all.empty:
        top_med_all = (grp_med_all.idxmax(), grp_med_all.max())
        bottom_med_all = (grp_med_all.idxmin(), grp_med_all.min())
    else:
        top_med_all = (None, None)
        bottom_med_all = (None, None)
    if not grp_med_6m.empty:
        top_med_6m = (grp_med_6m.idxmax(), grp_med_6m.max())
        bottom_med_6m = (grp_med_6m.idxmin(), grp_med_6m.min())
    else:
        top_med_6m = (None, None)
        bottom_med_6m = (None, None)

    # 4) Precio moda
    modos_all = precio_all.mode() if not precio_all.empty else pd.Series(dtype=float)
    mode_all = modos_all.iloc[0] if not modos_all.empty else None
    modos_6 = precio_6.mode() if not precio_6.empty else pd.Series(dtype=float)
    mode_6m = modos_6.iloc[0] if not modos_6.empty else None
    delta_mode = None
    if mode_all is not None and mode_6m is not None:
        delta_mode = mode_6m - mode_all

    # Grupos para moda por municipio
    def modo_serie(s: pd.Series):
        m = s.mode()
        return m.iloc[0] if not m.empty else np.nan

    grp_mode_all = df.dropna(subset=['Precio','Municipio']).groupby('Municipio')['Precio'].apply(modo_serie)
    grp_mode_6m = df_6m.dropna(subset=['Precio','Municipio']).groupby('Municipio')['Precio'].apply(modo_serie)
    # Filtrar NaN
    grp_mode_all = grp_mode_all.dropna()
    grp_mode_6m = grp_mode_6m.dropna()
    if not grp_mode_all.empty:
        top_mode_all = (grp_mode_all.idxmax(), grp_mode_all.max())
        bottom_mode_all = (grp_mode_all.idxmin(), grp_mode_all.min())
    else:
        top_mode_all = (None, None)
        bottom_mode_all = (None, None)
    if not grp_mode_6m.empty:
        top_mode_6m = (grp_mode_6m.idxmax(), grp_mode_6m.max())
        bottom_mode_6m = (grp_mode_6m.idxmin(), grp_mode_6m.min())
    else:
        top_mode_6m = (None, None)
        bottom_mode_6m = (None, None)

    # Función auxiliar para formatear delta numérico
    def fmt_delta(x):
        try:
            return f"{x:+,.0f}"
        except:
            return None

    # Display por filas de dos columnas y luego municipios debajo
    # 1) Conteo
    cols = st.columns(2)
    cols[0].metric("Total anuncios (all)", f"{total_all}")
    delta_cnt = fmt_delta(delta_count) if delta_count is not None else None
    cols[1].metric("Anuncios últimos (6m)", f"{total_6m}", delta=delta_cnt)
    # Municipios para conteo
    col1, col2 = st.columns(2)
    if top_cnt_all[0]:
        col1.write(f"Mayor count all: {top_cnt_all[0]} ({top_cnt_all[1]})")
    else:
        col1.write("Mayor count all: N/A")
    if top_cnt_6m[0]:
        col2.write(f"Mayor count 6m: {top_cnt_6m[0]} ({top_cnt_6m[1]})")
    else:
        col2.write("Mayor count 6m: N/A")
    col1b, col2b = st.columns(2)
    if bottom_cnt_all[0]:
        col1b.write(f"Menor count all: {bottom_cnt_all[0]} ({bottom_cnt_all[1]})")
    else:
        col1b.write("Menor count all: N/A")
    if bottom_cnt_6m[0]:
        col2b.write(f"Menor count 6m: {bottom_cnt_6m[0]} ({bottom_cnt_6m[1]})")
    else:
        col2b.write("Menor count 6m: N/A")
    st.markdown("---")

    # 2) Precio medio
    cols = st.columns(2)
    if mean_all is not None:
        cols[0].metric("Precio medio (all)", f"{mean_all:,.0f} USD")
    else:
        cols[0].metric("Precio medio (all)", "N/A")
    if mean_6m is not None:
        cols[1].metric("Precio medio (6m)", f"{mean_6m:,.0f} USD", delta=fmt_delta(delta_mean))
    else:
        cols[1].metric("Precio medio (6m)", "N/A")
    # Municipios para media
    col1, col2 = st.columns(2)
    if top_mean_all[0]:
        col1.write(f"Mayor media all: {top_mean_all[0]} ({top_mean_all[1]:,.0f})")
    else:
        col1.write("Mayor media all: N/A")
    if top_mean_6m[0]:
        col2.write(f"Mayor media 6m: {top_mean_6m[0]} ({top_mean_6m[1]:,.0f})")
    else:
        col2.write("Mayor media 6m: N/A")
    col1b, col2b = st.columns(2)
    if bottom_mean_all[0]:
        col1b.write(f"Menor media all: {bottom_mean_all[0]} ({bottom_mean_all[1]:,.0f})")
    else:
        col1b.write("Menor media all: N/A")
    if bottom_mean_6m[0]:
        col2b.write(f"Menor media 6m: {bottom_mean_6m[0]} ({bottom_mean_6m[1]:,.0f})")
    else:
        col2b.write("Menor media 6m: N/A")
    st.markdown("---")

    # 3) Precio mediano
    cols = st.columns(2)
    if median_all is not None:
        cols[0].metric("Precio mediano (all)", f"{median_all:,.0f} USD")
    else:
        cols[0].metric("Precio mediano (all)", "N/A")
    if median_6m is not None:
        cols[1].metric("Precio mediano (6m)", f"{median_6m:,.0f} USD", delta=fmt_delta(delta_median))
    else:
        cols[1].metric("Precio mediano (6m)", "N/A")
    # Municipios para mediana
    col1, col2 = st.columns(2)
    if top_med_all[0]:
        col1.write(f"Mayor mediana all: {top_med_all[0]} ({top_med_all[1]:,.0f})")
    else:
        col1.write("Mayor mediana all: N/A")
    if top_med_6m[0]:
        col2.write(f"Mayor mediana 6m: {top_med_6m[0]} ({top_med_6m[1]:,.0f})")
    else:
        col2.write("Mayor mediana 6m: N/A")
    col1b, col2b = st.columns(2)
    if bottom_med_all[0]:
        col1b.write(f"Menor mediana all: {bottom_med_all[0]} ({bottom_med_all[1]:,.0f})")
    else:
        col1b.write("Menor mediana all: N/A")
    if bottom_med_6m[0]:
        col2b.write(f"Menor mediana 6m: {bottom_med_6m[0]} ({bottom_med_6m[1]:,.0f})")
    else:
        col2b.write("Menor mediana 6m: N/A")
    st.markdown("---")

    # 4) Moda precio
    cols = st.columns(2)
    if mode_all is not None:
        cols[0].metric("Moda precio (all)", f"{mode_all:,.0f} USD")
    else:
        cols[0].metric("Moda precio (all)", "N/A")
    if mode_6m is not None:
        cols[1].metric("Moda precio (6m)", f"{mode_6m:,.0f} USD", delta=fmt_delta(delta_mode))
    else:
        cols[1].metric("Moda precio (6m)", "N/A")
    # Municipios para moda
    col1, col2 = st.columns(2)
    if top_mode_all[0]:
        col1.write(f"Mayor moda all: {top_mode_all[0]} ({top_mode_all[1]:,.0f})")
    else:
        col1.write("Mayor moda all: N/A")
    if top_mode_6m[0]:
        col2.write(f"Mayor moda 6m: {top_mode_6m[0]} ({top_mode_6m[1]:,.0f})")
    else:
        col2.write("Mayor moda 6m: N/A")
    col1b, col2b = st.columns(2)
    if bottom_mode_all[0]:
        col1b.write(f"Menor moda all: {bottom_mode_all[0]} ({bottom_mode_all[1]:,.0f})")
    else:
        col1b.write("Menor moda all: N/A")
    if bottom_mode_6m[0]:
        col2b.write(f"Menor moda 6m: {bottom_mode_6m[0]} ({bottom_mode_6m[1]:,.0f})")
    else:
        col2b.write("Menor moda 6m: N/A")
   
    st.markdown("---")



def descubir_page():
    inicio.page_config()

    with st.sidebar:
      st.title("Proyecto Gao")
      st.image("assets/logo.png")
      st.sidebar.title('Filtros de Búsqueda')
      category = st.radio("Seleccione la categoría:",["Alquileres","Ventas"])
      df = load_data(category)
      
      municipality = df['Municipio'].dropna().unique().tolist()
      seleccion_mun =st.multiselect("Municipios",municipality,default= municipality)
       
      min_price, max_price=int(df["Precio"].min()),int(df["Precio"].max())
      range_price=st.slider("Rango de Precios USD:",min_price,max_price,(min_price,max_price))
    
      max_rooms = int(df['Cuartos'].max())
      rooms=st.slider("Habitaciones",0,max_rooms,(0,max_rooms))
  
      max_baths = int(df['Banos'].max())
      baths=st.slider("Baños",0,max_baths,(0,max_baths))
      
    df_filtered = df[
        (df["Municipio"].isin(seleccion_mun)) &
        (df['Precio'] >= range_price[0]) & (df['Precio'] <= range_price[1]) &
        (df['Cuartos'] >= rooms[0]) & (df['Cuartos'] <= rooms[1]) &
        (df['Banos'] >= baths[0]) & (df['Banos'] <= baths[1])
    ]


    st.header(f'Descubir {category} :')
    st.markdown("---")
    show_kpis(df_filtered)

    
    inicio.navegation()
    inicio.flooter()



if __name__ == "__main__":
    descubir_page()
