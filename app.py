import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)

# Setup configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "ai-tools-directory-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['WTF_CSRF_ENABLED'] = True  # Re-enable CSRF protection

# Initialize the app with the extensions
db.init_app(app)
login_manager.init_app(app)

# Import blueprints before setting login_view
from auth import auth  # noqa: F401, E402
app.register_blueprint(auth)

# Set login_view after auth blueprint is registered
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

with app.app_context():
    import models  # noqa: F401
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    db.create_all()

# Import and register other blueprints
from routes import *  # noqa: F401, E402
from api import api  # Import the API blueprint
from admin import admin  # Import the admin blueprint
app.register_blueprint(api)  # Register the API blueprint
app.register_blueprint(admin)  # Register the admin blueprint
