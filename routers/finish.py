from fastapi import APIRouter, Request, Form, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,FileResponse
import os
from utils.importcsv import import_csv  
from utils.create_invoice import generate_invoice  
from utils.move_csv import move_csv
from utils.global_variable import CSV_WAITING_DIR, CSV_SEND_DIR, plus_day_pay, iban, referenca, tax, BILL_DIR
from database import get_db
from models.customer import Customer
from models.invoice import Invoice
from datetime import date, timedelta, datetime    
import smtplib
from email.message import EmailMessage

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/invoice/finish")
def show_finish(request: Request, invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "Invoice not found"})
    return templates.TemplateResponse("finish.html", {"request": request, "invoice": invoice})


@router.get("/invoice/download/{invoice_id}", name="download_invoice")
def download_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return {"error": "Invoice not found"}
    return FileResponse(path=f"{BILL_DIR}{invoice.file_path}", filename=os.path.basename(invoice.file_path), media_type="application/pdf")


@router.post("/invoice/send/{invoice_id}", name="send_invoice")
def send_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return {"error": "Invoice not found"}
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    
    msg = EmailMessage()
    msg["Subject"] = "Vaš račun"
    msg["From"] = "noreply@strom.si"
    msg["To"] = customer.email
    msg.set_content("Pozdravljeni,\nv prilogi je vaš račun.")

    pdf_path = f"static/bills/{invoice.file_path}"
    with open(pdf_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(pdf_path)
        msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("mt.cusin+notifications@gmail.com", "ombj lsea krvw grye")
            smtp.send_message(msg)
    except SMTPAuthenticationError as e:
        print(f"Napaka pri prijavi na SMTP strežnik: {e}")
        return {"error": "Napaka pri prijavi na SMTP strežnik. Preverite geslo za aplikacijo."}
    except Exception as e:
        print(f"Nepričakovana napaka: {e}")
        return {"error": "Prišlo je do nepričakovane napake pri pošiljanju e-pošte."}

    return RedirectResponse(url=f"/", status_code=303)