"""
this module contains instagram crawling methods that
can be called by celery tasks.

Purpose:
    - handling crawling specific errors here.

    - decoupling between celery tasks and crawling activities. Handling crawling details
    in celery tasks causing tasks to have too many responsibilities.

    - celery tasks should only care about domain-specific task coordination.
"""
import time

from xde.crawling.instagram.models import User
from xde.services import BaseService
from xde.services.crawlers import accounts, adapters
from xde.services.registry import ServiceRegistry
from xde.core.decorators import lazy_property
from xde.crawling.instagram.web import InstagramWebApi, InstagramRequestiumApi, InstagramError, PostUnavailableError
from xde.helpers.logger import get_logger


class InstagramCrawlingService(BaseService):

    def __init__(self):
        self.max_retries = None
        self._min_request_delay = 3
        self._max_request_delay = 5
        self._logger = get_logger(self.__class__.__name__)

    @lazy_property
    def username(self):
        username = None
        if not username:
            credentials = accounts.get_account_for_vm()
            username = credentials.get('ins_account')
        return username

    @lazy_property
    def password(self):
        password = None
        if not password:
            credentials = accounts.get_account_for_vm()
            password = credentials.get('ins_password')
        return password

    @lazy_property
    def gmail_credentials(self):
        gmail_credentials = None
        if not gmail_credentials:
            credentials = accounts.get_account_for_vm()
            gmail_account = credentials.get('gmail_account')
            gmail_credentials = '{}_credentials.json'.format(gmail_account)
        return gmail_credentials

    @lazy_property
    def web_api(self):
        api = InstagramWebApi(min_delayed_time=self._min_request_delay, max_delayed_time=self._max_request_delay)
        return api

    @lazy_property
    def requestium_api(self):
        api = InstagramRequestiumApi(min_request_delay=self._min_request_delay,
                                     max_request_delay=self._max_request_delay)
        try:
            api.log_in(self.username, self.password, self.gmail_credentials)
            return api
        except Exception:
            api.quit()
            raise

    @lazy_property
    def audience_service(self):
        from xde._services.audience import AudienceService
        return ServiceRegistry.service(AudienceService)

    @lazy_property
    def post_service(self):
        from xde._services.post import PostService
        return ServiceRegistry.service(PostService)

    def crawl_commenters_from_post_id(self, post_sns_id, limit=-1):
        pass

    def crawl_users(self, usernames):
        api = self.web_api
        users = []
        for username in usernames:
            while True:
                try:
                    user_json_raw = api.get_user_by_username(username)
                    user = User.parse(user_json_raw)
                    users.append(user)
                    break
                except InstagramError as e:
                    self._logger.error(e)
                    if e.status_code in (429, 502, 503):
                        self._logger.info('Wait for 5m...')
                        time.sleep(300)
                    elif e.status_code == 404:
                        users.append(None)
                        break
                    else:
                        raise e
                except Exception as e:
                    self._logger.error('%s - %s' % (e, username), exc_info=True)
                    raise e

        return users

    def crawl_commenters_from_post_mapping(self, post, limit=-1):
        """
        crawl and write audience to db.

        1. crawl audiences from post comments and write to audience db
        2. produce task to crawl profile of those audiences

        Needs long delay if using InstagramWebApi to avoid 429 error from instagram
            self._min_request_delay = 45
            self._max_request_delay = 75
            api = self.web_api

        Shorter delays are ok if using logged-in api. Decided to use RequestiumApi.

        :param post: dict that must have keys
            sns_name
            sns_id
            user_sns_id
            link
        :param limit:
        :return: generator of audience
        """
        try:
            # TODO add check if crawled commenters for this post
            api = self.requestium_api

            # TODO - get commenters should return models
            commenters = api.get_commenters_by_media_link(link=post.get('link'), limit=limit)
            for commenter in commenters:
                self._logger.debug(commenter)
                audience = adapters.build_audience_from_comment(post, commenter)
                self.audience_service.upsert(audience)
                yield audience

        except PostUnavailableError as e:
            # do nothing
            self._logger.info(e)

        except InstagramError as e:
            self._logger.error(e, exc_info=True)
            if e.status_code in (429, 502, 503):
                self._logger.info('Wait for 5m...')
                time.sleep(300)
                raise

