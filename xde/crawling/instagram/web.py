import re
import random
import time
from os.path import join, dirname

import traceback
import requests
from bs4 import BeautifulSoup
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

from requestium import Session, Keys
import pickle

from xde.helpers.gmailapi import GmailApi
from .utils import *

from xde.helpers.logger import get_logger

from .agents import random_agent
from .endpoints import *
from .utils import check_not_empty
from .elements import *


class InstagramError(Exception):
    def __init__(self, error_message=None, status_code=None, *args, **kwargs):
        super(InstagramError, self).__init__(*args, **kwargs)
        self.status_code = status_code
        self.error_message = error_message

    def __str__(self):
        if self.status_code:
            return '(%s) %s' % (self.status_code, self.error_message)
        return self.error_message


class InvalidCredentialError(InstagramError):
    def __init__(self, error_message='Invalid IG credentials'):
        super(InvalidCredentialError, self).__init__(error_message)


class PostUnavailableError(InstagramError):
    def __init__(self, error_message='Post is not available. Check post link.'):
        super(PostUnavailableError, self).__init__(error_message)


class SuggestedUsersNotFound(InstagramError):
    def __init__(self, error_message='Suggested users not found'):
        super(SuggestedUsersNotFound, self).__init__(error_message)


class RestrictedPostInLocationException(Exception):
    def __init__(self, error_message=None, status_code=None):
        super(RestrictedPostInLocationException, self).__init__(error_message)
        self.status_code = status_code
        self.error_message = error_message


class InstagramSession(requests.Session):
    DEFAULT_HEADERS = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.5',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'connection': 'keep-alive',
        'x-requested-with': 'XMLHttpRequest',
        'referer': BASE_URL,
        'host': HOST,
    }

    CSRF_TOKEN = 'csrftoken'
    X_CSRF_TOKEN = 'x-csrftoken'
    DEFAULT_REQUEST_TIMEOUT = 60

    _last_request_time = 0
    last_request_url = None

    def __init__(self, min_delayed_time=5, max_delayed_time=10):
        super(InstagramSession, self).__init__()
        self._min_delayed_time = min_delayed_time
        self._max_delayed_time = max_delayed_time
        self._logger = get_logger(self.__class__.__name__)

        # setup headers
        headers = self.DEFAULT_HEADERS.copy()
        headers['user-agent'] = random_agent()
        self.headers.update(headers)

    def request(self, *args, **kwargs):
        self._logger.info('%s with params %s' % (' '.join(args), kwargs))
        kwargs['timeout'] = kwargs.get('timeout', self.DEFAULT_REQUEST_TIMEOUT)
        self.last_request_url = args[1]

        self._delay_request_if_needed()
        r = super(InstagramSession, self).request(*args, **kwargs)
        self._last_request_time = time.time()
        self.raise_exception_for_status(r)

        self.headers.update({self.X_CSRF_TOKEN: self.cookies.get(self.CSRF_TOKEN)})

        return r

    def _delay_request_if_needed(self):
        delay = random.uniform(self._min_delayed_time, self._max_delayed_time)
        if delay > 0 and self._last_request_time > 0:
            d = time.time() - self._last_request_time
            if d < delay:
                sleep_time = delay - d
                self._logger.info('Wait for %ss...' % sleep_time)
                time.sleep(sleep_time)

    @staticmethod
    def raise_exception_for_status(response):
        code = response.status_code
        if code == 403:
            raise InstagramError('Forbidden', code)
        if code == 404:
            raise InstagramError('Page not found', code)
        if code in (503, 429):
            raise InstagramError('Too many requests', code)
        if code == 400:
            raise InstagramError('Bad request', code)
        if code != 200:
            raise InstagramError('Something went wrong', code)


