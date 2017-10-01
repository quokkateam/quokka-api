import sendgrid
import os
from sendgrid.helpers.mail import *


def send_test_email_to_andrew():
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("anoyes34@gmail.com")
    to_email = Email("anoyes34@gmail.com")
    subject = "Hello from Quokka API"
    content = Content("text/plain", "")
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
