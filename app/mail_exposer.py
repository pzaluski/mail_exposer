#!/usr/bin/python3

import grp
import signal
import daemon
import daemon.pidfile
from pwd import getpwnam
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

context.gid = grp.getgrnam('mail_exposer').gr_gid
context.uid = getpwnam('root').pw_uid

with context:
    start()
