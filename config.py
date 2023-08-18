from configparser import ConfigParser
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def config(filename='base.ini', section='postgresql'):
    """
    Парсим наш ini файл и возвращаем словарь данных конфига
    """
    parser = ConfigParser()
    parser.read(filename)

    config_data = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config_data[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config_data


def make_db_connect():
    """
    Подключение к БД, создание сессии и таблицы
    """
    config_info = config(filename='base.ini', section='postgresql')

    host = config_info.get('host')
    database_name = config_info.get('database')
    user = config_info.get('user')
    password = config_info.get('password')

    db_engine = create_engine('postgresql://{}:{}@{}/{}'.format(
        user, password, host, database_name)
    )

    session_local = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    base = declarative_base()
    base.metadata.create_all(bind=db_engine)
    return db_engine, session_local, base


engine, SessionLocal, Base = make_db_connect()
HOST_IP = config(section='my_api_service')
