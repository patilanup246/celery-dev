# Copyright (C) 2015 Xomad. All rights reserved.
#
# Created on 02/11/2015

from datetime import datetime

from sqlalchemy.ext.declarative.api import declarative_base


class Base(object):
    __column_names = None

    @classmethod
    def column_names(cls):
        if not cls.__column_names:
            cls.__column_names = {_.name for _ in cls.__table__.columns}
        return cls.__column_names

    def as_dict(self, fields=None):
        return {_.name: getattr(self, _.name) for _ in self.__table__.columns} if not fields else \
            {_.name: getattr(self, _.name) for _ in self.__table__.columns if _.name in fields}

    @classmethod
    def upsert_sql_statement(cls):
        table_name = cls.__table__.name
        primary_key = [col.name for col in cls.__table__.primary_key]
        columns = [col.name for col in cls.__table__.columns]
        primary_key_params = ','.join("{}".format(col) for col in primary_key)
        column_params = ','.join("{}".format(col) for col in columns)
        value_params = ','.join([':{}'.format(col) for col in columns])
        insert_sql = """
                INSERT INTO "{}" ({})
                VALUES ({})
                ON CONFLICT ({})
                DO 
            """.format(cls.__tablename__, column_params,
                       value_params,
                       primary_key_params)
        update_sql = """
            UPDATE SET ({}) = ({})
            RETURNING sns_name, sns_id
            """.format(column_params, value_params)
        update_sql = update_sql.replace(':sources',
                                        "CASE WHEN {table_name}.sources IS NULL OR NOT {table_name}.sources @> :sources"
                                        " THEN (array_cat({table_name}.sources, :sources)) "
                                        "ELSE {table_name}.sources END".format(table_name=table_name))
        upsert_sql = "{} {}".format(insert_sql, update_sql)
        return upsert_sql


    @property
    def dict(self):
        d = {}
        for column_name in self.column_names():
            value = getattr(self, column_name)
            if isinstance(value, datetime):
                d[column_name] = value.isoformat()
            else:
                d[column_name] = value
        return d

    def update_from_dict(self, a_dict):
        for column_name in self.column_names():
            if column_name in a_dict and getattr(self, column_name) != a_dict[column_name]:
                setattr(self, column_name, a_dict[column_name])


Base = declarative_base(cls=Base)
