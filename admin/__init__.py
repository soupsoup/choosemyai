from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import login_required, current_user
from app import db
from models import AppearanceSettings, Category, Tool, User
import json

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
            settings.primary_color = request.form.get('primary_color')
            settings.secondary_color = request.form.get('secondary_color')
            settings.background_color = request.form.get('background_color')
            settings.font_color = request.form.get('font_color')
            settings.header_background = request.form.get('header_background')
            settings.secondary_text_color = request.form.get('secondary_text_color')
            settings.font_family = request.form.get('font_family')
            
            # Button styles
            settings.button_background_color = request.form.get('button_background_color')
            settings.button_hover_background_color = request.form.get('button_hover_background_color')
            settings.button_text_color = request.form.get('button_text_color')
            settings.button_hover_text_color = request.form.get('button_hover_text_color')
            
            # Link colors
            settings.link_color = request.form.get('link_color')
            settings.link_hover_color = request.form.get('link_hover_color')
            
            # Navigation colors
            settings.nav_link_color = request.form.get('nav_link_color')
            settings.nav_link_hover_color = request.form.get('nav_link_hover_color')
            
            db.session.commit()
            flash('Appearance settings updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating appearance settings: {str(e)}', 'danger')
        
        return redirect(url_for('admin.appearance'))
    
    return render_template('admin/appearance.html', settings=settings)

@admin.route('/admin/manage-tools')
@login_required
def manage_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tools = Tool.query.order_by(Tool.created_at.desc()).all()
    return render_template('admin/manage_tools.html', tools=tools)

@admin.route('/admin/delete-tools', methods=['POST'])
@login_required
def delete_tools():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    tool_ids = request.form.getlist('tool_ids')
    if not tool_ids:
        return jsonify({'error': 'No tools selected'}), 400
    
    try:
        Tool.query.filter(Tool.id.in_(tool_ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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

@admin.route('/admin/delete-category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        category = Category.query.get_or_404(category_id)
        
        # Check if category has associated tools
        tools_count = len(category.tools)
        if tools_count > 0:
            tool_text = 'tool' if tools_count == 1 else 'tools'
            return jsonify({
                'error': f'Cannot delete category "{category.name}" because it has {tools_count} associated {tool_text}. '
                        'Please remove or reassign the tools first.'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Category "{category.name}" deleted successfully!'
        })
    except Exception as e:
        db.session.rollback()
        error_msg = f'Error deleting category: {str(e)}'
        return jsonify({'error': error_msg}), 500

@admin.route('/admin/edit-category/<int:category_id>', methods=['POST'])
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name or not description:
        flash('Both name and description are required.', 'danger')
        return redirect(url_for('admin.categories'))
    
    existing_category = Category.query.filter_by(name=name).first()
    if existing_category and existing_category.id != category_id:
        flash('A category with this name already exists.', 'danger')
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

@admin.route('/admin/import-tools', methods=['GET', 'POST'])
@login_required
def import_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(url_for('admin.import_tools'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('admin.import_tools'))
        
        if not file.filename.endswith('.json'):
            flash('Only JSON files are allowed', 'danger')
            return redirect(url_for('admin.import_tools'))
        
        try:
            content = file.read().decode('utf-8')
            tools_data = json.loads(content)
            
            # Ensure tools_data is a list
            if isinstance(tools_data, dict):
                tools_data = [tools_data]
            elif not isinstance(tools_data, list):
                raise ValueError("Invalid JSON format: must be an array or object of tools")
            
            for tool_data in tools_data:
                if not isinstance(tool_data, dict):
                    continue
                    
                tool = Tool()
                tool.name = str(tool_data.get('name', ''))
                tool.description = str(tool_data.get('description', ''))
                tool.url = str(tool_data.get('url', ''))
                tool.image_url = str(tool_data.get('image_url', '')) or None
                tool.youtube_url = str(tool_data.get('youtube_url', '')) or None
                tool.resources = json.dumps(tool_data.get('resources', []))
                tool.user_id = current_user.id
                tool.is_approved = True
                
                # Handle categories
                categories = []
                cat_names = tool_data.get('categories', [])
                if isinstance(cat_names, list):
                    for cat_name in cat_names:
                        category = Category.query.filter_by(name=str(cat_name)).first()
                        if category:
                            categories.append(category)
                tool.categories = categories
                
                db.session.add(tool)
            
            db.session.commit()
            flash('Tools imported successfully!', 'success')
        except json.JSONDecodeError:
            flash('Invalid JSON file format', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error importing tools: {str(e)}', 'danger')
        
        return redirect(url_for('admin.import_tools'))
    
    return render_template('admin/import_tools.html')

@admin.route('/admin/export-tools')
@login_required
def export_tools():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tools = Tool.query.all()
    tools_data = []
    
    for tool in tools:
        tool_data = {
            'name': tool.name,
            'description': tool.description,
            'url': tool.url,
            'image_url': tool.image_url,
            'youtube_url': tool.youtube_url,
            'categories': [cat.name for cat in tool.categories],
            'resources': json.loads(tool.resources) if tool.resources else [],
            'created_at': tool.created_at.isoformat()
        }
        tools_data.append(tool_data)
    
    return jsonify(tools_data)

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

@admin.route('/admin/manage-users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.order_by(User.username).all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/admin/edit-user-roles/<int:user_id>', methods=['POST'])
@login_required
def edit_user_roles(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-role modification
    if current_user.id != user.id:
        user.is_admin = bool(request.form.get('is_admin'))
    user.is_moderator = bool(request.form.get('is_moderator'))
    
    try:
        db.session.commit()
        flash('User roles updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user roles: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/delete-user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    if current_user.id == user_id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/export-users')
@login_required
def export_users():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    users_data = []
    
    for user in users:
        user_data = {
            'username': user.username,
            'email': user.email,
            'is_moderator': user.is_moderator,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
        users_data.append(user_data)
    
    response = make_response(json.dumps(users_data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename=users_export.json'
    return response

@admin.route('/admin/import-users', methods=['POST'])
@login_required
def import_users():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    if not file.filename.endswith('.json'):
        flash('Only JSON files are allowed', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        content = file.read().decode('utf-8')
        users_data = json.loads(content)
        
        if isinstance(users_data, dict):
            users_data = [users_data]
        
        for user_data in users_data:
            if User.query.filter_by(email=user_data.get('email')).first():
                continue
                
            user = User()
            user.username = user_data.get('username')
            user.email = user_data.get('email')
            user.is_moderator = user_data.get('is_moderator', False)
            user.is_admin = user_data.get('is_admin', False)
            user.set_password('temppass123')  # Set a temporary password
            
            db.session.add(user)
        
        db.session.commit()
        flash('Users imported successfully! Default password set to "temppass123"', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error importing users: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_users'))