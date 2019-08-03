# Copyright (C) 2015 Xomad. All rights reserved.
#
# This software is the confidential and proprietary information of
# Xomad or one of its subsidiaries. You shall not disclose this
# confidential information and shall use it only in accordance with
# the terms of the license agreement or other applicable agreement you
# entered into with Xomad.
#
# XOMAD MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT. XOMAD
# SHALL NOT BE LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE
# AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS
# DERIVATIVES.
#
# Created on 28/11/2015

from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime, Text

from xde.models import Base


class SnsFollower(Base):
    __table_args__ = (
        ForeignKeyConstraint(
            ['sns_name', 'sns_id'],
            ['public.sns_account.sns_name', 'public.sns_account.sns_id'],
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        UniqueConstraint('sns_name', 'sns_id', 'follower_id', name='sns_follower_sns_name_sns_id_follower_id_key'),
        {'schema': 'public'}
    )
    __tablename__ = 'sns_follower'

    sns_name = Column(Text, primary_key=True, nullable=False)
    sns_id = Column(Text, primary_key=True, nullable=False)
    username = Column(Text)
    follower_id = Column(Text, primary_key=True, nullable=False)
    follower_username = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, default=text("timezone('utc', now())"),
                        onupdate=text("timezone('utc', now())"))

    def __repr__(self):
        return '%s:%s-%s:%s' % (self.__class__.__name__, self.sns_name, self.sns_id, self.follower_id)