class InstagramWebApi(object):
    _session = None
    _logged_in = False

    def __init__(self, min_delayed_time=5, max_delayed_time=10):
        self._min_delayed_time = min_delayed_time
        self._max_delayed_time = max_delayed_time
        self._logger = get_logger(self.__class__.__name__)
        self.new_session()

    def new_session(self):
        self._session = InstagramSession(self._min_delayed_time, self._max_delayed_time)
        self._logged_in = False

    def with_referer(self, referer):
        self._session.headers.update({'referer': referer})
        return self

    def _require_login(self):
        if not self._logged_in:
            raise InstagramError('login required!')

    def is_logged_in(self):
        return self._logged_in

    def login(self, username, password):
        check_not_empty(username)
        check_not_empty(password)
        self._logger.debug('Try to login with account %s/%s' % (username, password))
        self._session.get(BASE_URL)
        r = self._session.post(LOGIN_URL, data={'username': username, 'password': password}).json()
        if not r.get('authenticated'):
            self._logger.error("InvalidCredentialError: %s/%s" % (username, password))
            raise InvalidCredentialError()

        self._logged_in = True
        self._logger.debug('Login successfully')
        return self

    def logout(self):
        if self._logged_in:
            try:
                self._session.post(
                    url=LOGOUT_URL,
                    data={'csrfmiddlewaretoken': self._session.cookies.get(self._session.CSRF_TOKEN)}
                )
                self._logged_in = False
                self._logger.debug('Logout successfully')
            except Exception as e:
                self._logger.error(e)

    def get_user_by_username(self, username):
        return self.get_user_by_username_from_html(username)

    def get_user_by_username_from_html(self, username):
        r = self._session.get(ACCOUNT_HTML_INFO % check_not_empty(username))
        bs = BeautifulSoup(r.content, 'lxml')
        content_tag = bs.find('script', text=re.compile('window._sharedData*'))
        content_text = content_tag.text
        content_text = content_text.replace('window._sharedData = ', '')
        content_json = json.loads(content_text[:-1])
        profile_info = content_json.get('entry_data', {}).get('ProfilePage', {})
        return profile_info[0].get('graphql', {}).get('user')

    def get_user_medias_by_username_from_html(self, username):
        user = self.get_user_by_username_from_html(username)
        medias = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
        for media in medias:
            yield media.get('node')

    def get_user_by_id(self, user_id):
        # return self._session.post(QUERY_URL, data={'q': ACCOUNT_JSON_INFO_BY_ID % user_id}).json()
        headers = self._session.headers.copy()
        headers['host'] = MOBILE_HOST
        headers['user-agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'
        r = self._session.get(USER_INFO_BY_ID % user_id, headers=headers)
        content_text = r.content
        content_json = json.loads(content_text)
        return content_json.get('user')

    def get_user_medias_by_id(self, user_id, per_page=12, end_cursor=None):
        """Get the list of medias of a user."""
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        while page_info.get('has_next_page'):
            r = self._session.get(user_medias(user_id, first=per_page, after=page_info.get('end_cursor'))).json()
            edge = r.get('data', {}).get('user', {}).get('edge_owner_to_timeline_media', {})
            edges = edge.get('edges', [])
            if not edges:
                break
            for each in edges:
                yield each.get('node')
            page_info = edge.get('page_info', {})

    def get_user_followers(self, user_id, per_page=10, end_cursor=None):
        """ Get the list of users this user is followed by.
        Require login.
        """
        user_id = int(user_id)
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        while page_info.get('has_next_page'):
            r = self._session.get(user_followers(user_id, first=per_page, after=page_info.get('end_cursor'))).json()
            edge = r.get('data', {}).get('user', {}).get('edge_followed_by', {})
            for each in edge.get('edges', []):
                yield each.get('node')
            page_info = edge.get('page_info', {})

    def get_user_following(self, user_id, per_page=10, end_cursor=None):
        """ Get the list of users this user follows.
        Require login.
        """
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        user_id = int(user_id)
        while page_info.get('has_next_page'):
            r = self._session.get(user_following(user_id, first=per_page, after=page_info.get('end_cursor'))).json()
            edge = r.get('data', {}).get('user', {}).get('edge_follow', {})
            for each in edge.get('edges', []):
                yield each.get('node')
            page_info = edge.get('page_info', {})

    def get_user_stories(self, user_id):
        r = self._session.get(user_stories(ids=[user_id])).json()
        return r

    def get_media_by_code(self, shortcode):
        media_res = self._session.get(MEDIA_JSON_INFO % check_not_empty(shortcode))
        try:
            media = media_res.json()
        except:
            if RESTRICTED_POST_IN_LOCATION_MSG in media_res.content:
                raise RestrictedPostInLocationException(RESTRICTED_POST_IN_LOCATION_MSG)
            raise
        return media.get('graphql', {}).get('shortcode_media', {})

    def get_media_likes_by_code(self, shortcode, per_page=24, end_cursor=None):
        """Get a list of users who have liked this media."""
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        while page_info.get('has_next_page'):
            r = self._session.get(media_likes(shortcode, first=per_page, after=page_info.get('end_cursor'))).json()
            edge = r.get('data', {}).get('shortcode_media', {}).get('edge_liked_by', {})
            for each in edge.get('edges', []):
                yield each.get('node')
            page_info = edge.get('page_info', {})

    def get_media_comments_by_code(self, shortcode, per_page=100, end_cursor=None):
        """Get a list of comments of this media."""
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        while page_info.get('has_next_page'):
            r = self._session.get(media_comments(shortcode, first=per_page, after=page_info.get('end_cursor'))).json()
            edge = r.get('data', {}).get('shortcode_media', {}).get('edge_media_to_comment', {})
            for each in edge.get('edges', []):
                yield each.get('node')
            page_info = edge.get('page_info', {})

    def get_medias_by_tag(self, tag, per_page=12, end_cursor=None):
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        while page_info.get('has_next_page'):
            r = self._session.get(
                hashtag_medias(tag_name=tag, first=per_page, after=page_info.get('end_cursor'))
            ).json()
            edge = r.get('data', {}).get('hashtag', {}).get('edge_hashtag_to_media', {})
            for each in edge.get('edges', []):
                yield each.get('node')
            page_info = edge.get('page_info', {})

    def get_recent_medias_by_tag(self, tag, **kwargs):
        r = self._session.get(
            recent_hashtag_medias(tag_name=tag)
        ).json()
        edge = r.get('graphql', {}).get('hashtag', {}).get('edge_hashtag_to_media', {})
        for each in edge.get('edges', []):
            yield each.get('node')

    def get_medias_with_cursors_by_tag(self, tag, per_page=12, end_cursor=None):
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        while page_info.get('has_next_page'):
            r = self._session.get(
                hashtag_medias(tag_name=tag, first=per_page, after=page_info.get('end_cursor'))
            ).json()
            edge = r.get('data', {}).get('hashtag', {}).get('edge_hashtag_to_media', {})
            page_info = edge.get('page_info', {})
            for each in edge.get('edges', []):
                yield each.get('node'), page_info

    def count_medias_by_tag(self, tag):
        r = self._session.get(
            hashtag_medias(tag_name=tag, first=0)
        ).json()
        return r.get('data', {}).get('hashtag', {}).get('edge_hashtag_to_media', {}).get('count')

    def get_top_medias_by_tag(self, tag):
        r = self._session.get(
            hashtag_medias(tag_name=tag, first=0)
        ).json()
        edge = r.get('data', {}).get('hashtag', {}).get('edge_hashtag_to_top_posts', {})
        for each in edge.get('edges', []):
            yield each.get('node')

    def get_recent_medias_by_location(self, id, per_page=12, end_cursor=None):
        """ Get a list of medias from a given location id """
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        while page_info.get('has_next_page'):
            r = self._session.get(location_medias(id=id, first=per_page, after=page_info.get('end_curor'))).json()
            edge = r.get('data', {}).get('location', {}).get('edge_location_to_media', {})
            for each in edge.get('edges', []):
                yield each.get('node')
            page_info = edge.get('page_info', {})

    def count_medias_by_location(self, id):
        """ Count number of medias from a given location id"""
        r = self._session.get(
            location_medias(id=id, first=0)
        ).json()
        return r.get('data', {}).get('location', {}).get('edge_location_to_media', {}).get('count')

    def get_top_medias_by_location(self, id):
        """ Get top medias from a given location id"""
        r = self._session.get(
            location_medias(id=id, first=0)
        ).json()
        edge = r.get('data', {}).get('location', {}).get('edge_location_to_top_posts', {})
        for each in edge.get('edges', []):
            yield each.get('node')

    def get_locations_by_city(self, id, page):
        """ Get a list of locations in a city by a given city id """
        if isinstance(page, int):
            page = [page]
        elif not isinstance(page, (list, tuple, set)):
            raise ValueError('page must be an integer or an array')
        for each in page:
            r = self._session.get(LOCATION_JSON_INFO % (id, each)).json()
            for location in r.get('location_list', []):
                yield location

    def get_suggested_users(self, id):
        """ Get a list of suggested users for this user.
        Require login."""
        r = self._session.get(user_suggestions(id=id)).json()
        edge = r.get('data', {}).get('chaining', {}).get('edge_chaining', {})
        for each in edge.get('edges', []):
            yield each.get('node')

    def get_chaining_users(self, user_id):
        r = self._session.get(chaining_users(user_id)).json()
        edge = r.get('data', {}).get('user', {}).get('edge_chaining', {})
        for each in edge.get('edges', []):
            yield each.get('node')


class InstagramSeleniumApi(InstagramWebApi):
    def __init__(self, min_scroll_delay=5, max_scroll_delay=10, headless=True, max_retries=3, **kwargs):
        super(InstagramSeleniumApi, self).__init__(**kwargs)
        self.headless = headless
        self._min_scroll_delay = min_scroll_delay
        self._max_scroll_delay = max_scroll_delay
        self._last_scroll_time = 0
        self._last_scroll_height = 0
        self._max_retries = max_retries
        self._logged_in = False
        self._logger = get_logger(self.__class__.__name__)
        options = Options()
        options.headless = self.headless
        self._logger.info("Initializing a browser...")
        self.browser = webdriver.Firefox(firefox_options=options)
        self.wait = WebDriverWait(self.browser, 10)

    def __repr__(self):
        return "InstagramSeleniumApi(min_scroll_delay=%d, max_scroll_delay=%d, headless=%s, max_retry=%d, **kwargs)" % (
            self._min_scroll_delay, self._max_scroll_delay, self.headless, self._max_retries
        )

    @staticmethod
    def _random_delay(min_delay=0, max_delay=3):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def _random_scroll(self, hanging=False, min_height=1080, max_height=2160):
        if hanging:
            scroll_height = self.browser.execute_script(POST_SCROLL_HEIGHT)
        else:
            scroll_height = random.uniform(min_height, max_height)
        self.browser.execute_script(SCROLL % scroll_height)

    def _delay_scroll_if_needed(self, min_scroll_delay=None, max_scroll_delay=None):
        min_scroll_delay = self._min_scroll_delay if min_scroll_delay is None else min_scroll_delay
        max_scroll_delay = self._max_scroll_delay if max_scroll_delay is None else min_scroll_delay

        process_time = time.time() - self._last_scroll_time
        delay = random.uniform(min_scroll_delay, max_scroll_delay)
        if process_time < delay:
            sleep_time = delay - process_time
            self._logger.info('Wait for %ss...' % sleep_time)
            time.sleep(sleep_time)

    def _handle_hanging(self):
        _new_scroll_height = self.browser.execute_script(POST_SCROLL_HEIGHT)
        if _new_scroll_height == self._last_scroll_height:
            retry_count = 0
            while _new_scroll_height == self._last_scroll_height:
                self._logger.warning('Browser is hanging!')
                self._random_scroll(min_height=-1080, max_height=-self._last_scroll_height)
                self._last_scroll_time = time.time()
                self._delay_scroll_if_needed(self._min_scroll_delay+10, self._max_scroll_delay+10)
                self._random_scroll(hanging=True)
                self._delay_scroll_if_needed(self._min_scroll_delay+10, self._max_scroll_delay+10)
                _new_scroll_height = self.browser.execute_script(POST_SCROLL_HEIGHT)
                retry_count += 1
                if retry_count == self._max_retries:
                    self._logger.error("Max retries exceeded!")
                    return True

        self._last_scroll_height = _new_scroll_height

    @staticmethod
    def get_urls_from_elements(elements, crawled_urls):
        for element in elements:
            try:
                url = element.find_element_by_xpath('./a').get_attribute('href')
                url = url.split('?')[0]
                if url not in crawled_urls:
                    crawled_urls.append(url)
                    yield url
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

    def get_media_urls_by_username(self, username, crawled_urls=None):
        """
        Get post urls from a given username.
        :param username: Instagram username of a profile.
        :param crawled_urls: a list of post urls crawled for that username (optional). If provided, these urls won't
        be returned.
        :return: media urls.
        """
        crawled_urls = crawled_urls if isinstance(crawled_urls, list) else list()
        url = ACCOUNT_HTML_INFO % check_not_empty(username)
        self.browser.get(url)
        # self._handle_challange()
        self.wait.until(EC.presence_of_element_located((By.XPATH, POST_COUNT)))
        while len(crawled_urls) < self.posts:
            try:
                self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, POST)))
                elements = self.browser.find_elements_by_xpath(POST)
                self._random_scroll()
                self._last_scroll_time = time.time()
                for url in self.get_urls_from_elements(elements, crawled_urls):
                    yield url
                self._delay_scroll_if_needed()
                if self._handle_hanging():
                    break
            except Exception as e:
                self._logger.error(traceback.print_exc())
                break

    def get_recent_media_urls_by_tag(self, tagname, crawled_urls=None):
        """
        Get recent post urls from a given hashtag on Instagram.
        :param tagname: Instagram hashtag.
        :param crawled_urls: a list of post urls crawled for that tag name (optional). If provided, these urls won't
        be returned.
        :return: media urls
        """
        crawled_urls = crawled_urls if isinstance(crawled_urls, list) else list()
        url = MEDIAS_BY_TAG % check_not_empty(tagname)
        self.browser.get(url)
        self.wait.until(EC.presence_of_element_located((By.XPATH, POST_COUNT)))

        top_posts = self.browser.find_elements_by_xpath(TOP_POST)
        recent_post_count = self.posts - len(top_posts)

        while len(crawled_urls) < recent_post_count:
            try:
                self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, POST)))
                elements = self.browser.find_elements_by_xpath(RECENT_POST)
                self._random_scroll()
                self._last_scroll_time = time.time()
                for url in self.get_urls_from_elements(elements, crawled_urls):
                    yield url
                self._delay_scroll_if_needed()
                if self._handle_hanging():
                    break
            except Exception as e:
                self._logger.error(e)
                break

    def get_recent_media_urls_by_location(self, location_id, crawled_urls=None):
        """
        Get recent post urls from a given location on Instagram.
        :param location_id: id of a location tag on Instagram.
        :param crawled_urls: a list of post urls crawled for that tag name (optional). If provided, these urls won't
        be returned.
        :return: media urls
        """
        crawled_urls = crawled_urls if isinstance(crawled_urls, list) else list()
        url = MEDIAS_BY_LOCATION % check_not_empty(location_id)
        self.browser.get(url)
        while True:
            try:
                self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, POST)))
                elements = self.browser.find_elements_by_xpath(RECENT_POST)
                self._random_scroll()
                self._last_scroll_time = time.time()
                for url in self.get_urls_from_elements(elements, crawled_urls):
                    yield url
                self._delay_scroll_if_needed()
                if self._handle_hanging():
                    break
            except Exception as e:
                self._logger.error(e)
                break

    def get_user_by_username(self, username):
        """
        Get json info of a profile from a given username.
        :param username: Instagram username.
        :return: json info of a profile.
        """
        self.browser.get(ACCOUNT_HTML_INFO % username)
        body = self.browser.find_element_by_tag_name('body')
        script = body.find_element_by_tag_name('script')
        content_text = script.get_attribute('innerHTML')
        content_text = content_text.replace('window._sharedData = ', '')
        content_json = json.loads(content_text[:-1])
        profile_info = content_json.get('entry_data', {}).get('ProfilePage', {})
        return profile_info[0].get('graphql', {}).get('user') if profile_info else profile_info

    def get_user_by_id(self, user_id):
        self.browser.get(USER_INFO_BY_ID % user_id)
        body = self.browser.find_element_by_tag_name('body').text
        json_data = json.loads(body)
        return json_data.get('user')

    def get_user_by_username_v2(self, username):
        """
        Get user info from a given username by inspecting elements on Instagram profile page.
        :param username: Instagram username.
        :return: Instagram user info
        """
        self.browser.get(ACCOUNT_HTML_INFO % username)
        data = dict()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, AVATAR)))
        data['avatar_url'] = self.browser.find_element_by_class_name(AVATAR).get_attribute('src')
        data['username'] = username
        data['statuses_count'] = self.posts
        data['followers_count'] = self.followers
        data['followings_count'] = self.followings
        name = self.browser.find_elements_by_xpath(PROFILE_NAME)
        data['name'] = name[0].text if name else None
        bio = self.browser.find_elements_by_xpath(BIO)
        data['bio'] = bio[0].text if bio else None
        website = self.browser.find_elements_by_xpath(WEBSITE)
        data['website'] = website[0].text if website else None
        data['redirected_website'] = website[0].get_attribute('href') if website else None
        return data

    def get_commenters_from_post(self, url=None, shortcode=None):
        """
        Get Instagram users who commented on a given post.
        :param url: Instagram post url.
        :param shortcode: shortcode in post url.
        :return: commenters' info.
        """
        url = url if url else MEDIA_LINK % shortcode
        self.browser.get(url)
        while True:
            try:
                self.wait.until(EC.element_to_be_clickable((By.XPATH, LOAD_MORE)))
                load_more = self.browser.find_element_by_xpath(LOAD_MORE)
                load_more.click()
            except selenium.common.exceptions.TimeoutException:
                break
        comments = self.browser.find_elements_by_xpath(COMMENT)
        for element in comments:
            commenter = element.find_element_by_xpath('./a')
            comment = element.find_element_by_xpath('./span')
            yield {'username': commenter.text, 'link': url, 'text': comment.text}

    def sign_up(self, email, full_name, username, password):
        """
        Sign up an Instagram account using given parameters.
        """
        self.browser.get(BASE_URL)
        self.wait.until(EC.presence_of_element_located((By.NAME, 'emailOrPhone')))
        e = self.browser.find_element_by_name('emailOrPhone')
        e.send_keys(email)
        self._random_delay()

        fn = self.browser.find_element_by_name('fullName')
        fn.send_keys(full_name)
        self._random_delay()

        u = self.browser.find_element_by_name('username')
        u.send_keys(Keys.CONTROL + "a")
        u.send_keys(Keys.DELETE)
        u.send_keys(username)
        self._random_delay()

        p = self.browser.find_element_by_name('password')
        sign_up = self.browser.find_elements_by_xpath(LOG_IN)
        p.send_keys(password)
        self._random_delay()

        sign_up[1].click()
        self._random_delay()
        if not self._check_exists_by_class_name(SIGN_UP_ERROR_CLASS):
            self._logger.info('Signed up successfully with email: %s, username: %s and password: %s'
                              % (email, username, password))
        else:
            error_msg = self.browser.find_element_by_id(SIGN_UP_ERROR_ID).text
            raise InstagramError(error_msg)

    def log_in(self, username, password, gmail_credentials=None, get_code_retries=3):
        """
        Log in to Instagram using a given account.
        """
        self._logger.info('Trying to log in with username: %s' % username)
        self.browser.get(WEB_LOGIN_URL)
        self.wait.until(EC.presence_of_all_elements_located((
                    By.NAME, "username")))
        u = self.browser.find_element_by_name("username")
        p = self.browser.find_element_by_name("password")
        u.send_keys(username)
        self._random_delay()
        p.send_keys(password)
        self._random_delay()
        self._submit()
        if self._check_exists_by_class_name(LOGGED_IN):
            # self._handle_challange()
            self._logger.info("Logged in successfully with username: %s!" % username)
            self._logged_in = True
            return
        elif self._submit():
            while get_code_retries > 0:
                gmailapi = GmailApi(credentials=gmail_credentials)
                codes = gmailapi.get_codes()
                if not codes:
                    raise InstagramError("No code found - Failed to log in!")
                for code in codes:
                    # security_code =  self.browser.find_element_by_id('security_code')
                    security_code = self.browser.find_element_by_xpath(SECURITY_INPUT)
                    security_code.click()
                    self._random_delay()
                    security_code.send_keys(code.get('code'))
                    self._random_delay()
                    self._submit()
                    if self._check_exists_by_class_name(LOGGED_IN):
                        gmailapi.mark_as_read(code.get('m_id'))
                        # self._handle_challange()
                        self._logger.info("Logged in successfully with username %s!" % username)
                        self._logged_in = True
                        return
                get_code_retries -= 1

        error_msg = self.browser.find_element_by_id('form_error').text
        raise InstagramError(error_msg)

    def log_out(self):
        """
        Log out from Instagram if you already logged in before.
        """
        if self._logged_in:
            try:
                self.browser.get(LOGOUT_URL)
                self._logged_in = False
                self._logger.info('Logged out successfully!')
            except Exception as e:
                raise InstagramError(e)

    def _check_exists_by_class_name(self, class_name):
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            # self.browser.find_element_by_class_name(class_name)
        except selenium.common.exceptions.TimeoutException:
            return False
        return True

    def _handle_challange(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, THIS_WAS_ME)))
            this_was_me = self.browser.find_elements_by_name('choice')
            this_was_me[1].click()
        except selenium.common.exceptions.TimeoutException:
            pass

    def _submit(self):
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, LOG_IN)))
            submit = self.browser.find_elements_by_xpath(LOG_IN)
            if submit[-1].text != 'Follow':
                submit[-1].click()
                return True
        except selenium.common.exceptions.ElementClickInterceptedException:
            self._submit()
        except selenium.common.exceptions.TimeoutException:
            return False
            pass

    def get_likers_from_post(self, url=None, shortcode=None):
        """
        Get Instagram users who liked a given post.
        :param url: Instagram post url.
        :param shortcode: shortcode in post url.
        :return: likers' info.
        """
        if not self._logged_in:
            self.quit()
            raise InstagramError("Login is required for this method!")
        url = url if url else MEDIA_LINK % shortcode
        self.browser.get(url)
        self._handle_challange()
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, LIKES)))
        except selenium.common.exceptions.TimeoutException:
            elements = self.browser.find_elements_by_xpath(FEW_LIKERS)
            for element in elements:
                yield {'username': element.text,
                       'link': element.get_attribute('href'),
                       'name': None,
                       'avatar_url': None}
            return
        likes = self.browser.find_element_by_class_name(LIKES)
        like_count = extract_number_from_text(likes.text)
        self.browser.execute_script("arguments[0].click();", likes)
        # likes.click()
        self.wait.until(EC.presence_of_all_elements_located((By.XPATH, BOX_USERS)))
        liker_box = self.browser.execute_script(LIKERS_BOX)
        liker_box.click()
        count = 0
        while count < like_count:
            self._logger.info('Scrolling down...')
            try:
                liker_box.click()
            except selenium.common.exceptions.StaleElementReferenceException as e:
                self._logger.error(e)
                pass
            liker_box.send_keys(Keys.END)
            self._last_scroll_time = time.time()
            self._delay_scroll_if_needed()
            if self._handle_box_hanging(liker_box, LIKERS_BOX_SCROLL_HEIGHT):
                break
            elements = self.browser.find_elements_by_xpath(BOX_USERS)
            for liker in self.get_box_users(elements[count:]):
                yield liker
            count = len(elements)
            self._logger.info('Number of elements scrolled %d' % len(elements))

    def _handle_box_hanging(self, box, scroll_height_script):
        new_scroll_height = self.browser.execute_script(scroll_height_script)
        retry = 0
        while new_scroll_height == self._last_scroll_height:
            self._logger.warning("Box is hanging!")
            box.send_keys(Keys.END)
            self._last_scroll_time = time.time()
            self._delay_scroll_if_needed(self._min_scroll_delay+10, self._max_scroll_delay+10)
            new_scroll_height = self.browser.execute_script(scroll_height_script)
            retry += 1
            if retry == self._max_retries:
                self._logger.error("Max retries exceeded!")
                return True
        self._last_scroll_height = new_scroll_height

    @staticmethod
    def get_box_users(elements):
        for element in elements:
            avatar_url = element.find_element_by_class_name(AVATAR).get_attribute('src')
            name = element.find_element_by_class_name(LIKER_NAME).text
            link = element.find_element_by_css_selector('a').get_attribute('href')
            yield {'username': extract_username_from_url(link),
                   'link': link,
                   'name': name,
                   'avatar_url': avatar_url}

    def get_followers_by_username(self, username):
        """
        Get followers of a given username
        :param username: Instagram username
        :return: followers' info.
        """
        return self._get_follows_by_username(username, FOLLOWER_COUNT)

    def get_followings_by_username(self, username):
        """
        Get followings of a given username
        :param username: Instagram username
        :return: followings' info.
        """
        return self._get_follows_by_username(username, FOLLOWING_COUNT)

    def get_followers_by_sns_id(self, sns_id, limit=-1, batch=False):
        return self._get_follows_by_sns_id(sns_id, limit=limit, batch=batch)

    def get_followings_by_sns_id(self, sns_id, limit=-1, batch=False):
        return self._get_follows_by_sns_id(sns_id, limit=limit, type='following', batch=batch)

    def _get_follows_by_sns_id(self, sns_id, limit=-1, type='follower', end_cursor="", batch=False):
        if not self._logged_in:
            self.quit()
            raise InstagramError('Login is required for this method!')
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        make_request_url = user_followers_by_id if type == 'follower' else user_followings_by_id
        follows = 'edge_followed_by' if type == 'follower' else 'edge_follow'
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = make_request_url(id=sns_id, first=50, after=page_info['end_cursor'])
                self._last_scroll_time = time.time()
                self.browser.get(url)
                self._logger.info('GET {}'.format(url))
                body = self.browser.find_element_by_tag_name('body').text
                json_data = json.loads(body)
                users = json_data.get('data', {}).get('user', {})
                status = json_data.get('status')
                if status == 'ok' and users is None:
                    break
                edge = users.get(follows, {})

                new_page_info = edge.get('page_info', {})
                error_message = json_data.get('message')
                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    profiles = [each.get('node') for each in edge.get('edges', [])]
                    if not profiles:
                        self._delay_scroll_if_needed()
                        continue
                    _count += len(profiles)
                    yield profiles
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        yield each.get('node')

                if 0 < limit <= _count:
                    break
                self._delay_scroll_if_needed()
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_scroll_delay, self._max_scroll_delay)
                continue

    def get_likers_by_media_link(self, link, limit=-1):
        shortcode = extract_shortcode(link)
        return self._get_engaged_audience_by_media_shortcode(shortcode=shortcode, limit=limit)

    def get_commenters_by_media_link(self, link, limit=-1):
        shortcode = extract_shortcode(link)
        return self._get_engaged_audience_by_media_shortcode(shortcode=shortcode, limit=limit, type='comment')

    def _get_engaged_audience_by_media_shortcode(self, shortcode, type='like', limit=-1, end_cursor="", batch=False):
        if not self._logged_in:
            self.quit()
            raise InstagramError('Login is required for this method!')
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        make_request_url = media_likes_by_shortcode if type == 'like' else media_comments_by_shortcode
        engaged_audience = 'edge_liked_by' if type == 'like' else 'edge_media_to_comment'
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = make_request_url(shortcode=shortcode, first=50, after=page_info['end_cursor'])
                self._last_scroll_time = time.time()
                self._logger.info('GET {}'.format(url))
                self.browser.get(url)
                body = self.browser.find_element_by_tag_name('body').text
                json_data = json.loads(body)
                edge = json_data.get('data', {}).get('shortcode_media', {}).get(engaged_audience, {})
                new_page_info = edge.get('page_info', {})
                error_message = json_data.get('message')
                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    profiles = [each.get('node') for each in edge.get('edges', [])]
                    if not profiles:
                        self._delay_scroll_if_needed()
                        continue
                    _count += len(profiles)
                    yield profiles
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        yield each.get('node')

                if 0 < limit <= _count:
                    break
                self._delay_scroll_if_needed()
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_scroll_delay, self._max_scroll_delay)
                continue

    def _get_follows_by_username(self, username, xpath):
        if not self._logged_in:
            self.quit()
            raise InstagramError('Login is required for this method!')
        self.browser.get(ACCOUNT_HTML_INFO % username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        follows = self.browser.find_element_by_xpath(xpath)
        follows.click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, FOLLOW_BOX)))
        box = self.browser.find_element_by_class_name(FOLLOW_BOX)
        box.click()
        self.wait.until(EC.presence_of_all_elements_located((By.XPATH, BOX_USERS)))
        count = self.followers if xpath == FOLLOWER_COUNT else self.followings
        last_len = 0
        while last_len < count:
            self._logger.info('Scrolling down...')
            box.send_keys(Keys.END)
            self._last_scroll_time = time.time()
            if self._handle_box_hanging(box, FOLLOW_BOX_SCROLL_HEIGHT):
                break
            elements = self.browser.find_elements_by_xpath(BOX_USERS)
            for follower in self.get_box_users(elements[last_len:]):
                yield follower
            last_len = len(elements)
            self._logger.info('Number of elements scrolled %d for %s' % (len(elements), username))
            self._delay_scroll_if_needed()

    def get_recent_medias_by_location(self, id, limit=-1, end_cursor="", batch=False):
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = location_medias(id=id, first=50, after=page_info.get('end_cursor'))
                self.browser.get(url)
                self._last_scroll_time = time.time()
                self._logger.info('GET {}'.format(url))
                body = self.browser.find_element_by_tag_name('body').text
                json_data = json.loads(body)
                location = json_data.get('data', {}).get('location', {})
                edge = location.get('edge_location_to_media', {})

                location.pop('edge_location_to_media', None)
                location.pop('edge_location_to_top_posts', None)

                status = json_data.get('status')
                if status == 'ok' and edge is None:
                    break

                new_page_info = edge.get('page_info', {})
                error_message = json_data.get('message')

                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    posts = [each.get('node') for each in edge.get('edges', [])]
                    if not posts:
                        self._delay_scroll_if_needed()
                        continue
                    for post in posts:
                        post['location'] = location
                    _count += len(posts)
                    yield posts
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        post = each.get('node')
                        post['location'] = location
                        yield post

                if 0 < limit <= _count:
                    break
                self._delay_scroll_if_needed()
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_scroll_delay, self._max_scroll_delay)
                continue

    def get_recent_medias_by_tag(self, tag, limit=-1, end_cursor="", batch=False):
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = hashtag_medias(tag_name=tag, first=50, after=page_info.get('end_cursor'))
                self.browser.get(url)
                self._last_scroll_time = time.time()
                self._logger.info('GET {}'.format(url))
                body = self.browser.find_element_by_tag_name('body').text
                json_data = json.loads(body)
                edge = json_data.get('data', {}).get('hashtag', {}).get('edge_hashtag_to_media', {})

                status = json_data.get('status')
                if status == 'ok' and edge is None:
                    break

                new_page_info = edge.get('page_info', {})
                error_message = json_data.get('message')

                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info
                if batch:
                    posts = [each.get('node') for each in edge.get('edges', [])]
                    if not posts:
                        self._delay_scroll_if_needed()
                        continue
                    _count += len(posts)
                    yield posts
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        yield each.get('node')

                if 0 < limit <= _count:
                    break
                self._delay_scroll_if_needed()
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_scroll_delay, self._max_scroll_delay)
                continue

    def get_user_medias_by_id(self, user_id, per_page=50, end_cursor=None, limit=-1, batch=False):
        """Get the list of medias of a user."""
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = user_medias(user_id, first=per_page, after=page_info.get('end_cursor'))
                self.browser.get(url)
                self._last_scroll_time = time.time()
                self._logger.info('GET {}'.format(url))
                body = self.browser.find_element_by_tag_name('body').text
                json_data = json.loads(body)
                user = json_data.get('data', {}).get('user', {})
                status = json_data.get('status')
                if status == 'ok' and user is None:
                    break
                edge = user.get('edge_owner_to_timeline_media', {})
                new_page_info = edge.get('page_info', {})
                error_message = json_data.get('message')

                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    posts = [each.get('node') for each in edge.get('edges', [])]
                    if not posts:
                        self._delay_scroll_if_needed()
                        continue
                    _count += len(posts)
                    yield posts
                for each in edge.get('edges', []):
                    _count += 1
                    yield each.get('node')

                if 0 < limit <= _count:
                    break
                self._delay_scroll_if_needed()
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_scroll_delay, self._max_scroll_delay)
                continue

    def close(self):
        """
        Close the browser window that the driver has focus of.
        """
        self._logger.info("Closed browser.")
        return self.browser.close()

    def quit(self):
        """
        Close all browser windows and safely ends the session.
        """
        self._logger.info("Quited browser.")
        return self.browser.quit()

    @property
    def posts(self):
        return extract_number_from_text(self.browser.find_element_by_xpath(POST_COUNT).text)

    @property
    def followers(self):
        return extract_number_from_text(self.browser.find_element_by_xpath(FOLLOWER_COUNT).get_attribute('title'))

    @property
    def followings(self):
        return extract_number_from_text(self.browser.find_element_by_xpath(FOLLOWING_COUNT).text)


