# coding:utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# 导入配置文件
from config import Config
from flask_mail import Mail
from momentjs import momentjs


app = Flask(__name__)
app.jinja_env.globals['momentjs'] = momentjs
app.config.from_object(Config)
mail = Mail(app)
# 建立数据库关系
db = SQLAlchemy(app)
# 绑定app和数据库，以便进行操作
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
