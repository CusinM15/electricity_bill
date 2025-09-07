from utils.global_variable import tax, iban, referenca, company_name, plus_day_pay, reciver_address, reciver_post
from utils.qr_format_banc import generate_upn_qr
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import qrcode
import io
from database import get_db
from models.customer import Customer
from datetime import date, timedelta    
# register UTF-8 writing
pdfmetrics.registerFont(TTFont("DejaVu", "fonts/DejaVuSans.ttf"))

def generate_invoice(customer, first_day, last_day, amount, save_path):
    today = date.today()
    pay_till = today + timedelta(days=plus_day_pay)
    document = canvas.Canvas("static/bills/" + save_path, pagesize=A4, encoding='utf-8-sign')
    width, height = A4
    ddv = amount * tax
    # title
    document.setFont("DejaVu", 16)
    document.drawString(50, height - 50, "Račun - Ta-bol štrom")

    # custumer data
    document.setFont("DejaVu", 12)
    document.drawString(50, height - 100, f"Ime: {customer.name}")
    document.drawString(50, height - 130, f"Email: {customer.email}")
    document.drawString(50, height - 160, f"Naslov: {customer.address}")

    # invoice data
    document.drawString(50, height - 190, f"Datum izdaje: {today}")
    document.drawString(50, height - 220, f"Rok plačila: {pay_till}")
    document.drawString(50, height - 250, f"Obdobje: {first_day.split('T')[0]} - {last_day.split('T')[0]}")
    document.drawString(50, height - 280, f"Znesek (brez DDV): {amount:.2f} €")
    document.drawString(50, height - 310, f"DDV: {ddv:.2f} €")
    document.drawString(50, height - 340, f"Skupaj: {amount + ddv:.2f} €")

    # split custommer address
    address_parts = customer.address.split(',')
    customer_short_add = address_parts[0]
    customer_post_add = address_parts[1].strip() if len(address_parts) > 1 else ""
    # QR code 
    qr_bytes = generate_upn_qr( # ment for bank appp to read it, but not successfuly, for now
        iban=iban,
        amount=amount + ddv,
        reference=referenca,
        payer_name=customer.name,
        payer_address=customer_short_add,
        payer_post=customer_post_add,  
        receiver_name=company_name,
        receiver_address=reciver_address,
        receiver_post=reciver_post,
        purpose=f"Plačilo računa za obdobje {first_day.split('T')[0]} - {last_day.split('T')[0]}",
    )

    qr_image = ImageReader(qr_bytes)
    document.drawImage(qr_image, width - 200, height - 250, 150, 150)

    document.showPage()
    document.save()
    return save_path


