import logging
from logging.handlers import RotatingFileHandler

__author__ = 'duydo'

CRITICAL = logging.CRITICAL
FATAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

__loggers = {}


def get_logger(name, log_file=None, level=INFO):
    global __loggers
    if name in __loggers:
        return __loggers[name]
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    sh = logging.StreamHandler()
    sh.setFormatter(log_formatter)
    logger.addHandler(sh)
    if log_file:
        fh = RotatingFileHandler(log_file, maxBytes=50000000, backupCount=5)
        fh.setFormatter(log_formatter)
        logger.addHandler(fh)
    __loggers[name] = logger
    return logger
