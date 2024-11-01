from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, make_response
from flask_login import login_required, current_user
from app import db
from models import AppearanceSettings, Category, Tool
from datetime import datetime
import json
from io import StringIO
import csv

admin = Blueprint('admin', __name__)

@admin.route('/admin/appearance', methods=['GET', 'POST'])
@login_required
def appearance():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    settings = AppearanceSettings.get_settings()
    
    if request.method == 'POST':
        try:
            # Update color settings
            color_fields = [
                'list_item_background_color',
                'list_item_text_color',
                'list_item_hover_background_color',
                'list_item_hover_text_color',
                'container_header_text_color',
                'font_family',
                'background_color', 'header_background',
                'main_text_color', 'card_text_color', 'footer_text_color',
                'container_background_color', 'container_border_color',
                'search_box_background_color', 'search_box_border_color',
                'category_item_background_color', 'category_item_hover_color',
                'category_item_text_color', 'category_item_hover_text_color'
            ]
            
            for field in color_fields:
                if field in request.form:
                    setattr(settings, field, request.form[field])
            
            db.session.commit()
            
            # Force CSS reload
            settings.last_updated = datetime.utcnow()
            db.session.commit()
            
            flash('Appearance settings updated successfully!', 'success')
            return redirect(url_for('admin.appearance'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating appearance settings: {str(e)}', 'danger')
    
    return render_template('admin/appearance.html', settings=settings)

@admin.route('/admin/categories')
@login_required
def categories():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('admin/categories.html', categories=Category.query.all())

@admin.route('/admin/add-category', methods=['POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Category name is required', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding category: {str(e)}', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/admin/edit-category/<int:category_id>', methods=['POST'])
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Category name is required', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        category.name = name
        category.description = description
        db.session.commit()
        flash('Category updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating category: {str(e)}', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/admin/delete-category/<int:category_id>')
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/admin/manage-tools')
@login_required
def manage_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('admin/manage_tools.html', tools=Tool.query.all())

@admin.route('/admin/export-tools')
@login_required
def export_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    try:
        si = StringIO()
        writer = csv.writer(si)
        
        writer.writerow(['Name', 'Description', 'URL', 'Image URL', 'YouTube URL', 'Categories', 'Resources', 'Is Approved'])
        
        tools = Tool.query.all()
        for tool in tools:
            categories = [c.name for c in tool.categories]
            resources = json.loads(tool.resources) if tool.resources else []
            writer.writerow([
                tool.name,
                tool.description,
                tool.url,
                tool.image_url or '',
                tool.youtube_url or '',
                ', '.join(categories),
                json.dumps(resources),
                'Yes' if tool.is_approved else 'No'
            ])
        
        output = si.getvalue()
        si.close()
        
        response = make_response(output)
        response.headers["Content-Disposition"] = "attachment; filename=tools_export.csv"
        response.headers["Content-type"] = "text/csv"
        return response
        
    except Exception as e:
        flash(f'Error exporting tools: {str(e)}', 'danger')
        return redirect(url_for('admin.import_tools'))

@admin.route('/admin/import-tools', methods=['GET', 'POST'])
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
        
        if not file.filename.endswith(('.json', '.csv')):
            flash('Only JSON and CSV files are allowed', 'danger')
            return redirect(url_for('admin.import_tools'))
        
        try:
            content = file.read()
            if file.filename.endswith('.json'):
                data = json.loads(content)
            else:
                decoded_content = content.decode('utf-8')
                reader = csv.DictReader(StringIO(decoded_content))
                data = list(reader)
            
            for item in data:
                tool = Tool(
                    name=item['name'],
                    description=item['description'],
                    url=item['url'],
                    image_url=item.get('image_url', ''),
                    youtube_url=item.get('youtube_url', ''),
                    is_approved=True,
                    user_id=current_user.id
                )
                
                if 'categories' in item:
                    category_names = []
                    if isinstance(item['categories'], str):
                        category_names = [c.strip() for c in item['categories'].split(',')]
                    elif isinstance(item['categories'], list):
                        category_names = item['categories']
                    else:
                        category_names = []
                    
                    for name in category_names:
                        name = str(name).strip()
                        category = Category.query.filter_by(name=name).first()
                        if category:
                            tool.categories.append(category)
                
                if 'resources' in item:
                    try:
                        if isinstance(item['resources'], str):
                            tool.resources = item['resources']
                        elif isinstance(item['resources'], list):
                            tool.resources = json.dumps(item['resources'])
                        else:
                            tool.resources = '[]'
                    except:
                        tool.resources = '[]'
                
                db.session.add(tool)
            
            db.session.commit()
            flash('Tools imported successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error importing tools: {str(e)}', 'danger')
        
        return redirect(url_for('admin.import_tools'))
    
    return render_template('admin/import_tools.html')

@admin.route('/admin/change-password')
@login_required
def change_password():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    return render_template('admin/change_password.html')