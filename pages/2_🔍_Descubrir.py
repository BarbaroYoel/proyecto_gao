import streamlit as st
import Inicio as inicio
import pandas as pd
import plotly.express as px
import os 
import sys


parent_directory=os.getcwd()
print(parent_directory)
path=os.path.join(parent_directory,'src')
print(path)
sys.path.append(parent_directory)
import src.cleaning_data as cln



@st.cache_data
def display_descubrir():
    
    st.title("Descubrir: Dashboard Inmobiliario 📊")
    st.markdown("---")
    st.info(
        """
        ¡Estamos trabajando arduamente para traerte esta sección!

        Aquí encontrarás un **análisis narrativo y visual profundo del mercado inmobiliario
        de La Habana**, inspirado en estudios detallados y con el objetivo de
        ofrecerte una comprensión clara de sus datos.
        """
    )


# implentar 
def load_data(category:str)-> pd.DataFrame :
    path =os.getcwd()
    data_file=os.path.join(path,"data","processed","processed.csv")
    df=pd.read_csv(data_file).copy()
    
    if category=="Alquileres":
      df= cln.cleaning_data_frame_by_category(df,"alquiler",min_outliner=10,max_outliner=1000)

    elif category=="Ventas" :
      df = cln.cleaning_data_frame_by_category(df,"venta",min_outliner=1000,max_outliner=1000000)
    
    return df


def show_kpis(df:pd.DataFrame)->pd.DataFrame :
    mean_price=df["Precio"].mean()
    median_price=df["Precio"].median()
    max_price=df["Precio"].max()
   
    col1,col2,col3=st.columns(3)
   
    col1.metric("Precio medio",f"{mean_price:,.0f} USD")
    col2.metric("Precio mediano",f"{median_price:,.0f} USD")
    col3.metric("Precio máximo",f"{max_price} USD")



def descubir_page():
    inicio.page_config()

    with st.sidebar:
    #   st.title("Proyecto Gao")
    #   st.image("assets/logo.png")
      st.sidebar.title('Filtros de Búsqueda')
   
      category = st.radio("Seleccione la categoría:",["Alquileres","Ventas"])
      df = load_data(category)
      
    #   
      municipality = df['Municipio'].dropna().unique().tolist()
      seleccion_mun =st.multiselect("Municipios",municipality,default= municipality)
    #  
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
  
    st.header(f'Análisis de {category}')
    show_kpis(df_filtered)
    # display_descubrir()
    inicio.navegation()
    inicio.flooter()


if __name__ == "__main__":
    descubir_page()
