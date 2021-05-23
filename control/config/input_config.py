from control.config.config import Config


class InputConfig(Config):
    _key = 'input'

    @property
    def path(self):
        return self.get_property(self._key, 'path')

    @property
    def job_file(self):
        return self.get_property(self._key, 'job_file')

    @property
    def env_file(self):
        return self.get_property(self._key, 'env_file')

    @property
    def map_file(self):
        return self.get_property(self._key, 'map_file')

    @property
    def deadline_seconds(self):
        return float(self.get_property(self._key, 'deadline_seconds'))

    @property
    def ac_size_seconds(self):
        return float(self.get_property(self._key, 'ac_size_seconds'))

    @property
    def idle_slack_time(self):
        return float(self.get_property(self._key, 'idle_slack_time'))
