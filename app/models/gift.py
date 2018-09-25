from flask import current_app
from sqlalchemy import Column, Integer, Boolean, ForeignKey, String,  desc, func
from sqlalchemy.orm import relationship

from app.models.base import Base, db

from app.spider.yushu_book import YuShuBook
from collections import namedtuple

# 高级方法，快速将一个复合列表定义成一个对象
# 第一个元素代表'EachGiftWishCount'代表对象，第二个代表对象属性
# EachGiftWishCount = namedtuple('EachGiftWishCount', ['count', 'isbn'])


class Gift(Base):
    id = Column(Integer, primary_key=True)
    user = relationship('User')
    uid = Column(Integer,ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)

    @classmethod
    def get_user_gifts(cls, uid):
        gifts = Gift.query.filter_by(uid=uid, launched=False).order_by(
            desc(Gift.create_time)).all()
        return gifts

    @classmethod
    def get_wish_counts(cls, isbn_list):
        from app.models.wish import Wish
        # 注意filter和filter_by的区别，filter中传入的是表达式，
        # 且query括号里传入什么就查询什么，传入Wish，则查模型，传入count则传数量
        count_list = db.session.query(func.count(), Wish.isbn).filter(Wish.launched == False,
                                             Wish.isbn.in_(isbn_list),
                                             Wish.status == 1).group_by(
            Wish.isbn).all()
        count_list = [{'count':w[0], 'isbn':w[1]} for w in count_list]
        return count_list

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def recent(self):
        # 遇到all()或者first()才会生成对应的SQL语句去数据库进行查找
        recent_gift = Gift.query.filter_by(
            launched=False).group_by(
            Gift.isbn).order_by(
            desc(Gift.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).distinct().all()
        return recent_gift

    def is_yourself_gift(self, uid):
        if self.uid == uid:
            return True
        else:
            return False
    # @classmethod
    # def get_wish_counts(cls, isbn_list):
    #     # 注意filter和filter_by的区别，filter中传入的是表达式，
    #     # 且query括号里传入什么就查询什么，传入Wish，则查模型，传入count则传数量
    #     count_list = db.session.query(func.count(), Wish.isbn).filter(Wish.launched == False,
    #                                          Wish.isbn.in_(isbn_list),
    #                                          Wish.status == 1).group_by(
    #         Wish.isbn).all()
    #     count_list = [EachGiftWishCount(w[0], w[1]) for w in count_list]
    #     return count_list