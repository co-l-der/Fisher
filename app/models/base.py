from datetime import datetime
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import Column, SmallInteger, Integer

# 高级用法，继承父类的Query,改写filter_by,以后的查询都会有status
class Query(BaseQuery):
    def filter_by(self, **kwargs):
        # 取字典中的所有key
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)


#contextmanager的高级用法
class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

db = SQLAlchemy(query_class=Query)

class Base(db.Model):
    # 设置为True是为了告诉Flask不用创建Base这张表
    __abstract__ = True
    create_time = Column('create_time', Integer)
    status = Column(SmallInteger, default=1)

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    # 高级用法，如果字典中有和Model中相同名字的key，则自动赋值
    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self,key) and key != 'id':
                setattr(self,key,value)

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    # 软删除
    def delete(self):
        self.status = 0

