import email
import os
import re
import datetime
from quopri import decodestring
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class Mail:
    def __init__(self, config, logger, message):
        self.config = config
        self.logger = logger
        self.message = message
        self.headers = None
        self.sender = None
        self.to = None
        self.date = None
        self.subject = None
        self.body = None
        self.text = None

    def get_str(self, str):
        return decodestring(str).decode()

    def get_date(self, date):
        try:
            return datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
        except ValueError:
            return date

    def get_email(self, email):
        email = decodestring(email).decode()
        if "<" in email and ">" in email:
            match = re.search(r"\<([A-Za-z0-9_.@]+)\>", email)
            result = match.group(1)
        else:
            result = email
        return result

    def get_body(self, msg):
        type = msg.get_content_maintype()

        if type == 'multipart':
            for part in msg.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload(decode=True).decode('utf-8')

        elif type == 'text':
            return msg.get_payload(decode=True).decode('utf-8')

    def parse(self):
        mail = email.message_from_string(self.message)

        self.headers = dict(mail._headers)
        self.sender = self.get_email(self.headers['From'])
        self.to = self.get_email(self.headers['To'])
        self.date = self.get_date(self.headers['Date'])
        self.subject = self.get_str(self.headers['Subject'])
        self.body = self.get_body(mail)

        template_path = os.path.join(os.path.dirname(__file__), './')
        templateLoader = FileSystemLoader(searchpath=template_path)
        templateEnv = Environment(loader=templateLoader)
        template = templateEnv.get_template('mail_template.j2')
        self.text = template.render(mail=self)
