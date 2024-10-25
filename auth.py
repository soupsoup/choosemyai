from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User
import logging

auth = Blueprint('auth', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        logger.info(f"Login attempt for username: {username}")  # Debug log
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user:
            logger.info(f"User found. Is admin: {user.is_admin}")  # Debug log
            if user.check_password(password):
                login_user(user)
                logger.info("Password correct, user logged in")  # Debug log
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('index'))
            logger.info("Password incorrect")  # Debug log
            flash('Invalid username or password', 'danger')
        else:
            logger.info("User not found")  # Debug log
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
