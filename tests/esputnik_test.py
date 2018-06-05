import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging
import requests
from requests.auth import HTTPBasicAuth

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

    ESPUTNIK_EMAIL = os.getenv('ESPUTNIK_EMAIL', '')
    ESPUTNIK_PASSWORD = os.getenv('ESPUTNIK_PASSWORD', '')
    ESPUTNIK_ADDRESSBOOK_ID = os.getenv('ESPUTNIK_ADDRESSBOOK_ID', '')

    try:
        auth = HTTPBasicAuth(ESPUTNIK_EMAIL, ESPUTNIK_PASSWORD)
        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        url = 'https://esputnik.com/api/v1/contact'

        contact = {
            'firstName' : 'Rishat',
            'lastName' : 'Sharafiev2',
            'channels' : [
                {
                    'type' : 'email',
                    'value' : 'rishatsharafiev@ya.ru'
                },
            ],
            'groups': [
                {
                    'name': 'Users'
                }
            ],
            'fields': [
                {
                    'id': 79703,
                    'value': '1994-05-25'
                }
            ]
        }

        response = requests.post(url, auth=auth , headers=headers, json=contact)
        print(response.text)
    except Exception as e:
        logger.exception(str(e))

if __name__ == '__main__':
    main()
