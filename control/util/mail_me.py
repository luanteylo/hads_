import smtplib
from datetime import datetime


class MailMe:

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd

    def __prepare_msg(self, recipient, subject, body):
        FROM = self.user
        TO = recipient if type(recipient) is list else [recipient]
        SUBJECT = subject
        TEXT = body

        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s \n\n\n Time: %s""" % (
            FROM, ", ".join(TO), SUBJECT, TEXT, str(datetime.now()))

        return message

    def send_email(self, recipient, subject, body):
        recipient = recipient if type(recipient) is list else [recipient]
        message = self.__prepare_msg(recipient, subject, body)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(self.user, self.pwd)
        server.sendmail(self.user, recipient, message)
        server.close()
