from control.config.config import Config


class LoggingConfig(Config):
    _key = 'logging'

    @property
    def path(self):
        return self.get_property(self._key, 'path')

    @property
    def log_file(self):
        return self.get_property(self._key, 'log_file')

    @property
    def level(self):
        return self.get_property(self._key, 'level')
