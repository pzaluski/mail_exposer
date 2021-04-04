import os
import logging
from configparser import ConfigParser, ExtendedInterpolation


class Preconfig():
    def __init__(self):
        configfile = '../config/config.ini'
        config = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), configfile)
        self._cfg = ConfigParser(interpolation=ExtendedInterpolation())
        self._cfg.read(config)

    @property
    def cfg(self):
        return self._cfg


class Logger():
    def __init__(self, config):
        self.logfile = config['SETTINGS']['logfile']
        self.loglevel = config['SETTINGS']['loglevel']
        self._logger = logging.getLogger()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler = logging.FileHandler(self.logfile)
        handler.setFormatter(formatter)
        self._logger.setLevel(self.loglevel)
        self._logger.addHandler(handler)

    @property
    def log(self):
        return self._logger

