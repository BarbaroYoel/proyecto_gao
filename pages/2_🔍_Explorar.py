import os 
import sys
import Inicio as inicio
import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
import plotly.express as px
import json
from collections import Counter
from plotly.subplots import make_subplots
import plotly.graph_objects as go 
import unicodedata

parent_directory=os.getcwd()
print(parent_directory)
path=os.path.join(parent_directory,'src')
print(path)
sys.path.append(parent_directory)

import src.cleaning_data as cln
import src.analysis as anl


@st.cache_data
def load_all_data()-> pd.DataFrame:
    path=os.getcwd()
    data_file=os.path.join(path,"data","processed","processed.csv")
    df=pd.read_csv(data_file).copy()
    
    df_rent= cln.cleaning_data_frame_by_category(df,"alquiler",min_outliner=10,max_outliner=1500)
    df_sale = cln.cleaning_data_frame_by_category(df,"venta",min_outliner=1000,max_outliner=1500000)
    return pd.concat([df_rent,df_sale],ignore_index=True)

def load_data(category:str)-> pd.DataFrame :
    path =os.getcwd()
    data_file=os.path.join(path,"data","processed","processed.csv")
    df=pd.read_csv(data_file).copy()
    
    if category=="Alquileres":
      df= cln.cleaning_data_frame_by_category(df,"alquiler",min_outliner=10,max_outliner=1500)

    elif category=="Ventas" :
      df = cln.cleaning_data_frame_by_category(df,"venta",min_outliner=1000,max_outliner=1500000)
    return df


def show_general_kpis(df:pd.DataFrame)->None:
    total_properties=len(df)
    
    number_of_houses=len(df[df["Tipo"]=="casa"])
    number_of_apartments=len(df[df["Tipo"]=="apartamento"])    
    
    municipal_count =df["Municipio"].value_counts()
    municipal_top=municipal_count.idxmax()
 
    df_rent=df[df["Categoria"]=="alquiler"]
    df_sale=df[df["Categoria"]=="venta"]
    
    price_rent_mean=df_rent["Precio"].mean()
    price_rent_median=df_rent["Precio"].median()
    price_sale_mean=df_sale["Precio"].mean()
    price_sale_median=df_sale["Precio"].median()
    
    st.subheader("🔑 KPIs Generales del Mercado")
    
    col1,col2,col3,col4=st.columns(4)
    col1.metric("🔐 Total de Propiedades",total_properties)
    col2.metric("🏡 Total de Casas",number_of_houses)
    col3.metric("🏢 Total de Apartamentos",number_of_apartments)
    col4.metric("📍 Municipio con más Propiedades",municipal_top)
    
    col1,col2,col3,col4=st.columns(4)
    col1.metric("💰 Precio Promedio Alquiler",f"${price_rent_mean:,.0f} USD")
    col2.metric("💵 Precio Mediano Alquiler",f"${price_rent_median:,.0f} USD")
    col3.metric("💰 Precio Promedio Venta",f"${price_sale_mean:,.0f} USD")
    col4.metric("💵 Precio Mediano Venta",f"${price_sale_median:,.0f} USD")

    st.markdown("---")


def show_general_charts(df: pd.DataFrame) -> None:
    st.subheader("📊 Visualizaciones Generales del Mercado")
    
    col1, col2 = st.columns(2)
    with col1:
        fig1 = anl.plot_properties_by_municipality(df, top_n=10)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = anl.plot_category_distribution(df)
        st.plotly_chart(fig2, use_container_width=True)
   
    col3, col4 = st.columns(2)
    with col3:
        fig3 = anl.plot_property_type_distribution(df)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
    with col4:
        fig4 = anl.plot_amenities_by_property_type(df, top_n=10)
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")


def show_kpis(df:pd.DataFrame)->None:
    
    total_properties = len(df)
    
    number_of_houses=len(df[df["Tipo"]=="casa"])
    number_of_apartments=len(df[df["Tipo"]=="apartamento"])  
   
    mean_price = df["Precio"].mean()
    median_price = df["Precio"].median()
   
    mean_rooms = df["Cuartos"].mean()
    mean_baths = df["Banos"].mean()
    
    garage_pct = (df["Garaje"].sum() / total_properties * 100)
            
    amenities = df["Amenidades"].fillna("").astype(str).str.lower()
    has_phone = amenities.str.contains("telefono fijo|teléfono fijo")
    phone_pct = (has_phone.sum() / total_properties * 100)  
   


    st.subheader("🔑 KPIs Específicos de las Propiedades Seleccionadas")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🔍 Propiedades Seleccionadas", total_properties)
    col2.metric("🏡 Casas", number_of_houses)
    col3.metric("🏢 Apartamentos", number_of_apartments)

    col4, col5, col6 = st.columns(3)
    col4.metric("💰 Precio Promedio", f"${mean_price:,.0f} USD")
    col5.metric("💵 Precio Mediano", f"${median_price:,.0f} USD")
    col6.metric("🚪 Cuartos Promedio", f"{mean_rooms:.0f}")

    col7, col8, col9 = st.columns(3)
    col7.metric("🚿 Baños Promedio", f"{mean_baths:.0f}")
    col8.metric("🚗 Con Garaje", f"{garage_pct:.0f}%")
    col9.metric("📞 Con Teléfono Fijo", f"{phone_pct:.1f}%")
    
    st.markdown("---")
    
