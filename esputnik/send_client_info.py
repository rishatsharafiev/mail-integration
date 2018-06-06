# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging
import pyodbc
import json
from pysendpulse.pysendpulse import PySendPulse
from datetime import datetime

### logger
logger = logging.getLogger(__name__)
logger_handler = logging.FileHandler(os.path.join(BASE_PATH, '{}.log'.format(__file__)))
logger_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)
logger.setLevel(logging.WARNING)
logger.propagate = False

# logger.error('We have a problem')
# logger.info('While this is just chatty')

def main():

    ESPUTNIK_EMAIL = os.getenv('ESPUTNIK_EMAIL', '')
    ESPUTNIK_PASSWORD = os.getenv('ESPUTNIK_PASSWORD', '')
    ESPUTNIK_GROUP_CLIENT_INFO = os.getenv('ESPUTNIK_GROUP_CLIENT_INFO', '')
    ESPUTNIK_FIELD_PHONE=os.getenv('ESPUTNIK_FIELD_PHONE', '')
    ESPUTNIK_FIELD_CREATED_AT=os.getenv('ESPUTNIK_FIELD_CREATED_AT', '')
    ESPUTNIK_FIELD_BIRTH_DATE=os.getenv('ESPUTNIK_FIELD_BIRTH_DATE', '')
    ESPUTNIK_FIELD_SEX=os.getenv('ESPUTNIK_FIELD_SEX', '')
    ESPUTNIK_FIELD_FIRST_CALL=os.getenv('ESPUTNIK_FIELD_FIRST_CALL', '')
    ESPUTNIK_FIELD_LAST_CALL=os.getenv('ESPUTNIK_FIELD_LAST_CALL', '')


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
        auth = HTTPBasicAuth(ESPUTNIK_EMAIL, ESPUTNIK_PASSWORD)
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        url = 'https://esputnik.com/api/v1/contact/{contact_id}'

        with MSSQL_DATABASE_CONNECTION:
            """
                -- Create table before

                CREATE TABLE [a2profile_fh].[dbo].[tSputnikClientInfo] (
                    ID int NOT NULL IDENTITY(1,1),
                    ContactID varchar(255) NOT NULL,
                    Email varchar(255),
                    PRIMARY KEY (ID),
                );
            """

            MSSQL_DATABASE_CURSOR.execute("\
                SELECT DISTINCT [ID] \
                    ,[ContactID] \
                    ,[Email] \
                FROM [a2profile_fh].[dbo].[tSputnikClientInfo]"
            )


            updated_contacts = []

            for row in MSSQL_DATABASE_CURSOR.fetchall():
                contact_id = row[0] or ''
                email = row[1] or ''

                updated_contacts.append({
                    'contact_id': contact_id,
                    'email': email
                })

            updated_contacts_email = [contact['email'] for contact in updated_contacts]

            MSSQL_DATABASE_CURSOR.execute("\
                SELECT DISTINCT [Номер анкеты] AS form_id \
                    ,[Дата создания] AS created_at \
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
                    ,[TS] AS ts \
                FROM [a2profile_fh].[dbo].[tGetClientInfo] \
                WHERE [Электронная почта] IS NOT NULL AND [Электронная почта] != ''"
            )

            emails_for_add = []

            for row in MSSQL_DATABASE_CURSOR.fetchall():
                form_id = row[0] or ''
                if row[1]:
                    created_at = row[1].strftime('%Y-%m-%d')
                else:
                    created_at = ''

                if row[2]:
                    surname = row[2].split('-')[0].capitalize() or ''
                else:
                    surname = ''

                if row[3]:
                    first_name = row[3].split('-')[0].capitalize() or ''
                else:
                    first_name = ''

                if row[4]:
                    second_name = row[4].split('-')[0].capitalize() or ''
                else:
                    second_name = ''

                if row[5]:
                    birth_date = row[5].strftime('%Y-%m-%d')
                else:
                    birth_date = ''

                sex = row[6] or ''
                email = row[7] or ''
                phone = row[8] or ''

                if row[9]:
                    first_call = row[9].strftime('%Y-%m-%d')
                else:
                    first_call = ''

                if row[10]:
                    last_call = row[10].strftime('%Y-%m-%d')
                else:
                    last_call = ''

                if row[11]:
                    first_meeting = row[11].strftime('%Y-%m-%d')
                else:
                    first_meeting = ''

                if row[12]:
                    last_meeting = row[12].strftime('%Y-%m-%d')
                else:
                    last_meeting = ''

                ts = row[13] or ''

                if email:
                    contact = {
                        'firstName' : first_name,
                        'lastName' : surname,
                        'channels' : [
                            {
                                'type' : 'email',
                                'value' : email,
                            },
                        ],
                        'groups': [
                            {
                                'name': ESPUTNIK_GROUP_CLIENT_INFO,
                            }
                        ],
                        'fields': [
                            {
                                'id': ESPUTNIK_FIELD_PHONE,
                                'value': phone,
                            },
                            {
                                'id': ESPUTNIK_FIELD_CREATED_AT,
                                'value': created_at,
                            },
                            {
                                'id': ESPUTNIK_FIELD_BIRTH_DATE,
                                'value': birth_date,
                            },
                            {
                                'id': ESPUTNIK_FIELD_SEX,
                                'value': sex,
                            },
                            {
                                'id': ESPUTNIK_FIELD_FIRST_CALL,
                                'value': first_call,
                            },
                            {
                                'id': ESPUTNIK_FIELD_LAST_CALL,
                                'value': last_call,
                            },
                        ]
                    }

                    contact_ids = [contact['contact_id'] for contact in updated_contacts if contact['email'] == email]
                    if email in updated_contacts_email and len(contact_ids) > 0:
                        response = requests.put(url.format(contact_ids[0], auth=auth , headers=headers, json=contact))
                    else:
                        response = requests.post(url, auth=auth , headers=headers, json=contact)
                        response = json.load(response.text)
                        if 'id' in response:
                            MSSQL_DATABASE_CURSOR.execute("\
                                INSERT INTO [dbo].[tSputnikClientInfo] \
                                    ([ContactID] \
                                    ,[Email]) \
                                VALUES \
                                    (?, ?);",
                                response['id'],
                                email
                            )
    except Exception as e:
        logger.exception(str(e))

if __name__ == '__main__':
    main()
