import streamlit as st


def main():
    st.set_page_config(
        page_title="Proyecto Gao",
        layout="wide",
        page_icon="assets/gao_icon.ico")
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
    st.markdown("---")
    # Footer y navegación
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        ### 🚀 Comienza a Explorar
        
        Utiliza la barra de navegación a la izquierda para:
        - 📰 Leer nuestro Blog con análisis detallados 
        - 📱 Contactarnos y seguirnos en redes sociales
        """)

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

if __name__ == "__main__":
    main()
