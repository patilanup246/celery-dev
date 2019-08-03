from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Text, SmallInteger, Integer, Boolean

from xde.models import Base


class Post(Base):
    """ store post data parsed from instagram without enrichment """
    __table_args__ = {'schema': 'public'}
    __tablename__ = 'post'

    sns_id = Column(Text, primary_key=True, nullable=False)
    sns_name = Column(Text, primary_key=True, nullable=False)

    status = Column(SmallInteger, nullable=False, default=1)

    created_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"))
    updated_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"),
                        onupdate=text("timezone('utc', now())"))
    published_at = Column(DateTime, nullable=False)

    link = Column(Text)
    body = Column(Text)
    user_sns_id = Column(Text)

    place_name = Column(Text)

    tags = Column(ARRAY(Text))
    media = Column(ARRAY(Text))
    mentions = Column(ARRAY(Text))
    likes_count = Column(Integer)
    replies_count = Column(Integer)

    display_image_url = Column(Text)
    is_original = Column(Boolean)
    video_view_count = Column()
    # mismatch: paid_partnerships with S on ES - 2019-07, keeping typo for compatibility
    paid_partnership = Column(JSONB)

    sources = Column(ARRAY(Text))

    def __repr__(self):
        return '%s:%s-%s' % (self.__class__.__name__, self.sns_name, self.sns_id)
