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
    col1.metric("💰 Precio Medio Alquiler",f"${price_rent_mean:,.0f} USD")
    col2.metric("💵 Precio Mediano Alquiler",f"${price_rent_median:,.0f} USD")
    col3.metric("💰 Precio Medio Venta",f"${price_sale_mean:,.0f} USD")
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

def show_specific_charts(df: pd.DataFrame) -> None:
    st.subheader("📈 Visualizaciones Específicas de los Datos Filtrados")
    
    if not df.empty:
        st.markdown("### Precio Promedio y Mediano por Municipio")
        fig1 = anl.plot_price_by_municipality(df)
        st.plotly_chart(fig1, use_container_width=True)
    
    if not df.empty and 'Fecha' in df:
        st.markdown("### Evolución de Precios por Tipo de Propiedad")
        fig2 = anl.plot_price_trend_by_property_type(df)
        st.plotly_chart(fig2, use_container_width=True)

    
    if not df.empty and 'Fecha' in df:
        st.markdown("### Evolución de Precio Promedio (Filtrado)")
        fig4 = anl.plot_price_trend(df)
        st.plotly_chart(fig4, use_container_width=True)
   

def descubir_page():
    inicio.page_config()
   
    with st.sidebar:
      st.title("Proyecto Gao")
      st.image("assets/logo.png")
      st.sidebar.title('Filtros de Búsqueda')
      category = st.radio("Seleccione la categoría:",["Alquileres","Ventas"])

      df = load_data(category)
      
      municipality = df['Municipio'].dropna().unique().tolist()
      seleccion_mun =st.multiselect("Municipios",municipality,default= ["Centro Habana","La Habana Vieja","Plaza de la Revolución","Cerro","Playa"])
       
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

    st.header("Explorar: Visión del Mercado Inmobiliario 🔍")
    st.markdown("---")
    
    df_all=load_all_data()
    show_general_kpis(df_all)
    show_general_charts(df_all)
    
    st.header(f'Datos filtrados de {category} :')
    st.markdown("---")
    show_kpis(df_filtered)
    show_specific_charts(df_filtered)    

    inicio.navegation()
    inicio.flooter()


if __name__ == "__main__":
    descubir_page()
