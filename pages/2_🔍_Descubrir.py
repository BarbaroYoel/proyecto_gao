import streamlit as st
import Inicio as inicio


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

def descubir_page():
    inicio.page_config()

    with st.sidebar:
      st.title("Proyecto Gao")
      st.image("assets/logo.png")

    display_descubrir()
    inicio.navegation()
    inicio.flooter()


if __name__ == "__main__":
    descubir_page()
