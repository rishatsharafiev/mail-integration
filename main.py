import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging
import pyodbc
from pysendpulse.pysendpulse import PySendPulse

### logger
logger = logging.getLogger(__name__)
logger_handler = logging.FileHandler(os.path.join(BASE_PATH, '{}.log'.format(__file__)))
logger_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)
logger.setLevel(logging.WARNING)

# logger.error('We have a problem')
# logger.info('While this is just chatty')

def main():

    SENDPULSE_REST_API_ID = os.getenv('SENDPULSE_REST_API_ID', '')
    SENDPULSE_REST_API_SECRET = os.getenv('SENDPULSE_REST_API_SECRET', '')
    SENDPULSE_TOKEN_STORAGE = os.getenv('SENDPULSE_TOKEN_STORAGE', 'memcached')
    SENDPULSE_ADDRESSBOOK_ID = os.getenv('SENDPULSE_ADDRESSBOOK_ID', '')

    MSSQL_DRIVER = os.getenv('MSSQL_DRIVER', '{FreeTDS}')
    MSSQL_TDS_VERSION = os.getenv('MSSQL_TDS_VERSION', 8.0)
    MSSQL_SERVER = os.getenv('MSSQL_SERVER')
    MSSQL_PORT = os.getenv('MSSQL_PORT', 1433)
    MSSQL_DATABASE = os.getenv('MSSQL_DATABASE')
    MSSQL_UID = os.getenv('MSSQL_UID')
    MSSQL_PWD = os.getenv('MSSQL_PWD')

    MSSQL_CONNECTION_STRING = 'DRIVER={DRIVER};' \
        'SERVER={SERVER};' \
        'PORT={PORT};' \
        'DATABASE={DATABASE};' \
        'UID={UID};' \
        'PWD={PWD};' \
        'TDS_Version={TDS_VERSION};'.format(
        DRIVER=MSSQL_DRIVER,
        TDS_VERSION=MSSQL_TDS_VERSION,
        SERVER=MSSQL_SERVER,
        PORT=MSSQL_PORT,
        DATABASE=MSSQL_DATABASE,
        UID=MSSQL_UID,
        PWD=MSSQL_PWD,
    )

    MSSQL_DATABASE_CONNECTION = pyodbc.connect(MSSQL_CONNECTION_STRING)

    MSSQL_DATABASE_CURSOR = MSSQL_DATABASE_CONNECTION.cursor()


    try:
        SPApiProxy = PySendPulse(SENDPULSE_REST_API_ID, SENDPULSE_REST_API_SECRET, SENDPULSE_TOKEN_STORAGE)

        with MSSQL_DATABASE_CONNECTION:
            MSSQL_DATABASE_CURSOR.execute('\
                SELECT [Номер анкеты] AS questionary_id \
                    ,[Дата создания] AS create_at \
                    ,[Фамилия] AS surname \
                    ,[Имя] AS first_name \
                    ,[Отчество] AS second_name \
                    ,[Дата рождения] AS birth_date \
                    ,[Пол.Название] AS sex \
                    ,[Электронная почта] AS email \
                    ,[Основной телефон.Номер] AS phone \
                    ,[Первый звонок] AS first_call \
                    ,[Последний звонок] AS last_call \
                    ,[Первая встреча] AS first_meeting \
                    ,[Последняя встреча] AS last_meeting \
                    ,[TS] \
                FROM [a2profile_fh].[dbo].[tGetClientInfo]'
            )
            for row in MSSQL_DATABASE_CURSOR.fetchall():
                print(row)

            # SPApiProxy.add_emails_to_addressbook(SENDPULSE_ADDRESSBOOK_ID, emails_for_add)
    except Exception as e:
        logger.exception(str(e))

if __name__ == '__main__':
    main()
