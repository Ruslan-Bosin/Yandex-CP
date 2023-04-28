from flask import Flask, render_template
from loguru import logger
from peewee import SqliteDatabase
from flask_login import LoginManager
from config import LOG_NAME, LOG_ROTATION, SECRET_KEY, SERVICE_DATABASE, MAX_CONTENT_LENGTH
from flask_sqlalchemy import SQLAlchemy

# Создание основного web приложения
app: Flask = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

import os
import run
basedir = os.path.abspath(os.path.dirname(run.__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Добавление файла сохранения log-ов
logger.add(
    sink=LOG_NAME,
    level="DEBUG",
    rotation=LOG_ROTATION,
    compression="zip",
)

# Создание базы данных
# service_db = SqliteDatabase(SERVICE_DATABASE)

# Настройка flask-login
login_manager = LoginManager(app=app)
login_manager.login_view = "select_role"
login_manager.login_message = ""

# Подключение отслеживания URL
from app import routes
from app import rest
from app.login import load_user
