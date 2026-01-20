from flask import Flask
from flask_login import LoginManager
from .config import Config
from .models import db, User

login_manager = LoginManager()
login_manager.login_view = "admin.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from .public.routes import bp as public_bp
    from .admin.routes import bp as admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    return app

