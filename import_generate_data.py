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
    db.query(Customer).delete()
    db.commit()
    for element in users_list:
        # dodaj customerja
        customer = Customer(
            name=element[0],
            email=element[1],
            address=element[2]
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

        # naključno število računov za stranko
        num_f = random.randint(1, 5)  # ne 20, da ne bo predolgo
        csv_files = [f for f in os.listdir(CSV_WAITING_DIR) if f.endswith(".csv")]

        for i in range(num_f):
            if not csv_files:
                print("Ni CSV datotek v mapi:", CSV_WAITING_DIR)
                return

            chosen_file = random.choice(csv_files)
            file_path = os.path.join(CSV_WAITING_DIR, chosen_file)

            # import podatkov iz CSV
            first_day, last_day, amount = import_csv(file_path)
            today = date.today()
            pay_till = today + timedelta(days=plus_day_pay)
            # dodaj invoice
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

            # dodaj pot do pdf računa
            save_path = f"racun{invoice.id}.pdf"
            invoice.file_path = save_path
            db.commit()

            # generiraj račun v PDF
            generate_invoice(customer, first_day, last_day, amount, save_path)
            print(f"Račun {save_path} ustvarjen za {customer.name}")

if __name__ == "__main__":
    import_data()
