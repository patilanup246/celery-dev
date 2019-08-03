import logging

from celery import Task

from xde.app import app
from .crawling.instagram import crawl_user


class BaseTask(Task):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)


@app.task(base=BaseTask)
def add(a, b, c):
    return a + b + c


@app.task(base=BaseTask)
def difference(a, b):
    return a - b