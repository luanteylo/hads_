from control.config.config import Config


class SchedulerConfig(Config):
    _key = 'scheduler'

    @property
    def path(self):
        return self.get_property(self._key, 'path')

    @property
    def name(self):
        return self.get_property(self._key, 'name')

    @property
    def burstable_factor(self):
        return float(self.get_property(self._key, 'burstable_factor'))

    @property
    def alpha(self):
        return float(self.get_property(self._key, 'alpha'))

    @property
    def max_iteration(self):
        return int(self.get_property(self._key, 'max_iteration'))

    @property
    def status_update_time(self):
        return float(self.get_property(self._key, 'status_update_time'))

    @property
    def allow_parallel_execution(self):
        return self.get_boolean(self._key, 'allow_parallel_execution')
