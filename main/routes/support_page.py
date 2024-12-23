import streamlit as st


def page_support():
    """Pagina dedicada ao suporte ao usuario"""
    x, y = st.columns([2, 1], gap="large", vertical_alignment="center")
    x.title("Bem vindo a pagina de support")
    feedback = x.text_area("Por favor descreva o ocorrido!!:", max_chars=500)
    y.write("Criador e support da pagina: @__little_renan.py")

    # Adicione botão de voltar
    if st.button("Voltar"):
        st.session_state["pagina"] = "homepage"
        st.rerun()
    st.html("<foot>@renanrodrigues.dev</foot>")
