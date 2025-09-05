from fastapi import APIRouter, Request, Form, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import os
from utils.importcsv import import_csv  
from database import get_db
from models.customer import Customer


router = APIRouter()
templates = Jinja2Templates(directory="templates")

CSV_WAITING_DIR = "static/csv/waiting"

@router.get("/invoice/csvimport")
def show_csvimport(request: Request, customer_id: int, db: Session = Depends(get_db)):
    print('v get', customer_id)
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
    print('v post',customer_id)
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return templates.TemplateResponse("error.html", {"request": request, "msg": "Customer not found"})
   
    first_day, last_day, amount, ddv = import_csv(os.path.join(CSV_WAITING_DIR, selected_file))
    print(f"Imported file: {selected_file}, First Day: {first_day}, Last Day: {last_day}, Amount: {amount}, DDV: {ddv}, Name: {customer.name}, Email: {customer.email}, Address: {customer.address}")
    return RedirectResponse(url="/invoice/finish", status_code=303)