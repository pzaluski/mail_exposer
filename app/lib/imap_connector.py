import imaplib
import datetime
import base64
from quopri import decodestring


class ImapConnector:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.host = config['IMAP']['host']
        self.port = config['IMAP']['port']
        self.username = base64.b64decode(config['IMAP']['username']).decode('utf-8')
        self.password = base64.b64decode(config['IMAP']['password']).decode('utf-8')
        self.connection = imaplib.IMAP4_SSL(
            host=self.host,
            port=self.port
        )

    def open_connection(self):
        try:
            self.connection.login(self.username, self.password)
            self.logger.info("{date} Imap connection opened.".format(date=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")))
        except Exception as err:
            self.logger.error('ERROR:', err)
        return self

    def list_mailboxes(self):
        _, data = self.connection.list()
        mailboxes = []

        for mailbox in data:
            mailbox = decodestring(mailbox).decode()
            mailbox = mailbox.split(' \"/\" ')[1]
            mailboxes.append(mailbox)
        self.logger.info("Imap mailboxes collected: {mailboxes}".format(
            mailboxes=" ".join(mailboxes)))

        return mailboxes

    def retrieve_messages_list(self, mailbox):
        self.connection.select(mailbox=mailbox, readonly=True)
        _, result = self.connection.search(None, 'ALL')
        messages = result[0].split()
        self.logger.info("Imap messsages id's collected from {mailbox}: {messages}".format(
            messages=result[0].decode("utf-8"), mailbox=mailbox))

        return messages

    def retrieve_message(self, msgid):
        _, data = self.connection.fetch(msgid, '(RFC822)')
        self.logger.info("Messsage id: {msgid} retrieved.".format(
            msgid=msgid.decode("utf-8")))

        return data[0][1].decode()

    def close_conection(self):
        self.connection.close()
        self.connection.logout()
        self.logger.info("Imap connection closed.")
