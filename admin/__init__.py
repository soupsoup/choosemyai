from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, make_response
from flask_login import login_required, current_user
from app import db
from models import AppearanceSettings, Category, Tool
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
            # Update all appearance settings
            for field in [
                'primary_color', 'secondary_color', 'background_color', 'font_color',
                'font_family', 'header_background', 'secondary_text_color',
                'button_background_color', 'button_hover_background_color',
                'button_text_color', 'button_hover_text_color', 'link_color',
                'link_hover_color', 'nav_link_color', 'nav_link_hover_color',
                'container_background_color', 'container_border_color',
                'search_box_background_color', 'search_box_border_color',
                'category_item_background_color', 'category_item_hover_color',
                'category_item_text_color', 'category_item_hover_text_color',
                'input_background_color', 'input_text_color'
            ]:
                if field in request.form:
                    setattr(settings, field, request.form[field])
            
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
    
    # Create CSV StringIO object
    si = StringIO()
    writer = csv.writer(si)
    
    # Write headers
    writer.writerow(['Name', 'Description', 'URL', 'Image URL', 'YouTube URL', 'Categories', 'Resources', 'Is Approved'])
    
    # Write tool data
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
    
    # Create a memory file for the CSV
    mem = StringIO()
    mem.write(output)
    mem.seek(0)
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name='tools_export.csv'
    )

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
                # Handle CSV import
                decoded_content = content.decode('utf-8')
                reader = csv.DictReader(StringIO(decoded_content))
                data = list(reader)
            
            # Process and import the tools
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
                
                # Handle categories
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
                
                # Handle resources field
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
