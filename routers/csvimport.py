from fastapi import APIRouter, Request, Form, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import os
from utils.importcsv import import_csv  
from utils.create_invoice import generate_invoice  
from utils.move_csv import move_csv
from utils.global_variable import CSV_WAITING_DIR, CSV_SEND_DIR, plus_day_pay, iban, referenca, tax
from database import get_db
from models.customer import Customer
from models.invoice import Invoice
from datetime import date, timedelta, datetime    


router = APIRouter()
templates = Jinja2Templates(directory="templates")



@router.get("/invoice/csvimport")
def show_csvimport(request: Request, customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "Customer not found"})
    files = [f for f in os.listdir(CSV_WAITING_DIR) if f.endswith(".csv")]
    return templates.TemplateResponse("csvimport.html", {"request": request, "files": files, "customer": customer})

@router.post("/invoice/csvimport")
def import_csv_view(
    request: Request,
    customer_id: int = Form(...),
    selected_file: str = Form(...),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    today = date.today()
    pay_till = today + timedelta(days=plus_day_pay)
    if not customer:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "Customer not found"})

    first_day, last_day, amount = import_csv(os.path.join(CSV_WAITING_DIR, selected_file))
    # add invoice in db
    date_format = '%Y-%m-%d'
    db_invoice = Invoice(
        customer_id = customer.id,
        date_from = datetime.strptime(first_day, date_format),
        date_to = datetime.strptime(last_day, date_format),
        due_date = pay_till,
        iban = iban,
        reference = referenca,
        amount_net = amount,
        amount_gross = round((amount + (amount * tax)), 2)
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    save_path = f"racun{db_invoice.id}.pdf"
    db_invoice.file_path = save_path
    db.commit()
    # generate invoice
    generate_invoice(customer, first_day, last_day, amount, save_path)
    
    # move csv to new directory
    move_csv(CSV_WAITING_DIR + selected_file, CSV_SEND_DIR)
    return RedirectResponse(url=f"/invoice/finish?invoice_id={db_invoice.id}", status_code=303)