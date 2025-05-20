import streamlit as st
import Inicio as inicio

def main():
    inicio.page_config()
    inicio.google_analytics()
    inicio.sidebar_config()
    
    
    st.title("Blog: Análisis del Mercado Inmobiliario 📰")
    st.markdown("---")
    
    st.header("🔍 Próximamente: Un Viaje por el Mercado Inmobiliario de La Habana")

    st.info(
        """
        ¡Estamos trabajando arduamente para traerte esta sección!

        Aquí encontrarás un **análisis narrativo y visual profundo del mercado inmobiliario
        de La Habana**, inspirado en estudios detallados y con el objetivo de
        ofrecerte una comprensión clara de sus datos.
        """
    )


    st.markdown("### ¿Qué podrás descubrir en esta sección una vez esté lista?")
    st.markdown(
        """
        El objetivo de esta página es transformar datos complejos en una historia comprensible
        y útil. A través de un enfoque de *storytelling*:

        * **📊 Presentar Tendencias Evolutivas:** Te mostraremos cómo ha cambiado el mercado a lo largo del tiempo, identificando patrones clave en precios, oferta y demanda.
        * **🏘️ Comparar Zonas y Propiedades:** Analizaremos las diferencias significativas entre los diversos municipios y tipos de propiedades, ayudándote a entender el valor y las oportunidades en cada área.
        * **🌍 Contextualizar los Datos:** Iremos más allá de los números, explicando los factores socioeconómicos y demográficos que influyen en la dinámica inmobiliaria de La Habana.
        * **📈 Visualizaciones Interactivas:** Utilizaremos gráficos, mapas y tablas para que puedas explorar los datos de manera intuitiva y personalizada.

        Nuestro fin es que, tanto si eres comprador, vendedor, inversor o simplemente un entusiasta del mercado, puedas tomar decisiones más informadas y estratégicas.
        """
    )

    st.warning(
        """
        🚧 **Actualmente, estamos en la fase de recopilación y procesamiento de los datos necesarios**
        para construir las visualizaciones y análisis que darán vida a esta sección.

        Agradecemos tu paciencia y te invitamos a explorar las otras secciones de **Proyecto Gao**
        mientras completamos este emocionante desarrollo.
        """
    )

    inicio.navegation()
    inicio.flooter()
    
    
if __name__ == "__main__":
    main()