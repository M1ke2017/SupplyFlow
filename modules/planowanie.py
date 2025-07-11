import streamlit as st
import pandas as pd

def panel_planowanie(conn, username):
    st.header("Panel Planowania")
    
    cur = conn.cursor()

    st.subheader("Magazyn")
    cur.execute("SELECT component, quantity FROM warehouse")
    warehouse_data = cur.fetchall()
    df_warehouse = pd.DataFrame(warehouse_data, columns=["Komponent", "Ilość"])
    st.dataframe(df_warehouse)


    with st.form("form_plan"):
        component = st.text_input("Nazwa komponentu")
        quantity = st.number_input("Ilość", min_value=1)
        needed_by = st.date_input("Potrzebne do", value=pd.Timestamp.now().date() + pd.Timedelta(days=7))
        submitted = st.form_submit_button("Zgłoś zapotrzebowanie")

        if submitted:
            if not component.strip():
                st.warning("Uzupełnij nazwę komponentu.")
            elif needed_by < pd.Timestamp.now().date():
                st.warning("Data potrzebna nie może być w przeszłości.")
            else:
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                result = cur.fetchone()
                if not result:
                    st.error("Nie znaleziono użytkownika w bazie.")
                    return
                user_id = result[0]

                cur.execute(
                    """
                    INSERT INTO requests (component, quantity, needed_by, status, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (component, quantity, needed_by, "Oczekujące", user_id)
                )
                conn.commit()
                st.success("Zapotrzebowanie zostało zapisane.")

        