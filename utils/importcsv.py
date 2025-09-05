import csv

def import_csv(file_path):
    amount = 0
    tax = 0.22
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        headers = next(reader)
        time_idx = headers.index(headers[0])
        poraba_idx = headers.index(headers[1])
        cena_idx = headers.index(headers[2])
        first_day = ''
        last_day = ''
        for i, row in enumerate(reader):
            if i ==0:
                first_day = row[time_idx]
            last_day = row[time_idx]
            amount += float(poraba_idx) * float(cena_idx)
    ddv = amount * tax
    return (first_day, last_day, amount, ddv)
            