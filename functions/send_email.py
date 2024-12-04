from email.message import EmailMessage
import smtplib


class SendEmail:

    def enviar_mail_h2o_faltante(tabla_faltantes):

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
            <h1>Seguimiento piezas sin H2o AGP sGlass</h1>
            <p>Se ha detectado las siguientes piezas aprobadas en UMA4 no tienen registro de H2o (Y lo requiere):</p>
            <p>Detalles:</p>
            {tabla_faltantes} 
            <p>Esto es un correo enviado automaticamente. Atentamente equipo de Smart Factory AGPsglass Colombia</p>
        </div>
        </body>
        </html>
        """
        email = EmailMessage()
        email["From"] = remitente
        destinatario = ["dbareno@agpglass.com", "opinto@agpglass.com","xarodriguez@agpglass.com", "magonzalez@agpglass.com", "fcastillo@agpglass.com","afgarcia@agpglass.com"]
        email["Subject"] = "Alerta NO H2o UMA 4"
        email.add_alternative(mensaje, subtype="html")

        smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        smtp.starttls()
        smtp.login(remitente, "AGPglass2021")
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()
        print("Email Enviado con exito..")

    def enviar_mail_h2o_incoming(tabla_faltantes):

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
            <h1>Seguimiento piezas entrantes UMA4 AGP sGlass</h1>
            <p>Se ha detectado las siguientes piezas que van a llegar proximamente a UMA4:</p>
            <p>Detalles:</p>
            {tabla_faltantes} 
            <p> Si existen valores negativos en ENTH puede indicar que la pieza no tuvo registro en Salida de hornos (SALH) o es un indicativo de que el tiempo de ciclo fue mayor al esperado máximo (23 horas)</p>
            <p> Para valores negativos en SALH significa que es una pieza que no ha bajado de hornos o no se ha retenido a la entrada UMA4 </p>
            <p> Este correo aún no incluye las piezas que estén en la directriz 34, no avisa de recuperaciones de lites ni cambios tapa/pro </p>
            
            <p>Esto es un correo enviado automaticamente. Atentamente equipo de Smart Factory AGPsglass Colombia</p>

        </div>
        </body>
        </html>
        """
        email = EmailMessage()
        email["From"] = remitente
        destinatario = ["dbareno@agpglass.com", "opinto@agpglass.com","xarodriguez@agpglass.com", "magonzalez@agpglass.com", "fcastillo@agpglass.com","afgarcia@agpglass.com"]
        email["Subject"] = "Segumiento ingresos H2o Uma4"
        email.add_alternative(mensaje, subtype="html")

        smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        smtp.starttls()
        smtp.login(remitente, "AGPglass2021")
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()
        print("Email Enviado con exito..")

    def enviar_mail_gasp_faltante(tabla_faltantes):

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
            <h1>Seguimiento piezas sin medición GASP AGP sGlass</h1>
            <p>Se ha detectado las siguientes piezas aprobadas en UMA4 no tienen registro de Esfuerzos (GASP) (Y lo requiere):</p>
            <p>Detalles:</p>
            {tabla_faltantes} 
            <p>Esto es un correo enviado automaticamente. Atentamente equipo de Smart Factory AGPsglass Colombia</p>
        </div>
        </body>
        </html>
        """
        email = EmailMessage()
        email["From"] = remitente
        destinatario = ["dbareno@agpglass.com"]#, "dpinilla@agpglass.com"]#, "salvarez@agpglass.com"]
        email["Subject"] = "Alerta NO GASP X5"
        email.add_alternative(mensaje, subtype="html")

        smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        smtp.starttls()
        smtp.login(remitente, "AGPglass2021")
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()
        print("Email Enviado con exito..")
