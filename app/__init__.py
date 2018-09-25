from flask import Flask
from app.models.base import db
from flask_login import LoginManager
from flask_mail import Mail

login_manager = LoginManager()
mail = Mail()

# 创建和初始化app
def create_app():
    app = Flask(__name__)
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    register_blueprint(app)

    db.init_app(app)
    login_manager.init_app(app)
    # 登录权限控制，如果用户没登录则重定向到login页面
    login_manager.login_view = 'web.login'
    # 重定向到Login页面的提示信息
    login_manager.login_message = '请先登录或注册'

    #注册mail插件
    mail.init_app(app)

    db.create_all(app=app)

    return app

# 使用app注册蓝图
def register_blueprint(app):
    from app.web import web
    app.register_blueprint(web)

