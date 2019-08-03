from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Text, SmallInteger, Integer, Float, Boolean

from xde.models import Base


class PostEnriched(Base):
    """ store post data enriched by machine """
    __table_args__ = {'schema': 'public'}
    __tablename__ = 'post_enriched'

    sns_id = Column(Text, primary_key=True, nullable=False)
    sns_name = Column(Text, primary_key=True, nullable=False)

    status = Column(SmallInteger, nullable=False, default=1)

    created_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"))
    updated_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"),
                        onupdate=text("timezone('utc', now())"))

    engagement = Column(Integer)
    engagement_rate = Column(Float)
    reach = Column(Integer)

    is_sponsored = Column(Boolean)
    brand_usernames = Column(ARRAY(Text))
    vertical_ids = Column(ARRAY(Integer))

    purchase_intents = Column(JSONB(none_as_null=True))
    fake_engagement = Column(SmallInteger)

    def __repr__(self):
        return '%s:%s-%s' % (self.__class__.__name__, self.sns_name, self.sns_id)
