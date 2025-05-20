import streamlit as st
import Inicio as inicio


def main():
    inicio.page_config()
    inicio.google_analytics()
   
   
    with st.sidebar:
      st.title("Proyecto Gao")
      st.image("assets/logo.png")
    
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
   
    inicio.navegation()
    inicio.flooter()


if __name__ == "__main__":
    main()
