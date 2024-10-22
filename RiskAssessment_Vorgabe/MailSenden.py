#  pip install pydantic
#  pip install pylance
#  pip install camunda-external-task-client-python3

import os
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker
import smtplib
import getpass

# SMTP-Server-Details
# Mail-Server aus Environment lesen. Falls nicht definiert, localhost verwenden
# Umgebungsvariable gefüllt nach Vorlage "Server;Port;User;Passwort", bspw: "smtp.example.com;465;your_email@example.com;"
print("Ausgabe gemacht")
server_data = os.getenv("M254_MailServerData")
print(server_data)
if server_data is not None:
    smtp_server, smtp_port, username, password = server_data.split(";")
    print(password)
    if password == '':
        password = getpass.getpass(f"Bitte Passwort für Benutzer '{username}' für SMTP-Server '{smtp_server}' eingeben: ")
else:
    smtp_server = "localhost"
    print(f"Ausgabe auf Mailserver '{smtp_server}'")

# configuration for the Client
default_config = {
    "maxTasks": 1,
    "lockDuration": 10000,
    "asyncResponseTimeout": 5000,
    "retries": 3,
    "retryTimeout": 5000,
    "sleepSeconds": 30
}

def handle_task(task: ExternalTask) -> TaskResult:
    """
    Sendet ein eMail. Die Angaben dazu werden aus Variablen gelesen:
    fromEmailAddress, toEmailAddress, mailSubject, mailBody
    """
    from_address = task.get_variable("fromEmailAddress")
    to_addresses = task.get_variable("toEmailAddresses")
    mail_subject = task.get_variable("mailSubject")
    mail_body = task.get_variable("mailBody")

    try:
        send_mail(from_address, to_addresses, mail_subject, mail_body)
    except Exception as e:
        print(f"Exception raised: {e}")
        return task.failure(error_message="task failed",  error_details=f"failed with Exception {e}", 
                                max_retries=2, retry_timeout=2000)
    
    return task.complete({"success": True, "ResultText": "Mail wurde versandt"}) 



def send_mail(from_address, to_addresses, mail_subject, mail_body):
    # Add the From: and To: headers at the start!
    lines = [f"From: {from_address}", f"To: {to_addresses}", f"Subject: {mail_subject}"]
    line = mail_body
    lines.append("")
    lines.append(line)

    msg = "\r\n".join(lines)
    print("Message length is", len(msg))

    if smtp_server == "localhost":    
        server = smtplib.SMTP(smtp_server)
    else:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()                       # ESMTP-Handshake
        server.starttls()                   # TLS-Verschlüsselung aktivieren (für Sicherheit)    
        server.ehlo()                       # ESMTP-Handshake erneut nach dem Starten von TLS    
        server.login(username, password)    # Anmeldung beim SMTP-Server

    server.set_debuglevel(1)
    server.sendmail(from_address, to_addresses.split(","), msg)
    server.quit()        

if __name__ == '__main__':
   ExternalTaskWorker(worker_id="2", config=default_config).subscribe("SendMail", handle_task)