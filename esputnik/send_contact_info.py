# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging
import pyodbc
import json
import requests
from requests.auth import HTTPBasicAuth
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
    ESPUTNIK_GROUP_CONTACT_INFO = os.getenv('ESPUTNIK_GROUP_CONTACT_INFO', '')
    ESPUTNIK_FIELD_CREATED_AT=os.getenv('ESPUTNIK_FIELD_CREATED_AT', '')
    ESPUTNIK_FIELD_LAST_MEETING=os.getenv('ESPUTNIK_FIELD_LAST_MEETING', '')
    ESPUTNIK_FIELD_LAST_CALL=os.getenv('ESPUTNIK_FIELD_LAST_CALL', '')
    ESPUTNIK_FIELD_NAME=os.getenv('ESPUTNIK_FIELD_NAME', '')


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
        post_url = 'https://esputnik.com/api/v1/contact'
        put_url = 'https://esputnik.com/api/v1/contact/{contact_id}'

        with MSSQL_DATABASE_CONNECTION:
            """
                -- Create table before

                CREATE TABLE [a2profile_fh].[dbo].[tSputnikContactInfo] (
                    ID int NOT NULL IDENTITY(1,1),
                    ContactID varchar(255) NOT NULL,
                    Email varchar(255),
                    PRIMARY KEY (ID),
                );
            """

            MSSQL_DATABASE_CURSOR.execute("\
                SELECT MAX([ContactID]), [Email] AS [ContactID] \
                FROM [a2profile_fh].[dbo].[tSputnikContactInfo] \
                GROUP BY [Email];"
            )


            updated_contacts = {}

            for row in MSSQL_DATABASE_CURSOR.fetchall():
                contact_id = row[0] or ''
                email = row[1] or ''

                updated_contacts[email] = contact_id

            MSSQL_DATABASE_CURSOR.execute("\
                SELECT DISTINCT [Дата создания] \
                  ,[Имя] \
                  ,[Номер] \
                  ,[Электронная почта] \
                  ,[Последняя встреча] \
                  ,[Последний звонок] \
                  ,[Название] \
                  ,[ContactTS] \
                FROM [a2profile_fh].[dbo].[tGetContactInfo] \
                WHERE [Электронная почта] IS NOT NULL AND [Электронная почта] != ''"
            )

            emails_for_add = []

            for row in MSSQL_DATABASE_CURSOR.fetchall():
                if row[0]:
                    created_at = row[0].strftime('%Y-%m-%d')
                else:
                    created_at = ''

                if row[1]:
                    first_name = row[1].split('-')[0].capitalize() or ''
                else:
                    first_name = ''

                number = row[2] or ''

                email = row[3] or ''

                if row[4]:
                    last_meeting = row[4].strftime('%Y-%m-%d')
                else:
                    last_meeting = ''

                if row[5]:
                    last_call = row[5].strftime('%Y-%m-%d')
                else:
                    last_call = ''

                name = row[6] or ''

                if email:
                    fields = []
                    if created_at:
                        fields.append({
                            'id': ESPUTNIK_FIELD_CREATED_AT,
                            'value': created_at,
                        })
                    if last_meeting:
                        fields.append({
                            'id': ESPUTNIK_FIELD_LAST_MEETING,
                            'value': last_meeting,
                        })
                    if last_call:
                        fields.append({
                            'id': ESPUTNIK_FIELD_LAST_CALL,
                            'value': last_call,
                        })
                    if name:
                        fields.append({
                            'id': ESPUTNIK_FIELD_NAME,
                            'value': name,
                        })


                    contact = {
                        'firstName' : first_name,
                        'channels' : [
                            {
                                'type' : 'email',
                                'value' : email,
                            },
                        ],
                        'groups': [
                            {
                                'name': ESPUTNIK_GROUP_CONTACT_INFO,
                            }
                        ],
                        'fields': fields
                    }

                    if email in updated_contacts:
                        response = requests.put(put_url.format(updated_contacts[email], auth=auth , headers=headers, json=contact))
                    else:
                        response = requests.post(post_url, auth=auth , headers=headers, json=contact)
                        if response.status_code == 200:
                            response = json.loads(response.text)
                            if 'id' in response:
                                MSSQL_DATABASE_CURSOR.execute("\
                                    INSERT INTO [a2profile_fh].[dbo].[tSputnikContactInfo] \
                                        ([ContactID] \
                                        ,[Email]) \
                                    VALUES \
                                        (?, ?);",
                                    response['id'],
                                    email
                                )
                                MSSQL_DATABASE_CONNECTION.commit()
    except Exception as e:
        logger.exception(str(e))

if __name__ == '__main__':
    main()
