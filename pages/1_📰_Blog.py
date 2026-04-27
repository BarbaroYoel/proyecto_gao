import os
import sys
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import Inicio as inicio

current_directory = os.getcwd()
src_path = os.path.join(current_directory, 'src')
sys.path.append(current_directory)

import src.cleaning_data as cln
import src.analysis as anl

@st.cache_data
def load_all_data() -> pd.DataFrame:
    data_path = os.path.join(current_directory, "data", "processed", "processed.csv")
    raw_df = pd.read_csv(data_path).copy()
    rental_df = cln.cleaning_data_frame_by_category(raw_df, "alquiler", min_outliner=10, max_outliner=1500)
    sale_df = cln.cleaning_data_frame_by_category(raw_df, "venta", min_outliner=1000, max_outliner=1500000)
    return pd.concat([rental_df, sale_df], ignore_index=True)

def load_onei_data():
    onei_path = os.path.join(current_directory, "data", "external", "onei_data.json")
    with open(onei_path) as f:
        return json.load(f)

def display_blog():
    st.title("📰 Blog: Análisis del Mercado Inmobiliario")
    st.markdown("---")
    
    real_estate_df = load_all_data()
    economic_data = load_onei_data()
    
    recent_df = real_estate_df[real_estate_df['Fecha'].dt.year >= 2024]
    sale_df = recent_df[recent_df['Categoria'] == 'venta']
    rental_df = recent_df[recent_df['Categoria'] == 'alquiler']
   
    st.header("🏙️ El Pulso Inmobiliario de La Habana: Radiografía de un Mercado en Tensión")
    st.subheader("Análisis 2024-2025 | Proyecto GAO")
    st.write(f"""
    Bienvenidos al análisis inaugural de **GAO**, la plataforma de datos para el mercado inmobiliario cubano. 
    Navegar el sector de la vivienda en La Habana es enfrentarse a un doble desafío: el sueño de comprar una propiedad 
    o la necesidad de encontrar un alquiler. Ambos caminos están marcados por una profunda incertidumbre 
    y una escasez de información fiable.
    
    La Habana es, sin lugar a dudas, el epicentro inmobiliario de Cuba. Sin embargo, el mercado opera en un entorno 
    de información fragmentada. La misión de este artículo, y de GAO, es iluminar este panorama dual. Para ello, 
    hemos procesado y analizado **{len(real_estate_df):,} anuncios** de portales públicos como Revolico y Porlalivre, 
    correspondientes al período de **enero de 2024 a mayo 2025**, ofreciendo una radiografía clara tanto del mercado 
    de compraventa como del de alquiler.
    """)

    st.header("🌪️ La Tormenta Perfecta: Colapso en la Construcción y Presión Demográfica")
    st.write("""
    La complejidad del mercado habanero se explica por una tensión crítica: una demanda histórica que choca contra una oferta en caída libre. 
    Los datos recientes pintan un cuadro alarmante. La construcción de viviendas en La Habana se ha desplomado de manera drástica en los últimos cinco años.
    """)
    
    st.subheader("📉 Colapso de la Construcción de Viviendas en La Habana (2020-2024)")
    construction_fig = anl.plot_housing_construction(economic_data)
    st.plotly_chart(construction_fig, use_container_width=True)
    
    construction_stats = economic_data["viviendas_terminadas"]
    first_year = construction_stats[0]["año"]
    last_year = construction_stats[-1]["año"]
    first_value = construction_stats[0]["cantidad"]
    last_value = construction_stats[-1]["cantidad"]
    difference = first_value - last_value
    decrease_percentage = ((first_value - last_value) / first_value) * 100
    
    st.info(f"""
    🏗️ **Análisis comparativo ({first_year} vs {last_year}):**  
    - **{first_year}:** {first_value:,d} viviendas construidas  
    - **{last_year}:** {last_value:,d} viviendas construidas  
    - **Reducción:** {difference:,d} viviendas menos (-{decrease_percentage:.0f}%)  
    """)
    
    st.write(f"""
    Esta caída en la construcción se enfrenta a una doble presión demográfica. Por un lado, el déficit habitacional crónico ha llevado 
    a la existencia de miles de "hogares agregados". Por otro lado, la dinámica poblacional de La Habana ha cambiado drásticamente, 
    con un saldo migratorio negativo de **{abs(economic_data['demografia']['saldo_migratorio_2023']):,d} personas** en 2023.
    
    Este éxodo transforma el mercado: muchos que emigran ponen sus propiedades en venta en dólares, 
    inalcanzables para residentes locales con un salario medio de **{economic_data['salario_medio']['valor']:,.0f} {economic_data['salario_medio']['moneda']}**.
    """)

    st.header("📈 La Fiebre de los Precios (Análisis 2024-2025)")
    st.write("""
    Entender el mercado actual requiere mirar su evolución reciente. El análisis de tendencias de **GAO**, enfocado en los anuncios de 2024 y 2025, 
    muestra una clara "fiebre" en los precios de venta y alquileres. Aunque los datos de un período corto deben interpretarse con cautela, se observa una volatilidad 
    significativa mes a mes, con picos que pueden estar influenciados por la entrada al mercado de propiedades de alto valor o la no publicación de anuncios. 
    La tendencia general sugiere que los precios no solo se mantienen altos, sino que son susceptibles a subidas abruptas.
    """)
    
    market_type = st.radio(
        "Seleccione el tipo de mercado:",
        ("Ventas 💰", "Alquileres 🏠"),
        horizontal=True,
        index=0,
        key="market_type_radio"
    )
    
    st.subheader(f"📊 Evolución del Precio Mediano en La Habana (Ene 2024 - May 2025)")
    
    if market_type == "Ventas 💰":
        filtered_df = sale_df
        chart_title = "Evolución del Precio Mediano de Venta"
    else:
        filtered_df = rental_df
        chart_title = "Evolución del Precio Mediano de Alquiler"
    
    if len(filtered_df) > 3:
        price_fig = anl.plot_price_trend(filtered_df)
        price_fig.update_layout(title=chart_title)
        st.plotly_chart(price_fig, use_container_width=True)
        
        last_month = filtered_df['Mes'].max().strftime("%B %Y")
        first_month = filtered_df['Mes'].min().strftime("%B %Y")
        price_change = (
            (filtered_df.groupby('Mes')['Precio'].median().iloc[-1] / 
            filtered_df.groupby('Mes')['Precio'].median().iloc[0] - 1
        ) * 100)
        
        st.info(f"""
        🔍 **Análisis de tendencias ({first_month} → {last_month}):**
        - Cambio porcentual: **{price_change:.1f}%**
        - Precio inicial mediano: **${filtered_df.groupby('Mes')['Precio'].median().iloc[0]:,.0f} USD**
        - Precio final mediano: **${filtered_df.groupby('Mes')['Precio'].median().iloc[-1]:,.0f} USD**
        """)
    else:
        st.warning("⚠️ No hay suficientes datos para mostrar la evolución de precios en esta categoría")

    st.header("🗺️ La Geografía del Precio: Dónde se Compra, Dónde se Alquila")
    st.write("""
    El precio en La Habana está definido por el código postal. Nuestro análisis de los datos de 2024-2025 confirma que los municipios de 
    Playa y Plaza de la Revolución constituyen el clúster de "precio alto", concentrando la mayoría de las ofertas de mayor valor. 
    En contraste, municipios como Cotorro, San Miguel del Padrón y Regla presentan opciones más asequibles, convirtiéndose en el refugio 
    para quienes tienen un presupuesto más limitado.
    """)
    
    st.subheader("🔥 Mapa de Calor de Precios: Venta vs. Alquiler en La Habana")
    
    geojson_path = os.path.join(current_directory, "data", "external", "lha.geojson")
    
    if not os.path.exists(geojson_path):
        st.error(f"Archivo GeoJSON no encontrado en: {geojson_path}")
    else:
        tab_sale, tab_rental = st.tabs(["Ventas 💰", "Alquileres 🏠"])
        
        with tab_sale:
            st.subheader("🏠 Precio Mediano de Venta por Municipio")
            sale_map = anl.plot_habana_map(recent_df, geojson_path, "Ventas")
            st.plotly_chart(sale_map, use_container_width=True)
            
            top_sales = sale_df.groupby("Municipio")["Precio"].median().sort_values(ascending=False)
            st.info(f"""
            🏆 **Municipios más caros para comprar:**
            1. {top_sales.index[0]}: ${top_sales.iloc[0]:,.0f} USD
            2. {top_sales.index[1]}: ${top_sales.iloc[1]:,.0f} USD
            3. {top_sales.index[2]}: ${top_sales.iloc[2]:,.0f} USD
            """)
            st.info(f"""
            💰 **Municipios más baratos para comprar:**
            1. {top_sales.index[-1]}: ${top_sales.iloc[-1]:,.0f} USD
            2. {top_sales.index[-2]}: ${top_sales.iloc[-2]:,.0f} USD
            3. {top_sales.index[-3]}: ${top_sales.iloc[-3]:,.0f} USD
            """)
        
        with tab_rental:
            st.subheader("🏠 Precio Mediano de Alquiler por Municipio")
            rental_map = anl.plot_habana_map(recent_df, geojson_path, "Alquileres")
            st.plotly_chart(rental_map, use_container_width=True)
            
            top_rentals = rental_df.groupby("Municipio")["Precio"].median().sort_values(ascending=False)
            st.info(f"""
            🏆 **Municipios más caros para alquilar:**
            1. {top_rentals.index[0]}: ${top_rentals.iloc[0]:,.0f} USD/mes
            2. {top_rentals.index[1]}: ${top_rentals.iloc[1]:,.0f} USD/mes
            3. {top_rentals.index[2]}: ${top_rentals.iloc[2]:,.0f} USD/mes
            """)
            st.info(f"""
            💰 **Municipios más baratos para alquilar:**
            1. {top_rentals.index[-1]}: ${top_rentals.iloc[-1]:,.0f} USD/mes
            2. {top_rentals.index[-2]}: ${top_rentals.iloc[-2]:,.0f} USD/mes
            3. {top_rentals.index[-3]}: ${top_rentals.iloc[-3]:,.0f} USD/mes
            """)
    
    st.subheader("💼 Análisis Comparativo: ¿Inversión o Necesidad?")
    st.markdown("""
    La relación entre el costo de venta y el de alquiler nos ofrece una de las claves más reveladoras sobre la naturaleza de la inversión en La Habana. 
    La siguiente tabla calcula cuántos años de alquiler se necesitarían para cubrir el precio de compra de una propiedad en el mismo municipio.
    """)
    
    sale_by_municipality = sale_df.groupby("Municipio")["Precio"].median().reset_index().rename(columns={"Precio": "Venta"})
    rental_by_municipality = rental_df.groupby("Municipio")["Precio"].median().reset_index().rename(columns={"Precio": "Alquiler"})
    comparison_df = pd.merge(sale_by_municipality, rental_by_municipality, on="Municipio", how="inner")
    
    if not comparison_df.empty:
        comparison_df["Años_Recuperación"] = comparison_df["Venta"] / (comparison_df["Alquiler"] * 12)
        st.dataframe(
            comparison_df.sort_values("Venta", ascending=False),
            column_config={
                "Municipio": "Municipio",
                "Venta": st.column_config.NumberColumn("Precio Mediano Venta (USD)", format="$%.0f"),
                "Alquiler": st.column_config.NumberColumn("Precio Mediano Alquiler (USD/mes)", format="$%.0f"),
                "Años_Recuperación": st.column_config.NumberColumn("Años de Recuperación", format="%.1f años")
            },
            hide_index=True
        )
        st.info("""
        🔍 **Análisis de la Tabla:**
        Lo que esta tabla expone es una fractura en la lógica del mercado. Con periodos de recuperación que superan los 30 o 40 años, 
        es evidente que el comprador en los segmentos altos no está haciendo un cálculo tradicional de retorno de inversión basado en la renta local. 
        Esto sugiere que la compra de vivienda funciona principalmente como una **reserva de valor** frente a la inflación o una **inversión especulativa a futuro**, 
        en lugar de una inversión para generar ingresos por alquiler.
        """)
    
    st.header("🔍 Anatomía de una Propiedad: ¿Qué Determina el Valor?")
    st.write("""
    Más allá de la ubicación, las características intrínsecas del inmueble son decisivas.
    
    **🏠 El ADN de las Amenidades: De lo Esencial a lo Aspiracional**
    
    Un análisis detallado de las amenidades más comunes revela diferencias significativas según 
    el tipo de propiedad y transacción. Seleccione los filtros para explorar las características 
    más valoradas en cada segmento del mercado.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        transaction_type = st.selectbox(
            "🔁 Tipo de transacción:",
            ["Todas", "venta", "alquiler"],
            index=0
        )
    with col2:
        property_type = st.selectbox(
            "🏢 Tipo de propiedad:",
            ["Todas", "casa", "apartamento"],
            index=0
        )
    
    filtered_features_df = recent_df.copy()
    if transaction_type != "Todas":
        filtered_features_df = filtered_features_df[filtered_features_df['Categoria'] == transaction_type]
    if property_type != "Todas":
        filtered_features_df = filtered_features_df[filtered_features_df['Tipo'] == property_type]
    
    st.subheader("🏆 Top 10 Amenidades")
    amenities_fig = anl.plot_top_amenities_by_filters(filtered_features_df, 10)
    st.plotly_chart(amenities_fig, use_container_width=True)
    
    transaction_label = "Ventas" if transaction_type == "venta" else "Alquileres" if transaction_type == "alquiler" else "Ambas categorías"
    property_label = "Casas" if property_type == "casa" else "Apartamentos" if property_type == "apartamento" else "Todos los tipos"
    
    st.write(f"""
    **🔑 Principales características para {property_label} en {transaction_label}:**
    - 🏷️ **Elementos destacados:** {anl.get_top_amenities_description(filtered_features_df)}
    """)

    st.header("👥 Los Actores del Mercado: Dos Realidades Paralelas")
    st.markdown("""
    Los datos revelan que quienes compran y quienes alquilan a menudo pertenecen a universos económicos distintos. 
    El **💰 Mercado de Venta** está dominado por actores con acceso a capital no generado por un salario local.  
    Esto incluye a personas que deciden emigrar y venden su propiedad para financiarse, cubanos que reciben remesas sustanciales 
    de familiares en el exterior, o inversores que compran, reparan y venden para obtener ganancias. 
    
    Este mercado se materializa en anuncios que antes parecían impensables. No hablamos de un simple apartamento, sino de propiedades descritas como **"Maravillosa residencia de lujo en Miramar"**, valoradas en más de 1.5 millones de dólares, con múltiples habitaciones, piscina y garita de seguridad, tal como documentan estudios previos. 

    El **🏠 Mercado de Alquiler** es más diverso. Incluye a la gran mayoría de cubanos que no pueden acceder a la compra, estudiantes, 
    profesionales trasladados a la capital y, crucialmente, el sector turístico. La alta rentabilidad del alquiler por noches para turistas 
    compite directamente con la oferta de alquiler a largo plazo para residentes, limitando las opciones y elevando los precios.
    """)
    
    st.header("🧭 Navegando la Dualidad con Datos")
    st.markdown("""
    El mercado inmobiliario de La Habana opera en dos velocidades: uno de venta, lento, de alto valor y profundamente dolarizado, 
    movido por capital externo y dinámicas migratorias; y otro de alquiler, rápido, impulsado por la necesidad local y la oportunidad turística. 
    Ambos reflejan y a la vez agudizan la tensión habitacional y la desigualdad económica de la isla.

    En este complejo ecosistema, la misión de **GAO** es ser una brújula imparcial. En un mercado definido por la opacidad, proporcionar datos limpios, 
    análisis rigurosos y herramientas visuales es ofrecer poder. El poder de entender, comparar y, en última instancia, tomar decisiones estratégicas 
    e informadas, sin importar de qué lado del mercado te encuentres.
    """)
    
    st.warning("""
        ⚠️ **Importante:** Este proyecto es una herramienta de análisis y no debe ser considerado como asesoramiento legal o financiero. 
        Los datos son proporcionados con fines informativos y pueden no reflejar la realidad del mercado inmobiliario.
        Proyecto GAO no se hace responsable por decisiones tomadas en base a esta información. 
        Cualquier acción relacionada con el mercado inmobiliario es bajo su propia responsabilidad.
    """)
    st.markdown("---")  

    st.markdown("""
    **📚 Fuentes de datos:**
    - Anuncios inmobiliarios de portales públicos (2024-2025)
    - [Oficina Nacional de Estadística e Información](https://www.onei.gob.cu/)
    - Elaboración propia de Proyecto GAO
    """)


def blog_page():
    inicio.page_config()
    inicio.sidebar_config()
    display_blog()
    inicio.navegation()
    inicio.flooter()
    
    
if __name__ == "__main__":
    blog_page()