def show_specific_charts(df: pd.DataFrame,df_grafica:pd.DataFrame) -> None:
    st.subheader("📈 Visualizaciones Específicas de los Datos Filtrados")
    
    
        
        
    if not df.empty:
        fig1 = anl.plot_price_by_municipality(df)
        st.plotly_chart(fig1, use_container_width=True)
    
    if not df.empty and 'Fecha' in df:
        fig2 = anl.plot_price_trend_by_property_type(df)
        st.plotly_chart(fig2, use_container_width=True)

    if not df.empty and 'Fecha' in df:
        fig4 = anl.plot_price_trend(df)
        st.plotly_chart(fig4, use_container_width=True)
    
    if not df.empty and 'Amenidades' in df:
        fig_amenities = anl.plot_amenities_distribution(df, top_n=10)
        if fig_amenities:
            st.plotly_chart(fig_amenities, use_container_width=True)




def descubir_page():
    inicio.page_config()
   
    with st.sidebar:
      st.title("Proyecto Gao")
      st.image("assets/logo.png")
      st.sidebar.title('Filtros de Búsqueda')
      category = st.radio("Seleccione la categoría:",["Alquileres","Ventas"])
      
      df = load_data(category)
      year_range = st.slider("Rango de Años:",2022,2025,(2022,2025))
     
      df_prueba=load_all_data()
      municipality = df['Municipio'].dropna().unique().tolist()
      seleccion_mun =st.multiselect("Municipios",municipality,default= ["Centro Habana","La Habana Vieja","Plaza de la Revolución","Cerro","Playa"])
      selc_municipality_grafica = st.radio("Seleccione Municipio:",municipality)
      
      
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
        (df['Banos'] >= baths[0]) & (df['Banos'] <= baths[1])& 
        ((df['Fecha'].dt.year >= year_range[0]) & 
        (df['Fecha'].dt.year <= year_range[1]))
    ]
    
    df_grafica =df_prueba[(df_prueba["Municipio"]==selc_municipality_grafica)& 
        ((df_prueba['Fecha'].dt.year >= year_range[0]) & 
        (df_prueba['Fecha'].dt.year <= year_range[1]))]
   
    # st.dataframe(df_grafica)
    # fig=anl.grafica(df_grafica)
    # st.plotly_chart(fig,use_container_width=True)  
   
    # data=anl.grafica(df_grafica)
    # st.dataframe(data) 
    
    
    st.header("Explorar: Visión del Mercado Inmobiliario 🔍")
    st.markdown("---")

    
    df_all=load_all_data()
    show_general_kpis(df_all)
    show_general_charts(df_all)
    
    st.header(f'Datos filtrados de {category} :')
    st.markdown("---")
    st.markdown(f"""
    - **Municipios:** {', '.join(seleccion_mun) if seleccion_mun else 'Todos'}
    - **Precio:** ${range_price[0]:,.0f} - ${range_price[1]:,.0f} USD
    - **Habitaciones:** {rooms[0]} - {rooms[1]}
    - **Baños:** {baths[0]} - {baths[1]}
    """)
    st.markdown("---")
    
    show_kpis(df_filtered)
    
    show_specific_charts(df_filtered,df_grafica)    

    

    st.warning("""
        ⚠️ Este proyecto es una herramienta de análisis y no debe ser considerado como asesoramiento legal o financiero. 
        Los datos son proporcionados con fines informativos y pueden no reflejar la realidad del mercado inmobiliario.
        Proyecto GAO no se hace responsable por decisiones tomadas en base a esta información. 
        Cualquier acción relacionada con el mercado inmobiliario es bajo su propia responsabilidad
    """)
    st.markdown("---")  
    
    inicio.navegation()
    inicio.flooter()


if __name__ == "__main__":
    descubir_page()
