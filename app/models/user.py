from math import floor

from flask import current_app
from sqlalchemy import Column, Integer, String, Boolean, Float
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app.libs.enums import PendingStatus
from app.libs.helper import is_isbn_or_key
from app.models.base import Base, db
from flask_login import UserMixin
from app import login_manager
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.wish import Wish
from app.spider.yushu_book import YuShuBook


class User(UserMixin, Base):
    #修改表的名字为user1
    # __table__ = 'user1'
    # 此处如果不是id这个名字，则flask-login的UserMixin的get_id无法识别
    id = Column(Integer, primary_key=True)
    nickname = Column(String(24), nullable=False)
    phone_number = Column(String(18), unique=True)
    # 修改字段的名字为Column里边的名字password
    _password = Column('password', String(255), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    beans = Column(Float, default=0)
    send_counter = Column(Integer, default=0)
    receive_counter = Column(Integer,default=0)

    # 高级写法，在内部对password加密后，在保存到数据库
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,raw):
        # 使用werkzeug提供的加密方法进行密码的加密
        self._password = generate_password_hash(raw)

    # 检查密码是否正确
    def check_password(self, raw):
        return check_password_hash(self._password, raw)

    # 检查该本书可不可以上传
    def can_save_to_list(self,isbn):
        if is_isbn_or_key(isbn) != 'isbn':
            return False
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(isbn)
        if not yushu_book.first:
            return False
        gifting = Gift.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        whishing = Wish.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        if not gifting and not whishing:
            return True
        else:
            return False

    # 将用户id生成token，用来标识重置密码的是哪个用户
    def generate_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        # token字节码转换成string
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        uid = data.get('id')
        if uid is not None:
            with db.auto_commit():
                user = User.query.get(uid)
                user.password = new_password
            return True
        else:
            return False

    def can_send_drift(self):
        if self.beans < 1:
            return False
        success_gifts_count = Gift.query.filter_by(
            uid=self.id, launched=True).count()
        success_recevice_count = Drift.query.filter_by(
            requester_id=self.id, pending=PendingStatus.Success).count()

        if floor(success_recevice_count / 2) <= floor(success_gifts_count):
            return True
        else:
            return False

    # 用户信息简介
    @property
    def summary(self):
        return dict(
            nickname=self.nickname,
            beans=self.beans,
            email=self.email,
            send_receive=str(self.send_counter) + '/' + str(self.receive_counter)
        )


    # flask-login已经在UserMixin中定义了这个方法，只需在模型中继承就可以了
    # def get_id(self):
    #     return self.id

# 高级用法，访问控制权限，将user转化成了对象关系模型，供后面保存在current_user中，供后面调用current_user
@login_manager.user_loader
def get_user(uid):
    # 查询主键不要要filter,这里是为login_required准备
    return User.query.get(int(uid))
