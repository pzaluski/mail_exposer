import os
import sys
import shutil
from time import sleep
import hashlib
import yaml
from lib.mail import Mail
from lib.imap_connector import ImapConnector
from lib.preconfig import Preconfig, Logger


active=True

"""def clean_up(data_dir):
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
    return True"""


def remove_empty_folders(path, removeRoot=True):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        print(f"Removing empty folder: {path}")
        os.rmdir(path)

def remove_files(files_to_remove):
    for file in files_to_remove:
        try:
            if os.path.isfile(file) or os.path.islink(file):
                os.unlink(file)
        except Exception as e:
            print(f"Failed to delete {file}. Reason: {e}")
    return True

    """for dir in ['mails','sender','timeline','topics']:
        try:
            if os.path.isfile(f"{data_dir}/{dir}") or os.path.islink(f"{data_dir}/{dir}"):
                os.unlink(f"{data_dir}/{dir}")
            elif os.path.isdir(f"{data_dir}/{dir}"):
                shutil.rmtree(f"{data_dir}/{dir}")
        except Exception as e:
            print(f"Failed to delete {data_dir}/{dir}. Reason: {e}")
        finally:
            os.makedirs(f"{data_dir}/{dir}", exist_ok=True)
    return True"""

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

    for dir in ['mails','sender','timeline','topics']:
        if not os.path.isdir(f"{data_dir}/{dir}"):
            os.makedirs(f"{data_dir}/{dir}", exist_ok=True)


    log.info('Starting...')
    while active:
        try:
            #clean_up(data_dir)

            imap_connection = ImapConnector(config, log)
            imap_connection.open_connection()
            mailboxes = imap_connection.list_mailboxes()

            #load hashmap
            md5_sync_map_previous={}
            md5_sync_map={}
            if os.path.isfile(f"{data_dir}/md5_sync.map"):
                with open(f"{data_dir}/md5_sync.map", 'r') as file:
                    md5_sync_map_previous = yaml.full_load(file)

            for mailbox in mailboxes:

                msgids = imap_connection.retrieve_messages_list(mailbox)

                for msgid in msgids:
                    message = imap_connection.retrieve_message(msgid)
                    result = hashlib.md5(message.encode('utf-8'))
                    md5 = result.hexdigest()
                    file_list = list()
                    if ( md5 in md5_sync_map_previous.keys() ):
                        list_of_dirs = [ e.rsplit('/',1)[0] for e in md5_sync_map_previous[md5] ]
                        if f"{data_dir}/topics/{mailbox}" in list_of_dirs:
                            md5_sync_map[md5]=md5_sync_map_previous.pop(md5)
                            continue
                    
                    mail = Mail(config, log, message)
                    mail.parse()
                    file_content = mail.text

                    file_name_prefix = f"{mail.sender}-{mail.subject}"
                    file_name = file_name_prefix

                    number = 0
                    while os.path.exists(f"{mail_dir}/{file_name}.txt"):
                        file_name = f"{file_name_prefix}-{number}"
                        number = number + 1

                    # add extension
                    file_name = f"{file_name}.txt"

                    with open(f"{mail_dir}/{file_name}", 'w') as file:
                        file.write(file_content)
                    file_list.append(f"{mail_dir}/{file_name}")

                    timeline_dir = "{data_dir}/timeline/{year}/{month}/{day}".format(
                        data_dir=data_dir,
                        year=mail.date.strftime('%Y'),
                        month=mail.date.strftime('%m'),
                        day=mail.date.strftime('%d')
                    )
                    sender_dir = f"{data_dir}/sender/{mail.sender}"
                    topics_dir = f"{data_dir}/topics/{mailbox}"

                    for symlink_dir in [timeline_dir, sender_dir, topics_dir]:
                        os.makedirs(symlink_dir, exist_ok=True)
                        os.symlink(f"{mail_dir}/{file_name}",  
                                f"{symlink_dir}/{file_name}")
                        file_list.append(f"{symlink_dir}/{file_name}")

                    md5_sync_map[md5]=file_list
            with open(f"{data_dir}/md5_sync.map", 'w') as file:
                yaml.dump(md5_sync_map, file)
 
            files_to_remove_list = [ file for file_list in md5_sync_map_previous.values() for file in file_list ]
            remove_files(files_to_remove_list)
            remove_empty_folders(data_dir)

        except Exception as err:
            log.error(f'{str(err)}')
        finally:
            imap_connection.close_conection()
            timer = 0
            while active and timer < int(config["SETTINGS"]["timer"]):
                timer = timer + 1
                sleep(1)
    log.info('Exiting...')
    os.unlink('/var/run/mail_exposer.pid')
    sys.exit(0)

if __name__ == "__main__":
    active = True
    start()
