import streamlit as st
import Inicio as inicio


def display_social_media():
    st.title("Redes Sociales: Mantente Conectado 📱")
    st.markdown("---") 
    st.header("Redes Sociales")
    
    col1, col2 = st.columns(2)
    with col1:
      st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/132px-Instagram_logo_2016.svg.png", width=50)
      st.markdown("[Instagram](https://www.instagram.com/proyectogao)")
   
    with col2:
      st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/YouTube_Logo_2017.svg/1200px-YouTube_Logo_2017.svg.png" , width=140)
      st.markdown("[YouTube](https://www.youtube.com/@ProyectoGAO)")

    st.header("Contactos")
    st.write( "📧 gao.cuba2025@gmail.com")


def social_media_page():
    inicio.page_config()
    inicio.sidebar_config()
    display_social_media()
    
    
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
    social_media_page() 