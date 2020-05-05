# coding:utf8
import os

# -*- coding: utf-8 -*-
# ...
# available languages
LANGUAGES = {
    'en': 'English',
    'zh': 'Chinese'
}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
# pagination
POSTS_PER_PAGE = 3
WHOOSH_BASE = os.path.join(BASE_DIR, 'search.db')
MAX_SEARCH_RESULTS = 50
ADMINS = ['413115175@qq.com']
MS_TRANSLATOR_CLIENT_ID = '20200505000440528'
MS_TRANSLATOR_CLIENT_SECRET = '54WFe_r77QN9O4sHYCoH'

class Config(object):
    # 设置密匙要没有规律，别被人轻易猜到哦
    SECRET_KEY = 'a9087FFJFF9nnvc2@#$%FSD'
    # 格式为mysql+pymysql://数据库用户名:密码@数据库地址:端口号/数据库的名字?数据库格式
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'db_repository')
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flask:flask@localhost:3306/flask_object?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # email server
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USERNAME = '413115175@qq.com'
    MAIL_PASSWORD = 'opekjyktlsyjbied'

    # administrator list

