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
        
        if not new_password or len(new_password) < 6:
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
        try:
            settings.primary_color = request.form.get('primary_color')
            settings.secondary_color = request.form.get('secondary_color')
            settings.background_color = request.form.get('background_color')
            settings.font_color = request.form.get('font_color')
            settings.header_background = request.form.get('header_background')
            settings.secondary_text_color = request.form.get('secondary_text_color')
            settings.font_family = request.form.get('font_family')
            settings.button_border_radius = request.form.get('button_border_radius')
            settings.button_border_width = request.form.get('button_border_width')
            settings.button_border_color = request.form.get('button_border_color')
            settings.input_border_radius = request.form.get('input_border_radius')
            settings.input_border_width = request.form.get('input_border_width')
            settings.input_border_color = request.form.get('input_border_color')
            settings.button_background_color = request.form.get('button_background_color')
            settings.button_text_color = request.form.get('button_text_color')
            settings.tool_card_border_color = request.form.get('tool_card_border_color')
            settings.tool_card_border_width = request.form.get('tool_card_border_width')
            settings.tool_card_border_style = request.form.get('tool_card_border_style')
            settings.link_color = request.form.get('link_color')
            settings.link_hover_color = request.form.get('link_hover_color')
            settings.category_badge_color = request.form.get('category_badge_color')
            settings.category_badge_hover_color = request.form.get('category_badge_hover_color')
            settings.nav_link_color = request.form.get('nav_link_color')
            settings.nav_link_hover_color = request.form.get('nav_link_hover_color')
            
            db.session.commit()
            flash('Appearance settings updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating appearance settings: {str(e)}', 'danger')
        
        return redirect(url_for('admin.appearance'))
    
    return render_template('admin/appearance.html', settings=settings)

@admin.route('/admin/categories')
@login_required
def categories():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/admin/add-category', methods=['POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name or not description:
        flash('Both name and description are required.', 'danger')
        return redirect(url_for('admin.categories'))
    
    if Category.query.filter_by(name=name).first():
        flash('A category with this name already exists.', 'danger')
        return redirect(url_for('admin.categories'))
    
    category = Category()
    category.name = name
    category.description = description
    
    try:
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding category: {str(e)}', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/admin/remove-category/<int:category_id>', methods=['POST'])
@login_required
def remove_category(category_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category removed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing category: {str(e)}', 'danger')
    
    return redirect(url_for('admin.categories'))
