from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask import __init__
from app.views import main_bp

app = Flask(__name__)
app.config.from_object(__init__)

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)