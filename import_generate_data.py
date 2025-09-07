import os
import random
from datetime import date, timedelta, datetime
from utils.users_list import users_list
from utils.global_variable import CSV_WAITING_DIR, iban, referenca, tax, plus_day_pay
from database import get_db
from models.customer import Customer
from models.invoice import Invoice
from utils.importcsv import import_csv
from utils.create_invoice import generate_invoice

def import_data():
    db = next(get_db())
    db.query(Customer).delete() # clean customer tabel, so email will be unique
    db.commit()
    for element in users_list:
        # add customer
        customer = Customer(
            name=element[0],
            email=element[1],
            address=element[2]
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

        # random number of csv, per each customer
        num_f = random.randint(1, 5)  
        csv_files = [f for f in os.listdir(CSV_WAITING_DIR) if f.endswith(".csv")] # list of csv files in correct directory

        for i in range(num_f):
            if not csv_files:
                print("Ni CSV datotek v mapi:", CSV_WAITING_DIR)
                return

            chosen_file = random.choice(csv_files) # choose one file randomly
            file_path = os.path.join(CSV_WAITING_DIR, chosen_file)

            # import data from CSV
            first_day, last_day, amount = import_csv(file_path)
            today = date.today()
            pay_till = today + timedelta(days=plus_day_pay)
            # add invoice
            date_format = '%Y-%m-%d'
            invoice = Invoice(
                customer_id=customer.id,
                date_from=datetime.strptime(first_day, date_format),
                date_to=datetime.strptime(last_day, date_format),
                due_date=pay_till,
                iban=iban,
                reference=referenca,
                amount_net=amount,
                amount_gross=amount * tax
            )
            db.add(invoice)
            db.commit()
            db.refresh(invoice)

            # invoice path
            save_path = f"racun{invoice.id}.pdf"
            invoice.file_path = save_path
            db.commit()

            # generate invoice pdf file
            generate_invoice(customer, first_day, last_day, amount, save_path)
            print(f"Račun {save_path} ustvarjen za {customer.name}")

if __name__ == "__main__":
    import_data()
