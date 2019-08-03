from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime, SmallInteger, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from xde.models import Base


class PostFakeEngagement(Base):
    __tablename__ = 'post_enriched_fake_engagement'
    __table_args__ = ({'schema': 'public'})

    sns_name = Column(Text, nullable=False, primary_key=True)
    sns_id = Column(Text, nullable=False, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"))
    updated_at = Column(DateTime, nullable=True, default=text("timezone('utc', now())"),
                        onupdate=text("timezone('utc', now())"))

    fake_engagement = Column(SmallInteger, nullable=False)
    payload = Column(JSONB, nullable=True)

    def __repr__(self):
        return '{}:{}-{} ({})'.format(self.__class__.__name__, self.sns_name, self.sns_id, self.fake_engagement)
