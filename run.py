from app import app
from app.views import main_bp
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)