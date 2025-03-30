import qrcode

local_ip = "192.168.0.132"  
port = "8501"
url = f"http://{local_ip}:{port}"

qr = qrcode.make(url)
qr.save("QR_code.png")