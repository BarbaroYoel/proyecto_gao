import streamlit as st


def main():
    st.set_page_config(
        page_title="Proyecto Gao",
        layout="wide",
        page_icon="assets/gao_icon.ico")

    with st.sidebar:
      st.title("Proyecto Gao")
      st.image("assets/logo.png")
      
     
     
     
    st.title("Redes Sociales: Mantente Conectado 📱")
    st.markdown("---") 
      
    st.header("Redes Sociales")
    
    col1, col2, col3 = st.columns(3)

    with col1:
      st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/132px-Instagram_logo_2016.svg.png", width=50)
      st.markdown("[Instagram](https://www.instagram.com/proyectogao)")
      
    with col2:
      st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Facebook_Logo_%282019%29.png/150px-Facebook_Logo_%282019%29.png", width=50)
      st.markdown("[Facebook](https://facebook.com/proyecto_gao)")

      
    with col3:
      st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/YouTube_Logo_2017.svg/1200px-YouTube_Logo_2017.svg.png" , width=140)
      st.markdown("[YouTube](https://www.youtube.com/@ProyectoGAO)")

    st.header("Contactos")
    st.write( "📧 gao.cuba2025@gmail.com")
    
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        ### 🚀 Comienza a Explorar
        
        Utiliza la barra de navegación a la izquierda para:
        - 📰 Leer nuestro Blog con análisis detallados 
        - 🔍 Explorar el Dashboard interactivo
        """)
        
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>Desarrollado con ❤️ por el equipo de Proyecto Gao</p>
        <p>© 2025 Proyecto Gao - Todos los derechos reservados</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 