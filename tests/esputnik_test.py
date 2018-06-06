import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging
import requests
import json
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

        contact = {'firstName': 'Ольга', 'lastName': 'Осипова', 'channels': [{'type': 'email', 'value': 'happyolga82@gmail.com'}], 'groups': [{'name': 'client_info'}], 'fields': [{'id': '79735', 'value': '9253070445'}, {'id': '79736', 'value': '2014-12-02'}, {'id': '79737', 'value': '1982-05-30'}, {'id': '79738', 'value': 'Женский'}, {'id': '79739', 'value': '2014-12-03'}, {'id': '79740', 'value': '2017-06-20'}]}

        response = requests.post(url, auth=auth , headers=headers, json=contact)
        print(json.loads(response.text)['id'])
        print(response.status_code)
    except Exception as e:
        logger.exception(str(e))

if __name__ == '__main__':
    main()
