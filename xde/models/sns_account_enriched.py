# Copyright (C) 2016 Xomad. All rights reserved.
#
# Created on 8/22/16

from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, DateTime, Float, Integer, SmallInteger, Text

from xde.models import Base


class SnsAccountEnriched(Base):
    __table_args__ = (
        ForeignKeyConstraint(
            ['sns_name', 'sns_id'],
            ['public.sns_account.sns_name', 'public.sns_account.sns_id'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        UniqueConstraint('sns_name', 'sns_id', name='sns_account_enriched_sns_name_sns_id_key'),
        {'schema': 'public'}
    )
    __tablename__ = 'sns_account_enriched'

    sns_name = Column(Text, primary_key=True, nullable=False)
    sns_id = Column(Text, primary_key=True, nullable=False)
    status = Column(SmallInteger, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=datetime.utcnow())
    birthyear = Column(SmallInteger)
    gender = Column(SmallInteger)
    locations = Column(JSONB)
    marital_status = Column(SmallInteger)
    is_parent = Column(Boolean)
    reach = Column(BigInteger)
    engagement = Column(Integer)
    engagement_rate = Column(Float)
    posts_count = Column(Integer)
    xfluences = Column(JSONB)
    tags = Column(ARRAY(Text))
    is_brand = Column(Boolean)
    sponsor_types = Column(ARRAY(SmallInteger))

    # Relationships
    sns_account = relationship('SnsAccount', back_populates='sns_account_enriched')

    def __repr__(self):
        return '%s:%s-%s' % (self.__class__.__name__, self.sns_name, self.sns_id)

    @property
    def sns_account_id(self):
        return '%s-%s' % (self.sns_name, self.sns_id)
