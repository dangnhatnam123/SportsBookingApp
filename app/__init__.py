from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary


db = SQLAlchemy()
login_manager = LoginManager()

app = Flask(__name__)


app.secret_key = 'aaaaaaaaaa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3307/sportdb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PAGE_SIZE"] = 6

cloudinary.config(
    cloud_name='dxxwcby8l',
    api_key='792844686918347',
    api_secret='T8ys_Z9zaKSqmKWa4K1RY6DXUJg'
)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth_bp.login_view'


