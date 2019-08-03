from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime, Text, Float
from xde.models import Base


class TsPost(Base):
    __table_args__ = {'schema': 'public'}
    __tablename__ = 'ts_post'

    ts = Column(DateTime, primary_key=True, nullable=False)
    sns_id = Column(Text, primary_key=True, nullable=False)
    sns_name = Column(Text, primary_key=True, nullable=False)
    metric_name = Column(Text, primary_key=True, nullable=False)
    value = Column(Float)
    user_sns_id = Column(Text)

    def __repr__(self):
        return '%s:%s-%s-%s' % (self.__class__.__name__, self.sns_name, self.sns_id, self.ts)
