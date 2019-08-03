import logging
import socket
import os
import random

ACCOUNTS = [
    ('belleprince1206', '123456xom'),
]

# need to add accounts here for vm to deploy tasks that need logging-in
ACCOUNTS_FOR_VMS = {
    'crawl-data-42': {
        'gmail_account': 'country.roadtrip.song',
        'ins_account': 'country.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-14': {
        'gmail_account': 'hu.roadtrip',
        'ins_account': 'hu.roadtripp',
            'ins_password': 'XoXo123456'
    },
    'crawl-data-15': {
        'gmail_account': 'nice .roadtrip.song',
        'ins_account': 'nice.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-16': {
        'gmail_account': 'soft.roadtrip.song',
        'ins_account': 'soft.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-6': {
        'gmail_account': 'dubstep.roadtrip.song',
        'ins_account': 'dubstep.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-13': {
        'gmail_account': 'pop.roadtrip.song',
        'ins_account': 'pop.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-30': {
        'gmail_account': 'krom.raccoon',
        'ins_account': 'krom.raccoon',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-26': {
        'gmail_account': 'envyearth1206',
        'ins_account': 'environment1206',
        'ins_password': '123456xom'
    },
    'crawl-data-28': {
        'gmail_account': 'moviegrace',
        'ins_account': 'moviegrace',
        'ins_password': '123456xom'
    },
    'crawl-data-29': {
        'gmail_account': 'environment1206',
        'ins_account': 'environment1206',
        'ins_password': '123456xom'
    },
    'crawl-data-27': {
        'gmail_account': 'house.roadtrip.song',
        'ins_account': 'house.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-22': {
        'gmail_account': 'krom.analytica',
        'ins_account': 'krom.analytica',
        'ins_password': '123456xom'
    },
    'crawl-data-25': {
        'gmail_account': 'duykrom',
        'ins_account': 'duykrom',
        'ins_password': 'duykrom123'
    },
    'crawl-data-31': {
        'gmail_account': 'krom.polarbear',
        'ins_account': 'krom.polarbear',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-32': {
        'gmail_account': 'krom.snowleopard',
        'ins_account': 'krom.snowleopard',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-33': {
        'gmail_account': 'krom.reindeer',
        'ins_account': 'krom.reindeer',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-34': {
        'gmail_account': 'krom.penguin',
        'ins_account': 'krom.penguin',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-37': {
        'gmail_account': 'krom.zebra',
        'ins_account': 'krom.zebra',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-36': {
        'gmail_account': 'krom.chimpanzee',
        'ins_account': 'krom.chimpanzee',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-21': {
        'gmail_account': 'cool.roadtrip.song',
        'ins_account': 'cool.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-23': {
        'gmail_account': 'sing.roadtrip.song',
        'ins_account': 'sing.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-24': {
        'gmail_account': 'thongkrom7813',
        'ins_account': 'thongkrom7813',
        'ins_password': 'thongkrom123'
    },
    'crawl-data-1': {
        'gmail_account': 'uranium.analytica',
        'ins_account': 'uranium.analytica',
        'ins_password': '123456xom'
    },
    'crawl-data-38': {
        'gmail_account': 'krom.anaconda',
        'ins_account': 'krom.anaconda',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-35': {
        'gmail_account': 'krom.giraffe',
        'ins_account': 'krom.giraffe',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-3': {
        'gmail_account': 'rock.roadtrip.song',
        'ins_account': 'rock.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-5': {
        'gmail_account': 'best.roadtrip.song',
        'ins_account': 'best.roadtrip.song',
        'ins_password': 'XoXo123456'
    },
    'crawl-data-4': {
        'gmail_account': 'mercury.analytica',
        'ins_account': 'mercury.analytica',
        'ins_password': '123456xom'
    },
    'crawl-data-39': {
        'gmail_account': 'techguy1206',
        'ins_account': 'techguy1206',
        'ins_password': '123456xom'
    },
    'crawl-data-20': {
        'gmail_account': 'hippo.krom',
        'ins_account': 'hippo.krom',
        'ins_password': 'XoXo123456'
    },
    'MBP.local': {
        'gmail_account': 'techguy1206',
        'ins_account': 'techguy1206',
        'ins_password': '123456xom'
    },
    'Macintoshs-MacBook-Pro.local': {
        'gmail_account': 'techguy1206',
        'ins_account': 'techguy1206',
        'ins_password': '123456xom'
    },
}
NUM_ACCOUNTS = len(ACCOUNTS)


def get_account(idx=None):
    idx = idx if idx is not None else random.randint(0, NUM_ACCOUNTS - 1)
    return ACCOUNTS[idx]


def get_account_for_vm():
    vm_name = socket.gethostname()
    credentials = ACCOUNTS_FOR_VMS.get(vm_name, {})
    return credentials


def get_account_from_env():
    username = os.environ.get('INS_ACCOUNT')
    password = os.environ.get('INS_PASSWORD')
    return username, password


def check_if_accounts_are_available():
    from xde.crawling.instagram.web import InstagramWebApi
    from xde.crawling.instagram.web import InstagramError

    api = InstagramWebApi()
    for username, password in ACCOUNTS:
        try:
            api.login(username, password)
            logging.info('(%s/%s)-> OK' % (username, password))
            api.logout()
        except InstagramError as e:
            logging.error(e)


if __name__ == '__main__':
    check_if_accounts_are_available()
