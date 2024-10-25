from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import AppearanceSettings, Category, Tool
from datetime import datetime
import json
import logging

admin = Blueprint('admin', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    try:
        logger.info("Attempting to retrieve appearance settings")
        settings = AppearanceSettings.get_settings()
        logger.info(f"Settings retrieved: {settings is not None}")
        
        if request.method == 'POST':
            try:
                logger.info("Processing POST request")
                color_fields = [
                    'primary_color', 'secondary_color', 'background_color',
                    'font_color', 'header_background', 'secondary_text_color',
                    'placeholder_text_color'
                ]
                
                for field in color_fields:
                    value = request.form.get(field)
                    logger.info(f"Processing field {field} with value {value}")
                    if value and value.startswith('#'):
                        setattr(settings, field, value)
                        logger.info(f"Updated {field} to {value}")
                
                settings.font_family = request.form.get('font_family', settings.font_family)
                logger.info(f"Updated font_family to {settings.font_family}")
                
                db.session.commit()
                logger.info("Successfully saved appearance settings")
                flash('Appearance settings updated successfully!', 'success')
                return redirect(url_for('admin.appearance'))
                
            except Exception as e:
                logger.error(f"Error in POST request: {str(e)}")
                db.session.rollback()
                flash('Error updating settings. Please try again.', 'danger')
                return redirect(url_for('admin.appearance'))
        
        return render_template('admin/appearance.html', settings=settings)
        
    except Exception as e:
        logger.error(f"Error in appearance route: {str(e)}")
        flash('Error loading appearance settings. Please try again.', 'danger')
        return redirect(url_for('index'))

@admin.route('/admin/categories', methods=['GET'])
@login_required
def categories():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/admin/categories/add', methods=['POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if name and description:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
    else:
        flash('Name and description are required.', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/admin/categories/<int:category_id>/remove', methods=['POST'])
@login_required
def remove_category(category_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category removed successfully!', 'success')
    return redirect(url_for('admin.categories'))
