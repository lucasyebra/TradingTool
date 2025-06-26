import streamlit as st
from app_logica import run_app

# Carga de estilos CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&family=Comic+Neue&display=swap');

html, body, [class*="css"] {
    font-family: 'Quicksand', sans-serif;
    background-color: #fffaf2;
    color: #333;
}

h1, h2, h3 {
    font-family: 'Comic Neue', cursive;
}

.title-box {
    background-color: #fff3e0;
    color: #f4a261;
    font-size: 42px;
    font-weight: bold;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 2px 2px 5px rgba(244, 162, 97, 0.3);
    margin-bottom: 2rem;
}

.highlight-box {
    background-color: #fff3e0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 2px 2px 5px rgba(244, 162, 97, 0.3);
}

.footer {
    text-align: center;
    font-size: 13px;
    color: #999;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# 🟠 Título principal
st.markdown('<div class="title-box">📊 Trading Tool</div>', unsafe_allow_html=True)

# 🧠 Ejecución del contenido principal (sin contenedor externo vacío)
run_app()

# 🔵 Footer
st.markdown('<div class="footer">Made by Lucas Rodriguez Yebra</div>', unsafe_allow_html=True)
