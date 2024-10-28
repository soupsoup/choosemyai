from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import AppearanceSettings

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
                'category_item_text_color', 'category_item_hover_text_color'
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
