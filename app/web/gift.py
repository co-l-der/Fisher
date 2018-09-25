from flask import current_app, flash, render_template, redirect, url_for

from app.libs.enums import PendingStatus
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.view_models.trade import MyTrades
from . import web
from flask_login import login_required, current_user

@web.route('/my/gifts')
@login_required
def my_gifts():
    uid = current_user.id
    gifts_of_mine = Gift.get_user_gifts(uid)
    isbn_list = [gift.isbn for gift in gifts_of_mine]
    wish_count_list = Gift.get_wish_counts(isbn_list)
    view_model = MyTrades(gifts_of_mine, wish_count_list)
    return render_template('my_gifts.html', gifts=view_model.trades)


@web.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    # 在登录的时候保存了用户模型，见User类中的get_user(uid)
    if current_user.can_save_to_list(isbn):
        # 一个事务，如果出现异常一定要回滚，不然会导致下次插入数据也失败
        # 只要有session的地方一定有try except，并进行回滚操作
        # 使用的是contextmanager的高级用法，上下文管理器
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)
            db.session.commit()

    else:
        flash('这本书已添加至您的赠送清单或已存在于您的心愿清单，请不要重复添加')
    return redirect(url_for('web.book_detail', isbn=isbn))



@web.route('/gifts/<gid>/redraw')
@login_required
def redraw_from_gifts(gid):
    gift = Gift.query.filter_by(id=gid, launched=False).first_or_404()
    drift = Drift.query.filter_by(gift_id=gid,pending=PendingStatus.Waiting)
    if drift:
        flash('这个礼物正处于交易状态，请先前往鱼漂完成该交易')
    else:
        with db.auto_commit():
            current_user.beans -= current_app.config['BEAN_UPLOAD_ONE_BOOK']
            gift.delete()

    return redirect(url_for('web.my_gifts'))

