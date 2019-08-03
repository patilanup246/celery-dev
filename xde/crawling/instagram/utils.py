# -*- coding: utf-8 -*-
import re
import datetime

HASHTAG_PATTERN = re.compile("(?:^|\s)[＃#]{1}(\w+)", re.UNICODE)


def extract_hashtags(text):
    if text:
        return HASHTAG_PATTERN.findall(text)
    return []


def datetime_from_timestamp(timestamp):
    try:
        return datetime.datetime.utcfromtimestamp(
            int(timestamp)
        )
    except ValueError:
        return None


def check_not_empty(reference, message=None):
    if not reference:
        raise ValueError(message or 'Empty value.')
    return reference


def extract_shortcode(link):
    pattern = r'(instagram\.com/p/)([A-Za-z_\-\d]+)/?'
    shortcode = re.search(pattern, link)
    if shortcode:
        return shortcode.group(2)


def extract_username_from_url(link):
    pattern = r'(instagram\.com|twitter\.com)\/([a-z._\d]{2,})(/?$)'
    username = re.search(pattern, link, flags=re.IGNORECASE)
    if username:
        return username.group(2)


def extract_number_from_text(text):
    if text:
        text = text.replace(',', '')
        number = re.search(r'\d{1,}', text)
        if number:
            return int(number.group())