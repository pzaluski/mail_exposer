import os
import sys
import hashlib
import yaml
from time import sleep
from lib.mail import Mail
from lib.imap_connector import ImapConnector
from lib.preconfig import Preconfig, Logger


active = True


def remove_empty_folders(log, path, removeRoot=True):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(log, fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        log.debug(f"Removing empty folder: {path}")
        os.rmdir(path)


def remove_files(log, files_to_remove):
    for file in files_to_remove:
        try:
            if os.path.isfile(file) or os.path.islink(file):
                os.unlink(file)
                log.debug(f"Removing file: {file}")

        except Exception as e:
            log.error(f"Failed to delete {file}. Reason: {e}")
    return True


def exit_gracefully(signum, frame):
    global active
    active = False


def start():
    # config and logger
    preconfig = Preconfig()
    config = preconfig.cfg
    logger = Logger(config)
    log = logger.log

    # mail dir
    data_dir = config['SETTINGS']['working_dir']
    data_dir = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), data_dir)
    mail_dir = f"{data_dir}/mails"

    # create dir structure
    for dir in ['mails', 'sender', 'timeline', 'topics']:
        if not os.path.isdir(f"{data_dir}/{dir}"):
            os.makedirs(f"{data_dir}/{dir}", exist_ok=True)
            log.debug(f"Creating directory: {data_dir}/{dir}")


    log.info('Starting...')
    while active:
        try:
            # imap connector
            imap_connection = ImapConnector(config, log)
            imap_connection.open_connection()
            mailboxes = imap_connection.list_mailboxes()

            # load md5 map
            md5_sync_map_previous = {}
            md5_sync_map = {}
            if os.path.isfile(f"{data_dir}/md5_sync.map"):
                with open(f"{data_dir}/md5_sync.map", 'r') as file:
                    md5_sync_map_previous = yaml.full_load(file)

            for mailbox in mailboxes:

                msgids = imap_connection.retrieve_messages_list(mailbox)

                for msgid in msgids:

                    # collect message from ldap and calculate md5
                    message = imap_connection.retrieve_message(msgid)
                    result = hashlib.md5(message.encode('utf-8'))
                    md5 = result.hexdigest()
                    file_list = list()
                    if (md5 in md5_sync_map_previous.keys()):
                        list_of_dirs = [e.rsplit('/', 1)[0]
                                        for e in md5_sync_map_previous[md5]]
                        if f"{data_dir}/topics/{mailbox}" in list_of_dirs:
                            md5_sync_map[md5] = md5_sync_map_previous.pop(md5)
                            continue

                    # parsing mail
                    mail = Mail(config, log, message)
                    mail.parse()
                    file_content = mail.text

                    # file name generation
                    file_name_prefix = f"{mail.sender}-{mail.subject}"
                    file_name = file_name_prefix

                    # calculate number for duplicated files
                    number = 0
                    while os.path.exists(f"{mail_dir}/{file_name}.txt"):
                        file_name = f"{file_name_prefix}-{number}"
                        number = number + 1

                    # add txt extension to files
                    file_name = f"{file_name}.txt"

                    # mail file creation
                    with open(f"{mail_dir}/{file_name}", 'w') as file:
                        file.write(file_content)
                        log.debug(f"Creating file: {mail_dir}/{file_name}")

                    file_list.append(f"{mail_dir}/{file_name}")

                    # dir structure preparation
                    timeline_dir = "{data_dir}/timeline/{year}/{month}/{day}".format(
                        data_dir=data_dir,
                        year=mail.date.strftime('%Y'),
                        month=mail.date.strftime('%m'),
                        day=mail.date.strftime('%d')
                    )
                    sender_dir = f"{data_dir}/sender/{mail.sender}"
                    topics_dir = f"{data_dir}/topics/{mailbox}"

                    # create links for files
                    for symlink_dir in [timeline_dir, sender_dir, topics_dir]:
                        os.makedirs(symlink_dir, exist_ok=True)
                        os.symlink(f"{mail_dir}/{file_name}",
                                f"{symlink_dir}/{file_name}")
                        log.debug(f"Creating file: {symlink_dir}/{file_name}")
                        file_list.append(f"{symlink_dir}/{file_name}")

                    md5_sync_map[md5] = file_list

            # write md5 map to file
            with open(f"{data_dir}/md5_sync.map", 'w') as file:
                yaml.dump(md5_sync_map, file)

            # remove deleted files and empty dirs
            files_to_remove_list = [
                file for file_list in md5_sync_map_previous.values() for file in file_list]
            remove_files(log, files_to_remove_list)
            remove_empty_folders(log, data_dir)

        except Exception as err:
            log.error(f'{str(err)}')

        finally:
            # close imap connection
            imap_connection.close_conection()
            timer = 0
            while active and timer < int(config["SETTINGS"]["timer"]):
                timer = timer + 1
                sleep(1)

    # clean up on exit
    log.info('Exiting...')
    sys.exit(0)


if __name__ == "__main__":
    active = True
    start()
