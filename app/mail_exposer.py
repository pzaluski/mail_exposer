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
    pidfile=daemon.pidfile.PIDLockFile(config['SETTINGS']['pidfile']),
    umask=0o002
)

# SIGHUP	1	Hang up detected on controlling terminal or death of controlling process
# SIGINT	2	Issued if the user sends an interrupt signal (Ctrl + C)
# SIGQUIT	3	Issued if the user sends a quit signal (Ctrl + D)
# SIGKILL	9	If a process gets this signal it must quit immediately and will not perform any clean-up operations
# SIGTERM	15	Software termination signal (sent by kill by default)

signal_map = {
    signal.SIGTERM: exit_gracefully,    
    signal.SIGINT: exit_gracefully,
    signal.SIGQUIT: exit_gracefully,
    signal.SIGHUP: exit_gracefully
}
context.signal_map = signal_map

context.gid = grp.getgrnam('mail').gr_gid
context.uid = getpwnam('root').pw_uid

with context:
    start()
