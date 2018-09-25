from wtforms import Form, StringField,  PasswordField
from wtforms.validators import Length, DataRequired, Email, ValidationError, EqualTo

from app.models.user import User


class RegisterForm(Form):
    email = StringField(validators=[DataRequired(),Length(8, 64),
                                    Email(message='电子邮箱不符合规范')])
    nickname = StringField('昵称', validators=[
        DataRequired(), Length(2, 10, message='昵称至少需要两个字符，最多10个字符')])

    password = PasswordField('密码', validators=[
        DataRequired(), Length(6, 20)])

    # 自定义验证器，flask自动根据下划线后面的email对form中输入的email做校验
    def validate_email(self,field):
        # 快速查询不用db.session，而是如下方法
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('电子邮件已被注册')


class EmailForm(Form):
    email = StringField(validators=[DataRequired(), Length(8, 64),
                                    Email(message='电子邮箱不符合规范')])

class LoginForm(EmailForm):
    password = PasswordField('密码', validators=[
        DataRequired(), Length(6, 20)])

class ResetPasswordForm(Form):
    password1 = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 20, message='密码长度至少需要在6到20个字符之间'),
        EqualTo('password2', message='两次输入的密码不相同')])
    password2 = PasswordField('确认新密码', validators=[
        DataRequired(), Length(6, 20)])


class ChangePasswordForm(Form):
    old_password = PasswordField('原有密码', validators=[DataRequired()])
    new_password1 = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 10, message='密码长度至少需要在6到20个字符之间'),
        EqualTo('new_password2', message='两次输入的密码不一致')])
    new_password2 = PasswordField('确认新密码字段', validators=[DataRequired()])

