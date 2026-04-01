from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import cloudinary

app = Flask(__name__)
app.secret_key = 'aaaaaaaaaa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/sportdb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PAGE_SIZE"] = 6

db = SQLAlchemy(app)

login = LoginManager(app=app)

cloudinary.config(cloud_name='dxxwcby8l',
                  api_key='792844686918347',
                  api_secret='T8ys_Z9zaKSqmKWa4K1RY6DXUJg')