from control.config.config import Config


class SimulationConfig(Config):
    _key = 'simulation'

    @property
    def with_simulation(self):
        return self.get_boolean(self._key, 'with_simulation')

    @property
    def revocation_rate(self):
        return float(self.get_property(self._key, 'revocation_rate'))

    @property
    def resume_rate(self):
        return float(self.get_property(self._key, 'resume_rate'))

    @property
    def sim_type(self):
        return self.get_property(self._key, 'sim_type')
