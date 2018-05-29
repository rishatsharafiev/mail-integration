import os
from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DOTENV_PATH = os.path.join(BASE_PATH, '.env')
load_dotenv(DOTENV_PATH)

import logging
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

    try:
        SPApiProxy = PySendPulse(SENDPULSE_REST_API_ID, SENDPULSE_REST_API_SECRET, SENDPULSE_TOKEN_STORAGE)
        emails_for_add = [
            {
                'email': 'test1@test1.com',
                'variables': {
                    'name': '232332',
                    'number': '11'
                }
            },
            {'email': 'test2@test2.com'},
            {
                'email': 'test3@test3.com',
                'variables': {
                    'firstname': 'test33',
                    'age': 33,
                    'date': '2015-09-30'
                }
            }
        ]
        SPApiProxy.add_emails_to_addressbook(SENDPULSE_ADDRESSBOOK_ID, emails_for_add)
    except Exception as e:
        logger.exception(str(e))

if __name__ == '__main__':
    main()
