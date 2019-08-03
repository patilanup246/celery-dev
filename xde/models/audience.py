from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime, SmallInteger, Text, Integer

from xde.models import Base


class Audience(Base):
    __tablename__ = 'audience'
    sns_name = Column(Text, nullable=False, primary_key=True)
    sns_id = Column(Text, primary_key=True)

    post_sns_id = Column(Text, nullable=False)
    user_sns_id = Column(Text, nullable=False)
    username = Column(Text, nullable=False)
    engaged_username = Column(Text)
    engaged_sns_id = Column(Text, nullable=False)
    action = Column(SmallInteger, nullable=False)

    body = Column(Text, nullable=True)
    acted_at = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"))
    updated_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"),
                        onupdate=text("timezone('utc', now())"))

    def __repr__(self):
        return '{}:{}-{}-{} ({})'.format(self.__class__.__name__, self.sns_name, self.post_sns_id, self.engaged_username, self.action)
