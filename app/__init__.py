from flask import Flask
import cloudinary

from app.auth import auth_bp
from app.booking import booking_bp
from app.courts import courts_bp
from app.extention import db, login_manager

app = Flask(__name__)


app.secret_key = 'aaaaaaaaaa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/sportdb?charset=utf8mb4'
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

app.register_blueprint(auth_bp)
app.register_blueprint(courts_bp)
app.register_blueprint(booking_bp)

