from threading import Thread
from flask import current_app, render_template
from flask_mail import Message

# 异步发送邮件
from app import mail


def send_async_email(app, msg):
    # 高级用法，上下文管理器，会自动入栈和出栈
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            pass


def send_email(to, subject, template, **kwargs):
    # 这里一定要拿到app，而不是current_app，因为current_app是代理对象，两个线程中使用会出现线程隔离
    app = current_app._get_current_object()
    msg = Message('[鱼书]' + ' ' + subject,
                  sender=app.config['MAIL_USERNAME'], recipients=[to])
    # msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

def _send_email():
    msg = Message('测试邮件',sender='1542734106@qq.com', body = 'Test',
                  recipients=['1542734106@qq.com'])
    mail.send(msg)
    pass
