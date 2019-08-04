from celery import Task

from xde.app import app
from xde.core.decorators import lazy_property
from xde.helpers.logger import get_logger
from xde.services.registry import ServiceRegistry


class BaseCrawler(Task):
    def __init__(self):
        self._logger = get_logger(self.__name__)

    @lazy_property
    def instagram_crawling_service(self):
        from xde.services.crawlers.instagram import InstagramCrawlingService
        return ServiceRegistry.service(InstagramCrawlingService)


@app.task(name='crawl_user', routing_key='rkey', bind=True, base=BaseCrawler)
def crawl_user(self, usernames):
    try:
        ics = self.instagram_crawling_service
        users = ics.crawl_users(usernames)
        return users
    except Exception as e:
        self._logger.error(e, exc_info=True)
        raise self.retry(exc=e)


@app.task(name='process_user', bind=True, base=BaseCrawler)
def process_user(self, users):
    try:
        self._logger.info('Processing...')
        processed_users = users
        return processed_users
    except Exception as e:
        self._logger.error(e, exc_info=True)
        raise self.retry(exc=e)


@app.task(name='write_user', bind=True, base=BaseCrawler)
def write_user(self, processed_users):
    try:
        self._logger.info('Writing...')
        return processed_users
    except Exception as e:
        self._logger.error(e, exc_info=True)
        raise self.retry(exc=e)
