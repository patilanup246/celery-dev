# Copyright (C) 2016 Xomad. All rights reserved.
#
# Created on 12/15/16

from datetime import datetime

from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime, SmallInteger, Text, Integer

from xde.models import Base

SOURCE_XINA_ENGINE = 1
SOURCE_DEMOGRAPHICS_PRO = 2

VERSION_XINA_ENGINE = 1
VERSION_DEMOGRAPHICS_PRO = 6


class SnsFollowerDemographic(Base):
    __table_args__ = (
        UniqueConstraint(
            'sns_name', 'sns_id', 'version',
            name='sns_follower_demographic_sns_name_sns_id_version_key'
        ),
        {'schema': 'public'}
    )
    __tablename__ = 'sns_follower_demographic'

    sns_name = Column(Text, primary_key=True, nullable=False)
    sns_id = Column(Text, primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=datetime.utcnow())
    version = Column(SmallInteger, primary_key=True, nullable=False)
    demographic = Column(JSONB)
    demographic_percentage = Column(JSONB)
    followers_count = Column(Integer)
    analyzed_followers_count = Column(Integer)

    def __repr__(self):
        return '%s:%s-%s-%s' % (self.__class__.__name__, self.sns_name, self.sns_id, self.version)

    @property
    def sns_account_id(self):
        return '%s-%s' % (self.sns_name, self.sns_id)
