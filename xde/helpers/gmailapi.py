from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import re
import time
from os.path import join, dirname
from xde.helpers.logger import get_logger

_logger = get_logger(__name__)

CONFIG_DIR = join(dirname(__file__), 'config/gmailapi')


class GmailApi:
    def __init__(self, credentials=None, client_secret=None, max_retry=30, delay=10, scopes='modify', user_id='me'):
        scopes = 'https://www.googleapis.com/auth/gmail.%s' % scopes
        store = file.Storage(join(CONFIG_DIR, credentials))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(join(CONFIG_DIR, client_secret), scopes)
            creds = tools.run_flow(flow, store)
        self.gmail = discovery.build('gmail', 'v1', http=creds.authorize(Http()))
        self.user_id = user_id
        self._max_retry = max_retry
        self._delay = delay

    @staticmethod
    def extract_code(snippet):
        pattern = r'(?<=(identity:\s))\d{6}'
        code = re.search(pattern=pattern, string=snippet)
        return code.group() if code else None

    def get_unread_msgs(self):
        retry = 0
        label_id_one = 'INBOX'
        label_id_two = 'UNREAD'
        while True:
            unread_msgs = self.gmail.users().messages().list(
                userId='me', labelIds=[label_id_one, label_id_two],
                q='from:security@mail.instagram.com after:%s' % datetime.datetime.strftime(datetime.datetime.now(),
                                                                                           "%Y/%m/%d")).execute()
            if unread_msgs['resultSizeEstimate'] > 0:
                return unread_msgs['messages']
            retry += 1
            if retry == self._max_retry:
                _logger.error("Max retry exceeded!")
                return []
            time.sleep(self._delay)

    def get_codes(self):
        _logger.info('Waiting for security code...')
        codes = []
        msgs = self.get_unread_msgs()
        for msg in msgs:
            m_id = msg['id']
            message = self.gmail.users().messages().get(userId=self.user_id, id=m_id).execute()
            code = self.extract_code(message['snippet'])
            if code:
                codes.append({'code': code, 'm_id': m_id})
        return codes

    def mark_as_read(self, m_id):
        self.gmail.users().messages().modify(userId=self.user_id, id=m_id, body={'removeLabelIds': ['UNREAD']}).execute()


if __name__ == '__main__':
    codes = GmailApi(credentials='/Users/duc/xomad-de/xde/analytics/helpers/config/gmailapi/dubstep.roadtrip.song_credentials.json').get_codes()
