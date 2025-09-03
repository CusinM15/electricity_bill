from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/invoice/{invoice_id}", response_class=HTMLResponse)
def get_invoice(request: Request, invoice_id: int):
    return templates.TemplateResponse(
        "invoice.html", 
        {"request": request, "invoice_id": invoice_id, "total": 123.45}
    )
