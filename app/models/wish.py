from flask import current_app
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, desc, func
from sqlalchemy.orm import relationship

from app.models.base import Base, db
from app.spider.yushu_book import YuShuBook


class Wish(Base):
    id = Column(Integer, primary_key=True)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)


    @classmethod
    def get_user_wishes(cls, uid):
        wishes = Wish.query.filter_by(uid=uid, launched=False).order_by(
            desc(Wish.create_time)).all()
        return wishes

    @classmethod
    def get_gift_counts(cls, isbn_list):
        from app.models.gift import Gift
        # 注意filter和filter_by的区别，filter中传入的是表达式，
        # 且query括号里传入什么就查询什么，传入Wish，则查模型，传入count则传数量
        count_list = db.session.query(func.count(), Gift.isbn).filter(Gift.launched == False,
                                                                      Gift.isbn.in_(isbn_list),
                                                                      Gift.status == 1).group_by(
            Gift.isbn).all()

        count_list = [{'count': g[0], 'isbn': g[1]} for g in count_list]
        return count_list


    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def recent(self):
        # 遇到all()或者first()才会生成对应的SQL语句去数据库进行查找
        recent_wish = Wish.query.filter_by(
            launched=False).group_by(
            Wish.isbn).order_by(
            desc(Wish.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).distinct().all()
        return recent_wish
