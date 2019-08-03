# Copyright (C) 2015 Xomad. All rights reserved.
#
# Created on 02/11/2015

from datetime import datetime
from hashlib import md5

from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, SmallInteger, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from xde.models import Base
# from xde.models.post import Post
from xde.models.sns_account_enriched import SnsAccountEnriched
from xde.models.sns_follower import SnsFollower


class SnsAccount(Base):
    __table_args__ = {'schema': 'public'}
    __tablename__ = 'sns_account'

    sns_name = Column(Text, primary_key=True, nullable=False)
    sns_id = Column(Text, primary_key=True, nullable=False)
    status = Column(SmallInteger, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=datetime.utcnow())
    user_id = Column(Integer, ForeignKey('public.x_user.user_id', ondelete='SET NULL', onupdate='CASCADE'), index=True)
    username = Column(Text)
    name = Column(Text)
    avatar_url = Column(Text)
    followers_count = Column(Integer)
    followings_count = Column(Integer)
    likes_count = Column(Integer)
    lists_count = Column(Integer)
    statuses_count = Column(Integer)
    location = Column(Text)
    bio = Column(Text)
    website_url = Column(Text)
    link = Column(Text)
    cover_url = Column(Text)
    source = Column(Text)
    is_verified = Column(Boolean)
    is_private = Column(Boolean)
    sources = Column(ARRAY(Text))
    email = Column(Text)
    category = Column(Text)
    is_business = Column(Boolean)
    phone_number = Column(Text)
    address = Column(JSONB)

    # Relationships
    followers = relationship('SnsFollower')
    # posts = relationship('Post', backref='sns_account')
    sns_account_enriched = relationship('SnsAccountEnriched', uselist=False, back_populates='sns_account')

    def __repr__(self):
        return '%s:%s-%s' % (self.__class__.__name__, self.sns_name, self.sns_id)

    @property
    def sns_account_id(self):
        return '%s-%s' % (self.sns_name, self.sns_id)

    def generate_avatar_filename(self, extension=None):
        return '%s%s' % (md5('%s:%s-%s:avatar' % (self.__class__.__name__, self.sns_name, self.sns_id)).hexdigest(), extension or '')

    def generate_cover_filename(self, extension=None):
        return '%s%s' % (md5('%s:%s-%s:cover' % (self.__class__.__name__, self.sns_name, self.sns_id)).hexdigest(), extension or '')
