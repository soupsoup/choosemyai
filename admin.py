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
        settings.primary_color = request.form.get('primary_color', settings.primary_color)
        settings.secondary_color = request.form.get('secondary_color', settings.secondary_color)
        settings.background_color = request.form.get('background_color', settings.background_color)
        settings.header_background = request.form.get('header_background', settings.header_background)
        settings.font_family = request.form.get('font_family', settings.font_family)
        settings.font_color = request.form.get('font_color', settings.font_color)
        settings.secondary_text_color = request.form.get('secondary_text_color', settings.secondary_text_color)
        
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

@admin.route('/admin/tools/export', methods=['GET'])
@login_required
def export_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tools = Tool.query.all()
    export_data = []
    
    for tool in tools:
        tool_data = {
            'name': tool.name,
            'description': tool.description,
            'url': tool.url,
            'image_url': tool.image_url,
            'youtube_url': tool.youtube_url,
            'categories': [category.name for category in tool.categories],
            'is_approved': tool.is_approved
        }
        export_data.append(tool_data)
    
    return jsonify({
        'tools': export_data,
        'exported_at': datetime.utcnow().isoformat()
    })

@admin.route('/admin/tools/import', methods=['GET', 'POST'])
@login_required
def import_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('admin.import_tools'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('admin.import_tools'))
        
        if not file.filename.endswith('.json'):
            flash('Only JSON files are allowed', 'danger')
            return redirect(url_for('admin.import_tools'))
        
        try:
            import_data = json.loads(file.read().decode('utf-8'))
            tools_data = import_data.get('tools', [])
            
            for tool_data in tools_data:
                tool = Tool()
                tool.name = tool_data['name']
                tool.description = tool_data['description']
                tool.url = tool_data['url']
                tool.image_url = tool_data.get('image_url')
                tool.youtube_url = tool_data.get('youtube_url')
                tool.is_approved = tool_data.get('is_approved', False)
                tool.user_id = current_user.id
                
                # Handle categories
                for category_name in tool_data.get('categories', []):
                    category = Category.query.filter_by(name=category_name).first()
                    if category:
                        tool.categories.append(category)
                
                db.session.add(tool)
            
            db.session.commit()
            flash('Tools imported successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error importing tools: {str(e)}', 'danger')
            return redirect(url_for('admin.import_tools'))
    
    return render_template('admin/import_tools.html')

@admin.route('/tools/bulk-remove', methods=['POST'])
@login_required
def bulk_remove_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tool_ids = request.form.getlist('tool_ids[]')
    if not tool_ids:
        flash('No tools selected for removal.', 'warning')
        return redirect(url_for('index'))
    
    Tool.query.filter(Tool.id.in_(tool_ids)).delete(synchronize_session=False)
    db.session.commit()
    
    flash(f'Successfully removed {len(tool_ids)} tools.', 'success')
    return redirect(url_for('index'))
