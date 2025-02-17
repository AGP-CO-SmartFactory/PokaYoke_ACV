from functions.log_manager import LogManager
from email.message import EmailMessage
import smtplib

log_manager = LogManager()

class SendEmail:

    @log_manager.log_errors(sector = 'Enviar Email')
    def mail_nc_acv(tabla_nc):

        tabla_nc = tabla_nc.to_html(index=False, border=1, justify="center")
        print("Enviando correo...")
        remitente = "pcplanta@agpglass.com"

        mensaje = f"""
        <html>
        <head>
        <style>
        /* Estilos personalizados para el correo */
        body {{
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
            padding: 20px;
        }}
        .container {{
            background-color: #fff;
            border-radius: 10px;
            padding: 20px;
        }}
        h1 {{
            color: #333;
        }}
        .alert {{
            color: #ff0000;
            font-weight: bold;
        }}
        </style>
        </head>
        <body>
        <div class="container">
            <h1>Seguimiento NC desaireación AGP sGlass</h1>
            <p>Se ha detectado las siguientes piezas con desaireación aprobada que no cumple con los criterios establecidos:</p>
            <p>Detalles:</p>
            {tabla_nc} 
            <p>Esto es un correo enviado automaticamente. Atentamente equipo de Smart Factory AGPsglass Colombia</p>
        </div>
        </body>
        </html>
        """
        email = EmailMessage()
        email["From"] = remitente
        destinatario = ["dbareno@agpglass.com", "ltovar@agpglass.com", "ebejarano@agpglass.com", "wrubio@agpglass.com", 
                        "jogomez@agpglass.com", "xarodriguez@agpglass.com", "afgarcia@agpglass.com", "opinto@agpglass.com", 
                        "fcastillo@agpglass.com", "dsalas@agpglass.com"]
        email["Subject"] = "Alerta NC Desaireacion ACV"
        email.add_alternative(mensaje, subtype="html")

        smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        smtp.starttls()
        smtp.login(remitente, "AGPglass2021")
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()
        print("Email Enviado con exito..")
