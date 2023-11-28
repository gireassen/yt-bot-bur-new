from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import ujson

with open('conf/config.json', encoding='utf-8') as f:
    data_load = ujson.load(f)


def send_mail_to(send_to, subject, message, files=None):
    smtp_server = data_load["mail_data"]["smtp_server"]
    smtp_port = data_load["mail_data"]["smtp_port"]
    mail_login = data_load["mail_data"]["mail_login"]
    mail_password = data_load["mail_data"]["mail_password"]

    msg = MIMEMultipart("mixed")
    msg['From'] = mail_login
    msg['To'] = ",".join(send_to)
    msg['Subject'] = subject

    message_content = MIMEText(message)
    msg.attach(message_content)

    if files is not None:
        with open(f'{files}', 'rb') as f:
            file_data = f.read()
            attachment = MIMEApplication(file_data, Name=files[11:])
            attachment['Content-Disposition'] = f'attachment; filename={files[11:]}'
            msg.attach(attachment)

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(mail_login, mail_password)
        server.sendmail(mail_login, send_to, msg.as_string())



if __name__ == "__main__":
    print("email_module.py")