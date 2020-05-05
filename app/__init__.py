# coding:utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# 导入配置文件
from config import Config
from flask_mail import Mail
from momentjs import momentjs
from flask_babel import Babel
from flask_babel import gettext, lazy_gettext
from flask_json import FlaskJSON

class CustomJSONEncoder(FlaskJSON):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)






app = Flask(__name__)
app.jinja_env.globals['momentjs'] = momentjs
app.config.from_object(Config)

babel = Babel(app)
# app.json_encoder = FlaskJSON
mail = Mail(app)
# 建立数据库关系
db = SQLAlchemy(app)
# 绑定app和数据库，以便进行操作
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = lazy_gettext('Please log in to access this page.')

from app import routes, models
