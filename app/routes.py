# coding:utf-8
import os
from datetime import datetime
from app import app
from flask import render_template, flash, redirect, url_for, g
from forms import LoginForm, EditForm, PostForm
from app.models import User, Post
from flask_login import current_user, login_user, login_required, logout_user
from flask import request
from werkzeug.urls import url_parse
from app.forms import RegistrationForm
from app import db
from config import POSTS_PER_PAGE
from forms import SearchForm, DownloadForm
from config import MAX_SEARCH_RESULTS
from emails import follower_notification
from app import babel
from config import LANGUAGES
from flask_babel import gettext
from guess_language import guessLanguage
from flask import jsonify, Response
from translate import baidu_translate
from werkzeug import secure_filename
from flask import send_from_directory
from redis import StrictRedis


rds = StrictRedis(db=3)


# 消息生成器
def event_stream():
    # 从数据库连接上获取发布订阅管理对象实例
    pub = rds.pubsub()
    # 在管理订阅(建立通道)频道
    pub.subscribe('chat')
    # 监听频道信息
    for message in pub.listen():
        print(type(message['data']), type(message), message)
        # 只响应有消息的（字节），首次无消息返回的为int状态码对象，直接忽略
        if isinstance(message['data'], bytes):
            # 转为utf8字符串，发送 SSE（Server Send Event）协议格式的数据
            yield 'data: %s\n\n' % message['data'].decode()

@login_required
@app.route('/chat')
def chat_home():
    user = g.user
    return render_template('chat.html', user=user)

@login_required
@app.route('/chat/<username>')
def chat(username=None):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    # 通过路由参数或querystring动注册为当前用户
    if user or len(request.args) > 0:
        # 消息闪现（存储在session内，模板页用完即丢）
        flash(username + u'已经成功登录，加入聊天室！')

    # 模板渲染
    data = {
        "user": user,
        "tip": u"正在聊天中..."
    }
    # 关键字参数解包，返回元组（框架会自动解析为一个完整的response对象）
    return render_template('chat.html', **data), 200


# 接收js发送过来的消息
@login_required
@app.route('/chatpost', methods=['POST'])
def chat_post():
    # 获取表单提交内容
    user = g.user
    message = request.form['message']
    # 返回一个指定字段的时间值
    now = datetime.datetime.now().replace(microsecond=0).time()
    # 通过频道发布消息
    rds.publish('chat', u'[%s] %s: %s' % (now.isoformat(), user, message))
    # 响应对象
    return Response(status=204)


@login_required  
@app.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")


@login_required
@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename)))
        return 'file uploaded successfully'
    return render_template('upload.html')


@login_required
@app.route('/download', methods = ['GET', 'POST'])
def download_file():
    form = DownloadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.filename.data)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], 'files')
        if os.path.exists(os.path.join(file_path, filename)):
            return send_from_directory(file_path, filename, as_attachment=True)
        return gettext("file [{0}] is not exists!".format(filename))
    return render_template('download.html', form=form)

@app.route('/translate', methods = ['POST'])
@login_required
def translate():
    return jsonify({
        'text': baidu_translate(
            request.form['text'],
            request.form['sourceLang'],
            request.form['destLang']) })
            
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = get_locale()


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # 创建一个表单实例
    form = LoginForm()
    # 验证表格中的数据格式是否正确
    if form.validate_on_submit():
        # 根据表格里的数据进行查询，如果查询到数据返回User对象，否则返回None
        user = User.query.filter_by(username=form.username.data).first()
        # 判断用户不存在或者密码不正确
        if user is None or not user.check_password(form.password.data):
            # 如果用户不存在或者密码不正确就会闪现这条信息
            flash(gettext("Logon failure: unknown user name or bad password."))
            # flash(gettext('无效的用户名或密码'))
            # flash('Logon failure: unknown user name or bad password.')
            # 然后重定向到登录前页面
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # 闪现的信息会出现在页面，当然在页面上要设置
        # flash(u'用户登录的名户名是:{} , 是否记住我:{}'.format(
        #    form.username.data,form.remember_me.data))
        next_page = request.args.get('next')
        # 如果next_page记录的地址不存在那么就返回首页
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        # 重定向至首页
        return redirect(next_page)
    # 首次登录/数据格式错误都会是在登录界面
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # 判断当前用户是否验证，如果通过的话返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = User.make_valid_username(form.username.data)
        user = User(username=username, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        # db.session.commit()
        db.session.add(user.follow(user))
        db.session.commit()
        flash(u'恭喜你成为我们网站的新用户!')
        return redirect(url_for('login'))
    return render_template('register.html', title=u'注册', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    user = g.user
    form = PostForm()
    if form.validate_on_submit():
        language = guessLanguage(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = 'en'
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user, language=language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = [{"author": {"username": u"阿强子"},
              "body": u"我是阿强子阿！！"},
             {"author": {"username": u"阿z子"},
              "body": u"我是阿z子阿！！"}]
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template("index.html", title="WORLD!", user=user, posts=posts, form=form)


@app.route("/imges")
@login_required
def imges():
    user = g.user
    posts = [{"author": {"username": u"阿强子"},
              "body": u"我是阿强子阿！！"},
             {"author": {"username": u"阿z子"},
              "body": u"我是阿z子阿！！"}]
    img_src = ["%d.png" % i for i in range(1, 9)]
    btn_src = ["%d.gif" % i for i in range(1, 9)]
    return render_template("imges.html", title="WORLD!", user=user, posts=posts, btn_src=btn_src, img_src=img_src)


@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>')
@login_required
def user(username, page=1):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        # g.user.username = form.username.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        # form.username.data = g.user.username
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form, user=g.user)


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + username + '!')
    follower_notification(user, g.user)
    return redirect(url_for('user', username=username))



@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + username + '.')
    return redirect(url_for('user', username=username))


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)



