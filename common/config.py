import json
import os
from kivy.config import Config as kivy_config


def singleton(cls):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class Config(object):
    def __init__(self, config_name=''):
        self.config_name = os.path.join('tmp', config_name)
        kivy_config.read(self.config_name)
        self.section = 'shDefault'
        kivy_config.adddefaultsection(self.section)

    def change_section(self, section):
        self.section = section
        kivy_config.adddefaultsection(self.section)

    def save(self):
        kivy_config.write()

    def get(self, key, default=None):
        return kivy_config.getdefault(self.section, key, default)

    def set_val(self, key, value):
        kivy_config.set(self.section, key, value)
        kivy_config.write()