import os
import sys
import shutil
import logging
from time import sleep
from lib.mail import Mail
from lib.imap_connector import ImapConnector
from lib.preconfig import Preconfig


active=True

def clean_up(data_dir):
    try:
        if os.path.isfile(data_dir) or os.path.islink(data_dir):
            os.unlink(data_dir)
        elif os.path.isdir(data_dir):
            shutil.rmtree(data_dir)
    except Exception as e:
        print('Failed to delete {}. Reason: {}'.format(data_dir, e))
    finally:
        mail_dir = data_dir+'/mails'
        os.makedirs(mail_dir, exist_ok=True)
    return True


def exit_gracefully(signum, frame):
    global active
    active=False

def start():


    preconfig = Preconfig()
    config = preconfig.cfg


    logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.FileHandler(config['SETTINGS']['logfile'])
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    data_dir = config['SETTINGS']['working_dir']
    mail_dir = mail_dir = data_dir+'/mails'

    logger.info('Starting...'+str(active))
    while active:
        try:
            clean_up(data_dir)

            imap_connection = ImapConnector(config, logger)
            imap_connection.open_connection()
            mailboxes = imap_connection.list_mailboxes()

            for mailbox in mailboxes:

                messages = imap_connection.retrieve_messages_list(mailbox)

                for msgid in messages:
                    message = imap_connection.retrieve_message(msgid)
                    mail = Mail(config, logger, message)
                    mail.parse()
                    file_content = mail.text

                    file_name_prefix = "{sender}-{subject}".format(
                        sender=mail.sender, subject=mail.subject)

                    file_name = file_name_prefix

                    number = 0
                    while os.path.exists(mail_dir+'/'+file_name):
                        file_name = file_name_prefix + \
                            "-{number}".format(number=number)
                        number = number + 1

                    with open(mail_dir+'/'+file_name, 'w') as file:
                        file.write(file_content)

                    timeline_dir = '{data_dir}/timeline/{year}/{month}/{day}'.format(
                        data_dir=data_dir,
                        year=mail.date.strftime('%Y'),
                        month=mail.date.strftime('%m'),
                        day=mail.date.strftime('%d')
                    )

                    os.makedirs(timeline_dir, exist_ok=True)
                    os.symlink(mail_dir+'/'+file_name,
                               timeline_dir+'/'+file_name)

                    sender_dir = data_dir+'/sender/'+mail.sender
                    os.makedirs(sender_dir, exist_ok=True)
                    os.symlink(mail_dir+'/'+file_name,
                               sender_dir+'/'+file_name)

                    topics_dir = data_dir+'/topics/'+mailbox
                    os.makedirs(topics_dir, exist_ok=True)
                    os.symlink(mail_dir+'/'+file_name,
                               topics_dir+'/'+file_name)
        except Exception as err:
            logger.error('ERROR:', err)
        finally:
            imap_connection.close_conection()
            timer = 0
            while active and timer < int(config["SETTINGS"]['timer']):
                timer = timer+1
                sleep(1)
    logger.info('Exiting...')
    os.unlink('/var/run/mail_exposer.pid')
    sys.exit(0)

if __name__ == "__main__":
    active = True
    start()