class RequestiumSession(Session):

    DEFAULT_REQUEST_TIMEOUT = 60
    _last_request_time = 0

    def __init__(self, min_request_delay=5, max_request_delay=10, driver='linux_chromedriver'):
        super(RequestiumSession, self).__init__(
            webdriver_path=join(dirname(__file__), 'webdrivers/%s' % driver),
            browser='chrome',
            default_timeout=15,
            webdriver_options={'arguments': []})
        self._min_request_delay = min_request_delay
        self._max_request_delay = max_request_delay
        self._logger = get_logger(self.__class__.__name__)

    def get(self, *args, **kwargs):
        self._logger.info('GET %s with params %s' % (' '.join(args), kwargs))
        kwargs['timeout'] = kwargs.get('timeout', self.DEFAULT_REQUEST_TIMEOUT)
        self._delay_request_if_needed()
        r = super(RequestiumSession, self).get(*args, **kwargs)
        self._last_request_time = time.time()
        InstagramSession.raise_exception_for_status(r)
        return r

    def _delay_request_if_needed(self):
        process_time = time.time() - self._last_request_time
        delay = random.uniform(self._min_request_delay, self._max_request_delay)
        if delay and process_time < delay:
            sleep_time = delay - process_time
            self._logger.info('Request delayed for %ss' % sleep_time)
            time.sleep(sleep_time)


