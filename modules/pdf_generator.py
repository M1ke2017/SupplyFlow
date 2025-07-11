from fpdf import FPDF
import os
from datetime import datetime
from io import BytesIO

def generate_delivery_report(order_id, component, quantity, needed_by):
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join("data", "fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=16)
    pdf.cell(200, 10, "Raport Dostaw", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Numer zamówienia: {order_id}", ln=True)
    pdf.cell(200, 10, txt=f"Komponent: {component}", ln=True)
    pdf.cell(200, 10, txt=f"Ilość: {quantity}", ln=True)
    pdf.cell(200, 10, txt=f"Potrzebne do: {needed_by}", ln=True)
    pdf.cell(200, 10, txt=f"Zrealizowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    folder = "data/reports"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"raport_zamowienia_{order_id}.pdf")
    pdf.output(filepath)
    with open(filepath, 'rb') as f:
        return f.read()
   
def generate_budget_report(history_data, remaining_budget):
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join("data", "fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=16)
    pdf.cell(200, 10, "Raport Budżetowy", ln=True, align="C")
    pdf.ln(10)

    for item in history_data.values:
        if len(item) >= 5:
            pdf.cell(200, 10, txt=f"ID: {item[0]} | {item[1]} x {item[2]} szt. | Koszt: {item[2]*item[3]:.2f} zł | Data: {item[4]}", ln=True)
        else:
            pdf.cell(200, 10, txt=f"Błąd danych w rekordzie: {item}", ln=True)


    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Pozostały budżet: {remaining_budget:.2f} zł", ln=True)

    folder = "data/reports"
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"raport_budzetowy.pdf")
    pdf.output(filepath)
    with open(filepath, 'rb') as f:
        return f.read()

def generate_analytics_report(df_component, df_monthly, df_stock):
    pdf = FPDF()
    pdf.add_page()
    
    font_path = os.path.join("data", "fonts", "DejaVuSans.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", size=16)
    pdf.cell(200, 10, "Raport Analityczny", ln=True, align="C")

    pdf.set_font("DejaVu", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, "Wydatki wg komponentów", ln=True)
    for index, row in df_component.iterrows():
        pdf.cell(200, 8, f"{row['Komponent']}: {row['Koszt']} zł", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Wydatki miesięczne", ln=True)
    for index, row in df_monthly.iterrows():
        month = row['Miesiąc'].strftime('%Y-%m')
        pdf.cell(200, 8, f"{month}: {row['Koszt']} zł", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Stan magazynowy", ln=True)
    for index, row in df_stock.iterrows():
        pdf.cell(200, 8, f"{row['Komponent']}: {row['Stan']} szt.", ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin1')  
    buffer = BytesIO(pdf_bytes)
    return buffer
