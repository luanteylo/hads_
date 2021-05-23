from control.config.config import Config


class ApplicationConfig(Config):
    _key = 'application'

    @property
    def app_local_path(self):
        return self.get_property(self._key, 'app_local_path')

    @property
    def daemon_path(self):
        return self.get_property(self._key, 'daemon_path')

    @property
    def daemon_file(self):
        return self.get_property(self._key, 'daemon_file')
