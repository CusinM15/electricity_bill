from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, engine

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/reports")
def get_reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})


@router.get("/reports_data")
def get_reports_data(
    db: Session = Depends(get_db),
    date_from: str = Query(None),
    date_to: str = Query(None),
    sum_mode: str = Query("normal"),
):
    try:
        with engine.connect() as conn:
            base_query = """
                SELECT 
                    c.id AS customer_id,
                    c.name,
                    c.email,
                    c.address,
                    c.post,
                    i.file_path,
                    i.due_date,
                    i.iban,
                    i.reference,
                    i.amount_net,
                    i.amount_gross,
                    i.date_from,
                    i.date_to
                FROM invoices i
                JOIN customers c ON c.id = i.customer_id
                WHERE 1=1
            """

            params = {}
            if date_from:
                base_query += " AND i.date_from >= :date_from"
                params["date_from"] = date_from
            if date_to:
                base_query += " AND i.date_to <= :date_to"
                params["date_to"] = date_to

            if sum_mode == "normal":
                base_query += " ORDER BY i.date_from ASC"
                result = conn.execute(text(base_query), params).mappings()
                return [dict(row) for row in result]

            elif sum_mode == "byCustomer":
                query = """
                    SELECT 
                        c.email,
                        c.name,
                        c.address,
                        c.post,
                        SUM(i.amount_net) AS amount_net,
                        SUM(i.amount_gross) AS amount_gross
                    FROM invoices i
                    JOIN customers c ON c.id = i.customer_id
                    WHERE 1=1
                """
                if date_from:
                    query += " AND i.date_from >= :date_from"
                if date_to:
                    query += " AND i.date_to <= :date_to"
                query += " GROUP BY c.email, c.name, c.address"
                result = conn.execute(text(query), params).mappings()
                return [dict(row) for row in result]

            elif sum_mode == "byPeriod":
                query = """
                    SELECT 
                        MIN(i.date_from) AS date_from,
                        MAX(i.date_to) AS date_to,
                        SUM(i.amount_net) AS amount_net,
                        SUM(i.amount_gross) AS amount_gross
                    FROM invoices i
                    JOIN customers c ON c.id = i.customer_id
                    WHERE 1=1
                    GROUP BY i.date_from
                """

                result = conn.execute(text(query), params).mappings()
                return [dict(row) for row in result]
            
            elif sum_mode == "byPost":
                query = """
                    SELECT 
                        c.post,
                        MIN(i.date_from) AS date_from,
                        MAX(i.date_to) AS date_to,
                        SUM(i.amount_net) AS amount_net,
                        SUM(i.amount_gross) AS amount_gross
                    FROM invoices i
                    JOIN customers c ON c.id = i.customer_id
                    WHERE 1=1
                    GROUP BY c.post
                """

                result = conn.execute(text(query), params).mappings()
                return [dict(row) for row in result]

    except Exception as e:
        print(f"Database error: {e}")
        return {"error": "Failed to retrieve reports"}



@router.get("/reports_filters")
def get_reports_filters():
    try:
        with engine.connect() as conn:
            query_from = "SELECT DISTINCT date_from FROM invoices ORDER BY date_from ASC;"
            query_to = "SELECT DISTINCT date_to FROM invoices ORDER BY date_to DESC;"

            from_dates = [str(row[0]) for row in conn.execute(text(query_from)).fetchall()]
            to_dates = [str(row[0]) for row in conn.execute(text(query_to)).fetchall()]

            return {"from_dates": from_dates, "to_dates": to_dates}

    except Exception as e:
        print(f"Database error: {e}")
        return {"error": "Failed to retrieve filters"}
