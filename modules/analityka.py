import streamlit as st
import pandas as pd
import plotly.express as px
from modules.pdf_generator import generate_analytics_report

def panel_analityczny(conn):
    st.title("Panel Analityka")
    cur = conn.cursor()

    
    st.subheader("Wydatki wg komponentów")
    cur.execute("""
        SELECT r.component, SUM(r.quantity * p.average_price) as total_cost
        FROM requests r
        JOIN prices p ON r.component = p.component
        GROUP BY r.component
    """)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["Komponent", "Koszt"])
    st.dataframe(df)
    st.plotly_chart(px.pie(df, names="Komponent", values="Koszt", title="Udział komponentów w kosztach"))

    
    st.subheader("Wydatki miesięczne")
    cur.execute("""
        SELECT DATE_TRUNC('month', o.approved_on) AS miesiac, 
               SUM(r.quantity * p.average_price) as koszt
        FROM orders o
        JOIN requests r ON o.request_id = r.id
        JOIN prices p ON r.component = p.component
        WHERE o.delivery_status = 'Dostarczone'
        GROUP BY miesiac
        ORDER BY miesiac
    """)
    months = cur.fetchall()
    df_month = pd.DataFrame(months, columns=["Miesiąc", "Koszt"])
    st.line_chart(df_month.set_index("Miesiąc"))

    
    st.subheader("Stan magazynowy")
    cur.execute("SELECT component, quantity FROM warehouse")
    df_stock = pd.DataFrame(cur.fetchall(), columns=["Komponent", "Stan"])
    st.dataframe(df_stock)

    
    st.subheader("Historia zdarzeń")
    cur.execute("""
    SELECT l.timestamp, u.username, l.action
    FROM logs l
    JOIN users u ON l.user_id = u.id
    ORDER BY l.timestamp DESC
    LIMIT 50
""")
    df_logs = pd.DataFrame(cur.fetchall(), columns=["Czas", "Użytkownik", "Akcja"])
    st.dataframe(df_logs)
    
    st.subheader("Eksport danych do CSV")
    cur.execute("""
        SELECT r.id, r.component, r.quantity, p.average_price, r.quantity * p.average_price AS koszt, o.approved_on, o.delivery_status
        FROM requests r
        JOIN orders o ON o.request_id = r.id
        JOIN prices p ON r.component = p.component
    """)
    export = cur.fetchall()
    df_export = pd.DataFrame(export, columns=["ID", "Komponent", "Ilość", "Cena", "Koszt", "Zatwierdzono", "Status"])
    st.download_button("Pobierz dane jako CSV", df_export.to_csv(index=False), "raport.csv")

    
    st.subheader("Raport zbiorczy PDF")
    if st.button("Wygeneruj raport PDF"):
        pdf_bytes = generate_analytics_report(df, df_month, df_stock)
        st.download_button("Pobierz PDF", data=pdf_bytes, file_name="raport_analityczny.pdf", mime="application/pdf")
