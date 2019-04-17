#coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError,Email,EqualTo
from app.models import User

class LoginForm(FlaskForm):
    #DataRequired，当你在当前表格没有输入而直接到下一个表格时会提示你输入
    username = StringField(u'用户名',validators=[DataRequired(message=u'请输入名户名')])
    password = PasswordField(u'密码',validators=[DataRequired(message=u'请输入密码')])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录')

class RegistrationForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired(), Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    password2 = PasswordField(
        u'重复密码', validators=[DataRequired(), EqualTo(u'password')])
    submit = SubmitField(u'注册')
    #校验用户名是否重复
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(u'用户名重复了，请您重新换一个呗!')
    #校验邮箱是否重复
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(u'邮箱重复了，请您重新换一个呗!')
