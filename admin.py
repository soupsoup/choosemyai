from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import AppearanceSettings, Category, Tool
from datetime import datetime
import json

admin = Blueprint('admin', __name__)

@admin.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('admin.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('admin.change_password'))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('admin.change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('admin/change_password.html')

@admin.route('/admin/appearance', methods=['GET', 'POST'])
@login_required
def appearance():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    settings = AppearanceSettings.get_settings()
    
    if request.method == 'POST':
        color_fields = [
            'primary_color', 'secondary_color', 'background_color',
            'font_color', 'header_background', 'secondary_text_color',
            'placeholder_text_color'
        ]
        
        for field in color_fields:
            value = request.form.get(field)
            if value and value.startswith('#'):
                setattr(settings, field, value)
        
        settings.font_family = request.form.get('font_family', settings.font_family)
        db.session.commit()
        flash('Appearance settings updated successfully!', 'success')
        return redirect(url_for('admin.appearance'))
    
    return render_template('admin/appearance.html', settings=settings)

@admin.route('/admin/categories', methods=['GET'])
@login_required
def categories():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

# ... rest of the admin.py file remains unchanged ...
