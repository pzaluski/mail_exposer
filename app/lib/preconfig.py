import os
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


    @cfg.setter
    def cfg(self, config):
        self._cfg = config

