import os
import sys
import shutil
from time import sleep
from lib.mail import Mail
from lib.imap_connector import ImapConnector
from lib.preconfig import Preconfig, Logger


active=True

def clean_up(data_dir):
    for dir in ['mails','sender','timeline','topics']:
        try:
            if os.path.isfile(f"{data_dir}/{dir}") or os.path.islink(f"{data_dir}/{dir}"):
                os.unlink(f"{data_dir}/{dir}")
            elif os.path.isdir(f"{data_dir}/{dir}"):
                shutil.rmtree(f"{data_dir}/{dir}")
        except Exception as e:
            print(f"Failed to delete {data_dir}/{dir}. Reason: {e}")
        finally:
            os.makedirs(f"{data_dir}/{dir}", exist_ok=True)
    return True


def exit_gracefully(signum, frame):
    global active
    active=False


def start():
    preconfig = Preconfig()
    config = preconfig.cfg
    logger = Logger(config)
    log = logger.log

    data_dir = config['SETTINGS']['working_dir']
    data_dir = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), data_dir)
    mail_dir = f"{data_dir}/mails"

    log.info('Starting...')
    while active:
        try:
            clean_up(data_dir)

            imap_connection = ImapConnector(config, log)
            imap_connection.open_connection()
            mailboxes = imap_connection.list_mailboxes()

            for mailbox in mailboxes:

                msgids = imap_connection.retrieve_messages_list(mailbox)

                for msgid in msgids:
                    message = imap_connection.retrieve_message(msgid)
                    mail = Mail(config, log, message)
                    mail.parse()
                    file_content = mail.text

                    file_name_prefix = f"{mail.sender}-{mail.subject}"
                    file_name = file_name_prefix

                    number = 0
                    while os.path.exists(f"{mail_dir}/{file_name}"):
                        file_name = f"{file_name_prefix}-{number}"
                        number = number + 1

                    with open(f"{mail_dir}/{file_name}", 'w') as file:
                        file.write(file_content)

                    timeline_dir = "{data_dir}/timeline/{year}/{month}/{day}".format(
                        data_dir=data_dir,
                        year=mail.date.strftime('%Y'),
                        month=mail.date.strftime('%m'),
                        day=mail.date.strftime('%d')
                    )

                    os.makedirs(timeline_dir, exist_ok=True)
                    os.symlink(f"{mail_dir}/{file_name}",  
                               f"{timeline_dir}/{file_name}")

                    sender_dir = f"{data_dir}/sender/{mail.sender}"
                    os.makedirs(sender_dir, exist_ok=True)
                    os.symlink(f"{mail_dir}/{file_name}",
                               f"{sender_dir}/{file_name}")

                    topics_dir = f"{data_dir}/topics/{mailbox}"
                    os.makedirs(topics_dir, exist_ok=True)
                    os.symlink(f"{mail_dir}/{file_name}",
                               f"{topics_dir}/{file_name}")

        except Exception as err:
            log.error('ERROR:', err)
        finally:
            imap_connection.close_conection()
            timer = 0
            while active and timer < int(config["SETTINGS"]["timer"]):
                timer = timer + 1
                sleep(1)
    log.info('Exiting...')
    clean_up(data_dir)
    os.unlink('/var/run/mail_exposer.pid')
    sys.exit(0)

if __name__ == "__main__":
    active = True
    start()
