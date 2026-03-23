from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Thay đổi user, password, host, port và ten_db cho đúng với MySQL của bạn
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/sportdb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)