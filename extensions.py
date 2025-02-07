from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
import bcrypt


class FlaskBcrypt:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass

    def generate_password_hash(self, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password, salt)

    def check_password_hash(self, pw_hash, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(pw_hash, str):
            pw_hash = pw_hash.encode('utf-8')
        try:
            return bcrypt.checkpw(password, pw_hash)
        except Exception:
            return False


bcrypt_instance = FlaskBcrypt()
# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
ma = Marshmallow()
jwt = JWTManager()
