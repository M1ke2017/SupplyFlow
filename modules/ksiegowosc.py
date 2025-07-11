import streamlit as st
import pandas as pd
from datetime import datetime
from modules.pdf_generator  import generate_budget_report

def panel_ksiegowosc(conn, username):
    st.header("Panel Księgowości")
    cur = conn.cursor()

    
    st.subheader("Budżet")
    cur.execute("SELECT total FROM budget LIMIT 1")
    budget_row = cur.fetchone()
    budget = budget_row[0] if budget_row else 0
    st.info(f"Pozostały budżet: {budget:,.2f} zł")


    st.subheader("Magazyn")
    cur.execute("SELECT component, quantity FROM warehouse")
    warehouse_data = cur.fetchall()
    df_warehouse = pd.DataFrame(warehouse_data, columns=["Komponent", "Ilość"])
    st.dataframe(df_warehouse)
    
    st.subheader("Oczekujące Zapotrzebowania")
    cur.execute("SELECT * FROM requests WHERE status = 'Oczekujące'")
    requests = cur.fetchall()

    if requests:
        df = pd.DataFrame(requests, columns=["id", "component", "quantity", "needed_by", "status", "created_by"])
        selected = st.selectbox("Wybierz ID do zatwierdzenia/odrzucenia:", df["id"])

        req_row = df[df["id"] == selected].iloc[0]
        component = req_row["component"]
        quantity = req_row["quantity"]

        with st.expander("Decyzja dla zapotrzebowania"):
            reason = st.text_input("Powód odrzucenia (opcjonalnie)")

            if st.button("Odrzuć zapotrzebowanie"):
                cur.execute("""
                    UPDATE requests SET status = 'Odrzucone' WHERE id = %s
                """, (selected,))
                conn.commit()
                st.warning(f"Zapotrzebowanie #{selected} zostało odrzucone.")

            
            cur.execute("SELECT average_price FROM prices WHERE component = %s", (component,))
            price_row = cur.fetchone()
            if not price_row:
                st.error("Brak informacji o cenie rynkowej dla tego komponentu.")
                return

            price = price_row[0]
            total_cost = price * quantity

            
            cur.execute("SELECT quantity FROM warehouse WHERE component = %s", (component,))
            warehouse_row = cur.fetchone()
            warehouse_qty = warehouse_row[0] if warehouse_row else 0

            if warehouse_qty + quantity > 500:
                st.error("Dostawa przekroczyłaby maksymalną pojemność magazynu (500 szt.).")
                return

            if total_cost > budget:
                st.error("Brak wystarczających środków w budżecie.")
                return

            if st.button("Zatwierdź zapotrzebowanie"):
                now = datetime.now()

                
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                approved_by = cur.fetchone()[0]

                
                cur.execute("UPDATE requests SET status = 'Zatwierdzone' WHERE id = %s", (selected,))

                
                cur.execute("""
                    INSERT INTO orders (request_id, approved_by, approved_on, delivery_status)
                    VALUES (%s, %s, %s, %s)
                """, (selected, approved_by, now, "W przygotowaniu"))

               
                cur.execute("UPDATE budget SET total = total - %s", (total_cost,))

                conn.commit()
                st.success(f"Zatwierdzono zapotrzebowanie #{selected}. Koszt: {total_cost:.2f} zł")

        st.dataframe(df)
    else:
        st.info("Brak oczekujących zapotrzebowań.")

   
    st.subheader("Historia Zatwierdzeń i Wydatków")
    cur.execute("""
        SELECT r.id, r.component, r.quantity, p.average_price, o.approved_on
        FROM requests r
        JOIN orders o ON r.id = o.request_id
        JOIN prices p ON r.component = p.component
        WHERE r.status = 'Zatwierdzone'
        ORDER BY o.approved_on DESC
    """)
    history = cur.fetchall()
    if history:
        hist_df = pd.DataFrame(history, columns=["ID", "Komponent", "Ilość", "Cena/szt.", "Zatwierdzono"])
        hist_df["Koszt"] = hist_df["Ilość"] * hist_df["Cena/szt."]
        st.dataframe(hist_df)
    else:
        st.info("Brak zatwierdzonych zapotrzebowań.")

    if 'hist_df' in locals():
        remaining_budget = budget  
    if st.button("Wygeneruj raport PDF budżetu"):
        pdf_bytes = generate_budget_report(hist_df, remaining_budget)
        st.download_button(
            label="Pobierz raport PDF",
            data=pdf_bytes,
            file_name="raport_budzetowy.pdf",
            mime="application/pdf"
        )

