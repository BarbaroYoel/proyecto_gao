import streamlit as st
from streamlit.components.v1 import html

# 1. CONFIGURACIÓN DE PÁGINA - DEBE SER ABSOLUTAMENTE PRIMERO
st.set_page_config(
    page_title="Proyecto Gao",
    layout="wide",
    page_icon="assets/gao_icon.ico",
)

# 2. GOOGLE ANALYTICS - Inmediatamente después
GA_ID = "G-TTV23M3QPB"
ga_script = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
"""
html(ga_script, width=0, height=0)

# 3. ELIMINA LA FUNCIÓN page_config() COMPLETAMENTE
# (ya no es necesaria porque la configuración está arriba)

def sidebar_config():
    with st.sidebar:
        st.title("Proyecto Gao")
        st.image("assets/logo.png")

def navegation():
    st.markdown("---")
    st.markdown(
    """
    <div style='text-align: center;'>
        <p>🚀 Comienza a Explorar</p>
        <p>Utiliza la barra de navegación a la izquierda para:</p>
        <p>- 📰 Leer nuestro Blog con análisis detallados</p>
        <p>- 🔍 Explorar el Dashboard interactivo</p>
        <p>- 📱 Contactarnos y seguirnos en redes sociales</p>
    </div>
    """,
    unsafe_allow_html=True
)

def flooter():
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center'>
        <p>Desarrollado con ❤️ por el equipo de Proyecto Gao</p>
        <p>© 2025 Proyecto Gao - Todos los derechos reservados</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

def display_inicio():
    st.title("Bienvenido a Proyecto Gao 🏘️")
    st.markdown("---")

    st.markdown(
        """
       ## 🎯 Nuestro Objetivo
       
       Proyecto Gao es una herramienta de análisis del mercado inmobiliario en La Habana que te permite:
       
       - 📊 Explorar tendencias de precios por municipio
       - 🏠 Analizar diferentes tipos de propiedades
       - 🔍 Descubrir oportunidades en el mercado
       - 📈 Visualizar datos históricos y actuales
       """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
        ### 📱 Fácil de Usar
        Interfaz intuitiva y amigable para explorar el mercado inmobiliario
        """
        )
    with col2:
        st.markdown(
            """
        ### 🔄 Datos Actualizados
        Información actualizada regularmente del mercado inmobiliario
        """
        )
    with col3:
        st.markdown(
            """
        ### 📊 Análisis Detallado
        Visualizaciones y estadísticas comprehensivas
        """
        )
    st.markdown("---")

    st.markdown(
        """
    ## 🤷‍♂️ ¿Quiénes Somos? 🤷‍♀️
    
    Somos un equipo de estudiantes de Ciencia de Datos de MATCOM comprometidos con:
    
    - 🎯 Proporcionar transparencia al mercado inmobiliario
    - 📊 Facilitar el análisis de datos para toma de decisiones
    - 💡 Innovar en la visualización de datos inmobiliarios
    """
    )
    
# 4. MODIFICA inicio_page() PARA ELIMINAR page_config()
def inicio_page():
    # Esta línea ha sido eliminada: page_config()
    sidebar_config()
    display_inicio()
    navegation()
    flooter()

# 5. EL CÓDIGO DE GOOGLE ANALYTICS SE HA MOVIDO ARRIBA

if __name__ == "__main__":
    inicio_page()