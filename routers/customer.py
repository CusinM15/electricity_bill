from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models.customer import Customer

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/invoice/customer")
def show_invoice(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.name, Customer.address, Customer.post).all()
    return templates.TemplateResponse("customer.html", {"request": request, "customers": customers})

@router.post("/invoice/customer")
async def process_invoice(
    request: Request,
    proxy_mode: str = Form(...),
    name: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    post: str = Form(""),
    customer_id: str = Form(""),
    known_name: str = Form(""),
    known_email: str = Form(""),
    known_address: str = Form(""),
    db: Session = Depends(get_db)
):
    errors = []
    if proxy_mode == "0":
        # new customer validation
        if not name:
            errors.append("Ime je obvezno.")
        if not email:
            errors.append("Email je obvezen.")
        if not address:
            errors.append("Naslov je obvezen.")
        if errors:
            customers = db.query(Customer).order_by(Customer.name, Customer.address).all()
            return templates.TemplateResponse("customer.html", {"request": request, "errors": errors, "customers": customers})
        existing = db.query(Customer).filter(Customer.email == email).first()
        if existing:
            errors.append("Email že obstaja.")
            customers = db.query(Customer).order_by(Customer.name, Customer.address).all()
            return templates.TemplateResponse("customer.html", {"request": request, "errors": errors, "customers": customers})
        db_customer = Customer(name=name.strip(), email=email-strip(), address=address.strip(), post=post.strip())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        selected_customer = db_customer
    else:
        # known customer
        if not customer_id:
            errors.append("Izberi uporabnika.")
            customers = db.query(Customer).order_by(Customer.name, Customer.address).all()
            return templates.TemplateResponse("customer.html", {"request": request, "errors": errors, "customers": customers})
        customer = db.query(Customer).filter(Customer.id == int(customer_id)).first()
        if not known_name:
            errors.append("Ime je obvezno.")
        if not known_email:
            errors.append("Email je obvezen.")
        if not known_address:
            errors.append("Naslov je obvezen.")
        if errors:
            customers = db.query(Customer).order_by(Customer.name, Customer.address).all()
            return templates.TemplateResponse("customer.html", {"request": request, "errors": errors, "customers": customers})
        if not customer:
            errors.append("Uporabnik ne obstaja.")
            customers = db.query(Customer).order_by(Customer.name, Customer.address).all()
            return templates.TemplateResponse("customer.html", {"request": request, "errors": errors, "customers": customers})
        # check if data was changed
        if (known_name != customer.name or known_email != customer.email or known_address != customer.address or known_post != customer.post):
            # if email changed, check uniqueness
            if known_email != customer.email:
                existing = db.query(Customer).filter(Customer.email == known_email).first()
                if existing:
                    errors.append("Email že obstaja.")
                    customers = db.query(Customer).order_by(Customer.name, Customer.address).all()
                    return templates.TemplateResponse("customer.html", {"request": request, "errors": errors, "customers": customers})
            # update customer
            customer.name = known_name.strip()
            customer.email = known_email.strip()
            customer.address = known_address.strip()
            customer.post = known_post.strip()
            db.commit()
        selected_customer = customer


    return RedirectResponse(url=f"/invoice/csvimport?customer_id={selected_customer.id}", status_code=303)
