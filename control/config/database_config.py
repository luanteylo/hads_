from control.config.config import Config

import os


class DataBaseConfig(Config):
    _key = 'database'

    def __init__(self, path=None, file_name=None):
        self.pwd = None
        self.user_name = None
        try:
            self.pwd = os.environ['POSTGRES_PASS']
        except Exception as e:
            print("DatabaseConfig: env var POSTGRES_PASS not found.")
            raise e

        try:
            self.user_name = os.environ['POSTGRES_USER']
        except Exception as e:
            print("DatabaseConfig: env var POSTGRES_USER not found.")
            raise e

        super().__init__(path, file_name)

    @property
    def user(self):
        return self.user_name

    @property
    def password(self):
        return self.pwd

    @property
    def host(self):
        return self.get_property(self._key, 'host')

    @property
    def database_name(self):
        return self.get_property(self._key, 'database_name')

    @property
    def dump_dir(self):
        return self.get_property(self._key, 'dump_dir')

    @property
    def with_dump(self):
        return self.get_boolean(self._key, 'with_dump')
