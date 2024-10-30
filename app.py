from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'sslmode': 'require'
    }
}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

@app.template_filter('parse_json')
def parse_json_filter(value):
    try:
        return json.loads(value) if value else []
    except:
        return []

# Register all blueprints
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint)

from api import api as api_blueprint
app.register_blueprint(api_blueprint)

from blog import blog as blog_blueprint
app.register_blueprint(blog_blueprint)

# Import routes after registering blueprints
import routes
