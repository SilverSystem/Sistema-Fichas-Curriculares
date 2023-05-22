import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
def enviar_correo(destinatario, asunto, cuerpo):
    load_dotenv()
    datos = os.getenv('SENDER_CREDENTIALS')
    remitente = os.getenv('SENDER_EMAIL')
    pswd = os.getenv('SENDER_PASSWORD')
    print(datos)

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    connection = smtplib.SMTP(host='smtp.gmail.com', port=587)
    connection.starttls()
    connection.login(remitente,pswd)
    connection.send_message(msg)
    connection.quit()
