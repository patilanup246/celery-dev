from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Text, SmallInteger

from xde.models import Base


class CommentEnrichedPurchaseIntent(Base):
    __table_args__ = {'schema': 'public'}
    __tablename__ = 'comment_enriched_purchase_intent'

    sns_name = Column(Text, primary_key=True, nullable=False)
    sns_id = Column(Text, primary_key=True, nullable=False)

    created_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"))
    updated_at = Column(DateTime, nullable=False, default=text("timezone('utc', now())"),
                        onupdate=text("timezone('utc', now())"))

    purchase_intents = Column(ARRAY(SmallInteger), nullable=False)
    payload = Column(JSONB)

    def __repr__(self):
        return '%s:%s-%s' % (self.__class__.__name__, self.sns_name, self.sns_id)
