from control.config.config import Config


class DockerConfig(Config):
    _key = 'docker'

    @property
    def docker_image(self):
        return self.get_property(self._key, 'docker_image')

    @property
    def work_dir(self):
        return self.get_property(self._key, 'work_dir')
