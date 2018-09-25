from flask import flash, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from sqlalchemy import or_, desc

from app.forms.book import DriftForm
from app.libs.email import send_email
from app.libs.enums import PendingStatus
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.user import User
from app.models.wish import Wish
from app.view_models.book import BookViewModel
from app.view_models.drift import DriftCollection
from . import web

__author__ = '七月'


@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    current_gift = Gift.query.get_or_404(gid)

    if current_gift.is_yourself_gift(current_user.id):
        flash('这本书是您自己的，不能向自己索要书籍')
        return redirect(url_for('web.book_detail', isbn=current_gift.isbn))
    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enough_beans.html', beans=current_user.beans)

    form = DriftForm(request.form)
    if request.method == 'POST' and form.validate():
        save_drift(form, current_gift)

        send_email(current_gift.user.email,'有人想要一本书', 'email/get_gift',
                   wisher = current_user,
                   gift = current_gift)
        return redirect(url_for('web.pending'))
    # 获取书籍赠送人
    gifter = current_gift.user.summary
    return render_template('drift.html',
                           gifter=gifter, user_beans=current_user.beans, form=form)


@web.route('/pending')
@login_required
def pending():
    # 或关系
    drifts = Drift.query.filter(
        or_(Drift.requester_id == current_user.id,
            Drift.gifter_id == current_user.id)).order_by(
        desc(Drift.create_time)).all()

    views = DriftCollection(drifts, current_user.id)
    return render_template('pending.html', drifts=views.data)


@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    with db.auto_commit():
        drift = Drift.query.filter(Gift.uid == current_user.id,
                                   Drift.id == did).first_or_404()
        drift.pending = PendingStatus.Reject
        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    with db.auto_commit():
        drift = Drift.query.filter_by(
            requester_id=current_user.id,
            id = did).first_or_404()
        # 枚举不能直接赋值给数字,在Drift模型中已处理
        drift.pending = PendingStatus.Redraw
        current_user.beans += 1

    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/mailed')
@login_required
def mailed_drift(did):
    # 事务的支持很重要
    with db.auto_commit():
        drift = Drift.query.filter_by(gifter_id = current_user.id,
                                      id = did).first_or_404()
        drift.pending = PendingStatus.Success
        current_user.beans += 1

        # 将自己礼物清单更新,两种写法可以任选
        gift = Gift.query.filter_by(id=drift.gifter_id).first_or_404()
        gift.launched = True

        # 将索要者的心愿清单更新
        Wish.query.filter_by(isbn=drift.isbn, uid=drift.requester_id,
                             launched=False).upadate({Wish.launched: True})

    return redirect(url_for('web.pending'))


def save_drift(dirft_form, current_gift):
    with db.auto_commit():
        drift = Drift()
        # 高级用法，将form中所有数据拷贝到模型中。但要确保两边名称一样
        dirft_form.populate_obj(drift)
        drift.gift_id = current_gift.id
        drift.requester_id = current_user.id
        drift.requester_nickname = current_user.nickname
        drift.gifter_nickname = current_gift.user.nickname
        drift.gifter_id = current_gift.user.id

        book = BookViewModel(current_gift.book)

        drift.book_title = book.title
        drift.book_author = book.author
        drift.book_img = book.image
        drift.isbn = book.isbn
        current_user.beans -= 1

        db.session.add(drift)

