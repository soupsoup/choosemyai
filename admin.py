from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import AppearanceSettings, Category

admin = Blueprint('admin', __name__)

@admin.route('/admin/appearance', methods=['GET', 'POST'])
@login_required
def appearance():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    settings = AppearanceSettings.get_settings()
    
    if request.method == 'POST':
        settings.primary_color = request.form.get('primary_color', settings.primary_color)
        settings.secondary_color = request.form.get('secondary_color', settings.secondary_color)
        settings.background_color = request.form.get('background_color', settings.background_color)
        settings.header_background = request.form.get('header_background', settings.header_background)
        settings.font_family = request.form.get('font_family', settings.font_family)
        settings.font_color = request.form.get('font_color', settings.font_color)
        
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

@admin.route('/admin/categories/add', methods=['POST'])
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
    
    category = Category()
    category.name = name
    category.description = description
    db.session.add(category)
    db.session.commit()
    
    flash('Category added successfully!', 'success')
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
