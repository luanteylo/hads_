from control.config.config import Config


class FileSystemConfig(Config):
    _key = 'file_system'

    @property
    def type(self):
        return self.get_property(self._key, 'type')

    @property
    def device(self):
        return self.get_property(self._key, 'device')

    @property
    def size(self):
        return int(self.get_property(self._key, 'size'))

    @property
    def path(self):
        return self.get_property(self._key, 'path')
    @property
    def ebs_delete(self):
        return self.get_boolean(self._key, 'ebs_delete')






