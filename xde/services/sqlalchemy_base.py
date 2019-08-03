# Copyright (C) 2017 Xomad. All rights reserved.
#
# Created on 10/25/17

from logging import getLogger

from xde._services import BaseService


class SqlAlchemyBaseService(BaseService):
    """Base SqlAlchemy Service that ensures the connection to the database is handled correctly"""

    def __init__(self):
        self._logger = getLogger(self.name)
        self._pg_repo = None  # Assign the primary Postgres repository to this property

    def use_pg_repo(self, pg_repo):
        """assigns the primary Postgres repository to the service"""
        self._pg_repo = pg_repo

    def remove_all_pg_sessions(self):
        """removes all Postgres sessions used by this service

        Override this in case this service uses many Postgres repositories with different sessions"""
        self._pg_repo.remove_session()
