from control.config.config import Config


class CheckPointConfig(Config):
    _key = 'checkpoint'

    @property
    def with_checkpoint(self):
        return self.get_boolean(self._key, 'with_checkpoint')

    @property
    def formulation(self):
        return self.get_property(self._key, 'formulation')

    @property
    def period(self):
        return float(self.get_property(self._key, 'period'))

    @property
    def overhead_factor(self):
        return float(self.get_property(self._key, 'overhead_factor'))




