import configparser
from pathlib import Path
import os


class EnvInterpolation(configparser.BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        return os.path.expandvars(value)


class Config(object):
    def __init__(self, path=None, file_name=None):

        if path is None:
            path = os.environ['SETUP_PATH']

        if file_name is None:
            file_name = os.environ['SETUP_FILE']

        self.file_name = Path(path + file_name)

        if self.file_name.is_file() is False:
            raise FileNotFoundError

        if self.file_name.suffix != '.cfg':
            raise Exception('invalid file format')

        self._config = configparser.ConfigParser(interpolation=EnvInterpolation())
        self._config.read(self.file_name)

    def get_property(self, key, name):

        if key in self._config and name in self._config[key]:
            return self._config[key][name]
        else:
            return None

    def get_boolean(self, key, name):
        if key in self._config and name in self._config[key]:
            return self._config.getboolean(key, name)
