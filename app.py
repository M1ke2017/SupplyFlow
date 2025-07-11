import streamlit as st
from modules.auth import login_user
from modules.planowanie import panel_planowanie
from modules.ksiegowosc import panel_ksiegowosc
from modules.dostawy import panel_dostawy
from modules.db import get_connection
from modules.analityka import panel_analityczny


st.set_page_config(page_title="SupplyFlow", layout="centered")
st.title("SupplyFlow")

conn = get_connection()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Logowanie")
    username = st.text_input("Login")
    password = st.text_input("Hasło", type="password")
    if st.button("Zaloguj"):
        role = login_user(username, password, conn)
        if role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Nieprawidłowy login lub hasło")
else:
    st.success(f"Zalogowano jako: {st.session_state.username} ({st.session_state.role})")
    if st.button("Wyloguj"):
        st.session_state.logged_in = False
        st.rerun()

    role = st.session_state.role
    if role == 'planning':
        panel_planowanie(conn, st.session_state.username)
    elif role == 'accounting':
        panel_ksiegowosc(conn, st.session_state.username)
    elif role == 'logistics':
        panel_dostawy(conn, st.session_state.username)
    elif role == 'analityka':
        panel_analityczny(conn)
    else:
        st.warning("Nieznana rola użytkownika.")
