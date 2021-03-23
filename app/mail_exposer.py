#!/usr/bin/python3

import os
import grp
import signal
from threading import active_count
import daemon
import daemon.pidfile
from main import start, exit_gracefully
from lib.preconfig import Preconfig


preconfig = Preconfig()
config = preconfig.cfg

context = daemon.DaemonContext(
    working_directory=config['SETTINGS']['working_dir'],
    pidfile=daemon.pidfile.PIDLockFile('/var/run/mail_exposer.pid'),
    umask=0o002
)


signal_map = {
    signal.SIGTERM: exit_gracefully,
    signal.SIGHUP: exit_gracefully,
    signal.SIGTSTP: exit_gracefully
}
context.signal_map = signal_map

mail_gid = grp.getgrnam('mail').gr_gid
context.gid = mail_gid

with context:
    start()
