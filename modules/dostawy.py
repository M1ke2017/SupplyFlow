import streamlit as st
import pandas as pd
from modules.pdf_generator import generate_delivery_report
from io import BytesIO
import base64

def panel_dostawy(conn, username):
    st.header("Panel Dostaw")

    cur = conn.cursor()

    st.subheader("Magazyn")
    cur.execute("SELECT component, quantity FROM warehouse")
    warehouse_data = cur.fetchall()
    df_warehouse = pd.DataFrame(warehouse_data, columns=["Komponent", "Ilość"])
    st.dataframe(df_warehouse)

    
    st.subheader("Zamówienia do realizacji")
    cur.execute("""
        SELECT r.id, r.component, r.quantity, r.needed_by, u.username
        FROM requests r
        JOIN orders o ON o.request_id = r.id
        JOIN users u ON r.created_by = u.id
        WHERE o.delivery_status = 'W przygotowaniu'
    """)
    orders = cur.fetchall()
    if not orders:
        st.info("Brak zamówień do realizacji.")
        return

    df_orders = pd.DataFrame(orders, columns=["ID", "Komponent", "Ilość", "Potrzebne do", "Użytkownik"])
    selected_id = st.selectbox("Wybierz ID zamówienia do realizacji:", df_orders["ID"])
    selected_row = df_orders[df_orders["ID"] == selected_id].iloc[0]

   
    if st.button("Zrealizuj zamówienie"):
        quantity = int(selected_row["Ilość"])
        component = str(selected_row["Komponent"])

        cur.execute("""
                UPDATE warehouse
                SET quantity = quantity - %s
                WHERE component = %s
            """, (quantity, component))

        cur.execute("""
                UPDATE orders
                SET delivery_status = 'Dostarczone'
                WHERE request_id = %s
            """, (selected_id,))

        conn.commit()
        st.success("Zamówienie zostało zrealizowane.")

        
        st.subheader("Generowanie raportu dostawy")
        file = generate_delivery_report(
                selected_id,
                component,
                quantity,
                selected_row["Potrzebne do"]
            )
        st.download_button(
                label="Pobierz raport PDF dostawy",
                data=file,
                file_name=f"dostawa_{selected_id}.pdf",
                mime="application/pdf"
            )


