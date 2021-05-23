from control.config.config import Config

import os


class NotifyConfig(Config):
    _key = 'notify'

    def __init__(self, path=None, file_name=None):
        self.pwd = None
        try:
            self.pwd = os.environ['NOTIFY_PWD']
        except Exception as e:
            print("NotifyConfig: env var NOTIFY_PWD not found.")

        super().__init__(path, file_name)

    @property
    def dest_mail(self):
        return self.get_property(self._key, 'dest_mail')

    @property
    def src_mail(self):
        return self.get_property(self._key, 'src_mail')

    @property
    def pwd_mail(self):
        return self.pwd
