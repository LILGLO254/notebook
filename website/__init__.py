
from flask import Flask
from flask_login import LoginManager

from .models import get_user_by_id


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "initkey"

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    return app
