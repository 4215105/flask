# coding:utf8
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from app import app
import sys
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemy as whooshalchemy


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # back是反向引用,User和Post是一对多的关系，backref是表示在Post中新建一个属性author，关联的是Post中的user_id外键关联的User对象。
    # lazy属性常用的值的含义，select就是访问到属性的时候，就会全部加载该属性的数据;joined则是在对关联的两个表进行join操作，从而获取到所有相关的对象;dynamic则不一样，在访问属性的时候，并没有在内存中加载数据，而是返回一个query对象, 需要执行相应方法才可以获取对象，比如.all()
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def __repr__(self):
        return '<用户名:{}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(Post.timestamp.desc())


class Post(db.Model):
    __searchable__ = ['body']
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

if enable_search:
    whooshalchemy.whoosh_index(app, Post)

# @NOTE 暂时不知道杂使用
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# u = User(username='king',email='king@qq.com')
# db.session.add(u)
# db.session.commit()
# p1 = Post(body='我第一次提交数据！',author=u)
# p2 = Post(body='我第二次提交数据了！',author=u)
# db.session.add(p)
# db.session.commit()
# u = User.query.get(1)
# posts = u.posts.all()
# posts >>> [<Post 我第一次提交数据！>, <Post 我第二次提交数据了！>]
# u = User.query.get(2)
# u.posts.all() >>> []
# posts = Post.query.all()
# for p in posts:
#     print(p.id,p.author.username,p.body)
# >>> 1 duke 我第一次提交数据！
#     2 duke 我第二次提交数据了！
# User.query.order_by(User.username.desc()).all()

# users = User.query.all()
# for u in users:
#     db.session.delete(u)
# posts = Post.query.all()
# for p in posts:
#     db.session.delete(p)
# db.session.commit()
#
