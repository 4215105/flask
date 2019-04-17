#coding:utf8
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    #设置密匙要没有规律，别被人轻易猜到哦
    SECRET_KEY = 'a9087FFJFF9nnvc2@#$%FSD'
    #格式为mysql+pymysql://数据库用户名:密码@数据库地址:端口号/数据库的名字?数据库格式
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flask:flask@localhost:3306/flask_object?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
