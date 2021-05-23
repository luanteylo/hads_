from control.config.config import Config


class DebugConfig(Config):
    _key = 'debug'

    @property
    def debug_mode(self):
        return self.get_boolean(self._key, 'debug_mode')

