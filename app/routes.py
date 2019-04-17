#coding:utf-8
from app import app
from flask import render_template, flash, redirect, url_for
from forms import LoginForm
from app.models import User
from flask_login import current_user, login_user, login_required, logout_user
from flask import request
from werkzeug.urls import url_parse
from app.forms import RegistrationForm
from app import db


@app.route('/login', methods=['GET','POST'])
def login():
    #判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    #创建一个表单实例
    form = LoginForm()
    #验证表格中的数据格式是否正确
    if form.validate_on_submit():
        #根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
        user = User.query.filter_by(username=form.username.data).first()
        #判断用户不存在或者密码不正确
        if user is None or not user.check_password(form.password.data):
            #如果用户不存在或者密码不正确就会闪现这条信息
            flash(u'无效的用户名或密码')
            # flash('Logon failure: unknown user name or bad password.')
            #然后重定向到登录前页面
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        #闪现的信息会出现在页面，当然在页面上要设置
        # flash(u'用户登录的名户名是:{} , 是否记住我:{}'.format(
        #    form.username.data,form.remember_me.data))
        next_page = request.args.get('next')
        #如果next_page记录的地址不存在那么就返回首页
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        #重定向至首页
        return redirect(next_page)
    #首次登录/数据格式错误都会是在登录界面
    return render_template('login.html',title='Login',form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(u'恭喜你成为我们网站的新用户!')
        return redirect(url_for('login'))
    return render_template('register.html', title=u'注册', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
@app.route("/index")
@login_required
def index():
    user = {"username": u"你好亚"}
    posts = [{"author": {"username": u"阿强子"},
              "body": u"我是阿强子阿！！"},
             {"author": {"username": u"阿z子"},
              "body": u"我是阿z子阿！！"}]
    return render_template("index.html", title="WORLD!", user=user, posts=posts)


@app.route("/imges")
@login_required
def imges():
    user = {"username": u"你好亚"}
    posts = [{"author": {"username": u"阿强子"},
              "body": u"我是阿强子阿！！"},
             {"author": {"username": u"阿z子"},
              "body": u"我是阿z子阿！！"}]
    img_src = ["%d.png"%i for i in range(1,9)]
    btn_src = ["%d.gif"%i for i in range(1,9)]
    return render_template("imges.html", title="WORLD!", user=user, posts=posts, btn_src=btn_src, img_src=img_src)
