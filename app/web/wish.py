from flask import flash, url_for, render_template
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app.libs.email import send_email
from app.models.base import db
from app.models.gift import Gift
from app.models.wish import Wish
from app.view_models.trade import MyTrades
from . import web

__author__ = '七月'


@web.route('/my/wish')
@login_required
def my_wish():

    uid = current_user.id
    wishes_of_mine = Wish.get_user_wishes(uid)
    isbn_list = [wish.isbn for wish in wishes_of_mine]
    gift_count_list = Wish.get_gift_counts(isbn_list)
    view_model = MyTrades(wishes_of_mine, gift_count_list)
    return render_template('my_wish.html', wishes=view_model.trades)


@web.route('/wish/book/<isbn>')
@login_required
def save_to_wish(isbn):
    # 在登录的时候保存了用户模型，见User类中的get_user(uid)
    if current_user.can_save_to_list(isbn):
        # 一个事务，如果出现异常一定要回滚，不然会导致下次插入数据也失败
        # 只要有session的地方一定有try except，并进行回滚操作
        # 使用的是contextmanager的高级用法，上下文管理器
        with db.auto_commit():
            wish = Wish()
            wish.isbn = isbn
            wish.uid = current_user.id
            db.session.add(wish)

    else:
        flash('这本书已添加至您的赠送清单或已存在于您的心愿清单，请不要重复添加')
    return redirect(url_for('web.book_detail', isbn=isbn))

@web.route('/satisfy/wish/<int:wid>')
def satisfy_wish(wid):
    wish = Wish.query.get_or_404(wid)
    gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first()
    if not gift:
        flash('你还没有上传此书，'
              '请点击“添加到赠送清单”添加此书。')
    else:
        send_email(wish.user.email,
                  '有人想送你一本书', 'email/satisify_wish',wish=wish,
                  gift=gift)
        flash('已向他发送了一封邮件，如果他愿意接受你的赠送，你将收到一个鱼漂')
    return redirect(url_for('web.book_detail', isbn=wish.isbn))



@web.route('/wish/book/<isbn>/redraw')
def redraw_from_wish(isbn):
    wish = Wish.query.filter_by(isbn=isbn, launched=False).first_or_404()
    with db.auto_commit():
        wish.delete()
    return redirect(url_for('web.my_wish'))