class InstagramRequestiumApi(object):
    """
    For methods requiring login, use a single process to log in in the first time to save cookies, the launch muliple
    processes which will load cookies from the saved file.
    """
    def __init__(self, min_request_delay=5, max_request_delay=10, headless=True, driver='linux_chromedriver'):
        self._logged_in = False
        self._logger = get_logger(self.__class__.__name__)
        self._min_request_delay = min_request_delay
        self._max_request_delay = max_request_delay
        self._session = RequestiumSession(driver=driver, min_request_delay=self._min_request_delay,
                                          max_request_delay=self._max_request_delay)
        if headless:
            self._session.webdriver_options['arguments'].append('headless')

    @staticmethod
    def _random_delay(min_delay=0, max_delay=3):
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    def get_user_by_username(self, username):
        if not self._logged_in:
            raise InstagramError('Login is required for this method!')
        response = self._session.get(ACCOUNT_JSON_INFO % username).json()
        return response.get('graphql', {}).get('user')

    def get_user_by_id(self, user_id):
        url = user_info_by_id(user_id)
        response = self._session.get(url).json()
        user = response.get('data', {}).get('user', {})
        if user:
            return user.get('reel', {}).get('user')
        else:
            self._logger.warning('The given id is not available')

    def log_in(self, username, password, gmail_credentials=None):
        self._logger.info('Trying to load cookies for %s' % username)
        try:
            cookies = self._load_cookies(username)
            self._session.cookies.update(cookies)
            self._logged_in = True
            self._logger.info("Logged in successfully with username: %s!" % username)
            return
        except IOError:
            self._logger.info('No cookies found for %s' % username)
        self._logger.info('Trying to log in with username: %s' % username)
        self._session.driver.get(WEB_LOGIN_URL)
        self._session.driver.ensure_element_by_name('username').send_keys(username)
        self._random_delay()
        self._session.driver.ensure_element_by_name('password').send_keys(password)
        self._random_delay()
        self._session.driver.ensure_element_by_xpath(LOG_IN).click()
        try:
            self._session.driver.ensure_element_by_class_name(LOGGED_IN, timeout=5)
            self._logger.info("Logged in successfully with username: %s!" % username)
            self._session.transfer_driver_cookies_to_session()
            self._save_cookies(self._session.cookies, username)
            self._logged_in = True
            return
        except selenium.common.exceptions.TimeoutException:
            try:
                self._session.driver.ensure_element_by_xpath(SEND_CODE).click()
                gmailapi = GmailApi(credentials=gmail_credentials)
                codes = gmailapi.get_codes()
                if not codes:
                    raise InstagramError("No code found - Failed to log in!")
                for code in codes:
                    self._session.driver.ensure_element_by_id('security_code').send_keys(code.get('code'))
                    self._random_delay()
                    self._session.driver.ensure_element_by_xpath(SUBMIT_CODE).click()
                    try:
                        self._session.driver.ensure_element_by_class_name(LOGGED_IN)
                        gmailapi.mark_as_read(code.get('m_id'))
                        self._logger.info("Logged in successfully with username %s!" % username)
                        self._session.transfer_driver_cookies_to_session()
                        self._save_cookies(self._session.cookies, username)
                        self._logged_in = True
                        return
                    except selenium.common.exceptions.TimeoutException:
                        pass
            except selenium.common.exceptions.TimeoutException:
                try:
                    error_msg = self._session.driver.ensure_element_by_id('form_error', timeout=3).text
                    raise InstagramError(error_msg)
                except selenium.common.exceptions.TimeoutException:
                    try:
                        error_msg = self._session.driver.ensure_element_by_id('slfErrorAlert', timeout=3).text
                        raise InstagramError(error_msg)
                    except selenium.common.exceptions.TimeoutException:
                        raise InstagramError("Unknown error - Failed to log in!")

    @staticmethod
    def _save_cookies(cookies, filename):
        filepath = join(dirname(__file__), 'cookies/%s' % filename)
        with open(filepath, 'wb') as f:
            pickle.dump(cookies, f)

    @staticmethod
    def _load_cookies(filename):
        filepath = join(dirname(__file__), 'cookies/%s' % filename)
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def log_out(self):
        if self._logged_in:
            try:
                self._session.get(LOGOUT_URL)
                self._logged_in = False
                self._logger.info('Logged out successfully!')
            except Exception as e:
                raise InstagramError(e)

    def get_followers_by_sns_id(self, sns_id, limit=-1, batch=False):
        return self._get_follows_by_sns_id(sns_id, limit=limit, batch=batch)

    def get_followings_by_sns_id(self, sns_id, limit=-1, batch=False):
        return self._get_follows_by_sns_id(sns_id, limit=limit, type='following', batch=batch)

    def _get_follows_by_sns_id(self, sns_id, limit=-1, type='follower', end_cursor="", batch=False, max_retries=5):
        if not self._logged_in:
            raise InstagramError('Login is required for this method!')
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        make_request_url = user_followers_by_id if type == 'follower' else user_followings_by_id
        follows = 'edge_followed_by' if type == 'follower' else 'edge_follow'
        _count = 0
        _retries = 0
        while page_info.get('has_next_page'):
            try:
                url = make_request_url(id=sns_id, first=50, after=page_info['end_cursor'])
                response = self._session.get(url).json()
                users = response.get('data', {}).get('user', {})
                status = response.get('status')
                if status == 'ok' and users is None:
                    break
                edge = users.get(follows, {})

                new_page_info = edge.get('page_info', {})
                error_message = response.get('message')
                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    profiles = [each.get('node') for each in edge.get('edges', [])]
                    if not profiles:
                        continue
                    _count += len(profiles)
                    yield profiles
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        yield each.get('node')

                if 0 < limit <= _count:
                    break
            except InstagramError as e:
                if e.status_code in (429, 502, 503):
                    self._random_delay(self._min_request_delay, self._max_request_delay)
                elif e.status_code == 404:
                    break
                else:
                    raise e
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_request_delay, self._max_request_delay)

    def get_likers_by_media_link(self, link, limit=-1):
        shortcode = extract_shortcode(link)
        return self._get_engaged_audience_by_media_shortcode(shortcode=shortcode, limit=limit)

    def get_commenters_by_media_link(self, link, limit=-1):
        shortcode = extract_shortcode(link)
        return self._get_engaged_audience_by_media_shortcode(shortcode=shortcode, limit=limit, type='comment')

    def _get_engaged_audience_by_media_shortcode(self, shortcode, type='like', limit=-1, end_cursor="", batch=False):
        if not self._logged_in:
            raise InstagramError('Login is required for this method!')
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        make_request_url = media_likes_by_shortcode if type == 'like' else media_comments_by_shortcode
        engaged_audience = 'edge_liked_by' if type == 'like' else 'edge_media_to_comment'
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = make_request_url(shortcode=shortcode, first=50, after=page_info['end_cursor'])
                response = self._session.get(url).json()
                edge = response.get('data', {}).get('shortcode_media', {}).get(engaged_audience, {})
                new_page_info = edge.get('page_info', {})
                error_message = response.get('message')
                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    profiles = [each.get('node') for each in edge.get('edges', [])]
                    if not profiles:
                        continue
                    _count += len(profiles)
                    yield profiles
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        yield each.get('node')

                if 0 < limit <= _count:
                    break
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_request_delay, self._max_request_delay)
                continue

    def get_recent_medias_by_location(self, id, limit=-1, end_cursor="", batch=False):
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = location_medias(id=id, first=50, after=page_info.get('end_cursor'))
                response = self._session.get(url).json()
                location = response.get('data', {}).get('location', {})
                edge = location.get('edge_location_to_media', {})

                location.pop('edge_location_to_media', None)
                location.pop('edge_location_to_top_posts', None)

                status = response.get('status')
                if status == 'ok' and edge is None:
                    break

                new_page_info = edge.get('page_info', {})
                error_message = response.get('message')

                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    posts = [each.get('node') for each in edge.get('edges', [])]
                    if not posts:
                        continue
                    for post in posts:
                        post['location'] = location
                    _count += len(posts)
                    yield posts
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        post = each.get('node')
                        post['location'] = location
                        yield post

                if 0 < limit <= _count:
                    break
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_request_delay, self._max_request_delay)
                continue

    def get_recent_medias_by_tag(self, tag, limit=-1, end_cursor="", batch=False):
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = hashtag_medias(tag_name=tag, first=50, after=page_info.get('end_cursor'))
                response = self._session.get(url).json()
                hashtag = response.get('data', {}).get('hashtag')
                if not hashtag:
                    break
                edge = hashtag.get('edge_hashtag_to_media', {})
                status = response.get('status')
                if status == 'ok' and edge is None:
                    break
                new_page_info = edge.get('page_info', {})
                error_message = response.get('message')

                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info
                if batch:
                    posts = [each.get('node') for each in edge.get('edges', [])]
                    if not posts:
                        continue
                    _count += len(posts)
                    yield posts
                else:
                    for each in edge.get('edges', []):
                        _count += 1
                        yield each.get('node')

                if 0 < limit <= _count:
                    break
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_request_delay, self._max_request_delay)
                continue

    def get_user_medias_by_id(self, user_id, per_page=50, end_cursor=None, limit=-1, batch=False):
        if not self._logged_in:
            raise InstagramError('Login is required for this method!')
        page_info = {'has_next_page': True, 'end_cursor': end_cursor}
        _count = 0
        while page_info.get('has_next_page'):
            try:
                url = user_medias(user_id, first=per_page, after=page_info.get('end_cursor'))
                response = self._session.get(url).json()
                user = response.get('data', {}).get('user', {})
                status = response.get('status')
                if status == 'ok' and user is None:
                    break
                edge = user.get('edge_owner_to_timeline_media', {})
                new_page_info = edge.get('page_info', {})
                error_message = response.get('message')

                if not new_page_info and error_message:
                    self._logger.info("Sleep in 5 minutes due to %s." % error_message)
                    time.sleep(300)
                    continue
                else:
                    page_info = new_page_info

                if batch:
                    posts = [each.get('node') for each in edge.get('edges', [])]
                    if not posts:
                        continue
                    _count += len(posts)
                    yield posts
                for each in edge.get('edges', []):
                    _count += 1
                    yield each.get('node')

                if 0 < limit <= _count:
                    break
            except Exception as e:
                self._logger.error("Retrying due to %s." % e)
                traceback.print_exc()
                self._random_delay(self._min_request_delay, self._max_request_delay)
                continue

    def get_suggested_users(self, sns_id):
        """
        Get suggested users of account sns_id.

        As of 2019-06, Instagram provides no pagination for the response and suggested users
        are returned at once. The number is usually 80, can be less if account's network is limited.

        Instagram returns below response if sns_id is invalid (for example deactivated)
            {
              "data": {
                "user": {

                },
                "chaining": null
              },
              "status": "ok"
            }

        :param sns_id: instagram sns_id of account to get suggestions for.
        :return: generator of dicts of suggested user info. Example:
            {
              "id": "1464476059",
              "blocked_by_viewer": false,
              "followed_by_viewer": false,
              "follows_viewer": false,
              "full_name": "agooddaytowork",
              "has_blocked_viewer": false,
              "has_requested_viewer": false,
              "is_private": false,
              "is_verified": false,
              "profile_pic_url": "https://instagram.fsgn3-1.fna.fbcdn.net/vp/d6d4cfd20285ecded21594b0bcd35bac/5D80704F/t51.2885-19/10593327_1468861590034122_832461119_a.jpg?_nc_ht=instagram.fsgn3-1.fna.fbcdn.net",
              "requested_by_viewer": false,
              "username": "agooddaytowork"
            }
        """
        if not self._logged_in:
            self.quit()
            raise InstagramError('Login is required for this method!')

        make_request_url = user_suggestions
        url = make_request_url(id=sns_id)
        response = self._session.get(url).json()

        chaining = response['data']['chaining']
        if chaining is None and response['status'] == 'ok':
            # see docstring for instagram response
            self._logger.error('Could not get suggested users for [sns_id={}] might be obsolete. Response: {}'
                               .format(sns_id, response))
            raise SuggestedUsersNotFound()
        suggested_users = chaining['edge_chaining']['edges']
        error_message = response.get('message')
        if error_message:
            self._logger.info("Sleep for 2 minutes due to %s." % error_message)
            time.sleep(120)
        if suggested_users:
            for node in suggested_users:
                user_raw = node.get('node', {})
                yield user_raw

    def close(self):
        """
        Close the browser window that the driver has focus of.
        """
        self._logger.info("Closed browser.")
        return self._session.driver.close()

    def quit(self):
        """
        Close all browser windows and safely ends the session.
        """
        self._logger.info("Quited browser.")
        return self._session.driver.quit()



