from sqlalchemy import create_engine
from control.repository.postgres_objects import Base
from sqlalchemy.orm import sessionmaker

from control.config.database_config import DataBaseConfig

import logging


class RecreateDatabase:

    @staticmethod
    def execute():
        conf = DataBaseConfig()

        logging.info('Recreating database {}...'.format(conf.database_name))

        DATABASE_URI = 'postgres+psycopg2://postgres:{}@{}:5432/{}'.format(
            conf.password,
            conf.host,
            conf.database_name
        )

        engine = create_engine(DATABASE_URI)

        Session = sessionmaker(bind=engine)
        s = Session()

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        s.close()
