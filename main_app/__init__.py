from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = 'fucking lady fucking guy after fucking telling lie.'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'wprince00@gmail.com'
app.config['MAIL_PASSWORD'] = 'sh018019'
mail= Mail(app)

from main_app import routes


# https://myaccount.google.com/u/1/lesssecureapps?pli=1&pageId=none