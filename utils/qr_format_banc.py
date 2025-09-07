import io
import qrcode

def generate_upn_qr(
    iban: str,
    amount: float,
    reference: str,
    payer_name: str,
    payer_address: str,
    payer_post: str,
    receiver_name: str,
    receiver_address: str,
    receiver_post: str,
    purpose: str
):
    lines = [
        "UPNQR",         
        "1",             
        "0",             
        "0",             
        iban.replace(" ", ""),  
        f"EUR{str(amount).replace('.', ',')}",     
        reference,       
        purpose,         
        receiver_name,   
        receiver_address,
        receiver_post,   
        payer_name,      
        payer_address,   
        payer_post,      
    ]

    while len(lines) < 30:
        lines.append("")

    qr_text = "\n".join(lines)

    qr = qrcode.make(qr_text)
    qr_bytes = io.BytesIO()
    qr.save(qr_bytes, format="PNG")
    qr_bytes.seek(0)
    return qr_bytes
