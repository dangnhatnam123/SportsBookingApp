from app import app
from app.auth.views import auth_bp
from app.courts.views import courts_bp
from app.booking.views import booking_bp
from app.staff.views import staff_bp
from app.admin.views import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(courts_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)