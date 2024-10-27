from flask import render_template, request, redirect, url_for, jsonify, flash, send_file
from flask_login import current_user, login_required
from app import app, db
from models import Category, Tool, Comment, ToolVote, CommentVote, AppearanceSettings
from sqlalchemy import desc, func, or_
from api import api
from admin import admin
import bleach
import re
import logging
import json

logging.basicConfig(level=logging.INFO)

@app.route('/ads.txt')
def serve_ads_txt():
    return send_file('static/ads.txt', mimetype='text/plain')

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    '*': ['class']
}

@app.template_filter('parse_json')
def parse_json_filter(value):
    try:
        return json.loads(value) if value else []
    except:
        return []

def is_valid_youtube_url(url):
    if not url:
        return True
    youtube_regex = (
        r'^(?:https?:\/\/)?'
        r'(?:www\.)?'
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|'
        r'youtu\.be\/)([a-zA-Z0-9_-]{11})$'
    )
    return bool(re.match(youtube_regex, url))

def is_valid_image_url(url):
    if not url:
        return True
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    return url.lower().endswith(image_extensions)

@app.context_processor
def inject_appearance_settings():
    return {'appearance_settings': AppearanceSettings.get_settings()}

@app.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category')
    sort_by = request.args.get('sort', 'votes')
    
    query = Tool.query.filter_by(is_approved=True)
    
    if search_query:
        query = query.filter(
            or_(
                Tool.name.ilike(f'%{search_query}%'),
                Tool.description.ilike(f'%{search_query}%')
            )
        )
    
    if category_id:
        try:
            category_id = int(category_id)
            query = query.join(Tool.categories).filter(Category.id == category_id)
        except (ValueError, TypeError):
            pass
    
    if sort_by == 'votes':
        query = query.join(ToolVote, Tool.id == ToolVote.tool_id, isouter=True)\
                    .group_by(Tool.id)\
                    .order_by(desc(func.coalesce(func.sum(ToolVote.value), 0)))
    else:
        query = query.order_by(desc(Tool.created_at))
    
    tools = query.all()
    categories = Category.query.all()
    
    return render_template('index.html', tools=tools, categories=categories)

@app.route('/submit-tool', methods=['GET', 'POST'])
@login_required
def submit_tool():
    if request.method == 'POST':
        name = request.form.get('name')
        description = bleach.clean(request.form.get('description') or '', tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        url = request.form.get('url')
        image_url = request.form.get('image_url')
        youtube_url = request.form.get('youtube_url')
        category_ids = request.form.getlist('categories')
        
        if not name or not description or not url or not category_ids:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('submit_tool'))
            
        if youtube_url and not is_valid_youtube_url(youtube_url):
            flash('Please enter a valid YouTube URL', 'danger')
            return redirect(url_for('submit_tool'))
            
        if image_url and not is_valid_image_url(image_url):
            flash('Please enter a valid image URL', 'danger')
            return redirect(url_for('submit_tool'))
            
        tool = Tool()
        tool.name = name
        tool.description = description
        tool.url = url
        tool.image_url = image_url
        tool.youtube_url = youtube_url
        tool.user_id = current_user.id
        
        # Handle categories
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        if not categories:
            flash('Please select at least one valid category', 'danger')
            return redirect(url_for('submit_tool'))
        tool.categories = categories
        
        # Handle resources
        resource_titles = request.form.getlist('resource_titles[]')
        resource_urls = request.form.getlist('resource_urls[]')
        resources = []
        for title, url in zip(resource_titles, resource_urls):
            if title and url:
                resources.append({'title': title, 'url': url})
        tool.resources = json.dumps(resources)
        
        try:
            db.session.add(tool)
            db.session.commit()
            flash('Tool submitted successfully! It will be reviewed by moderators.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting tool: {str(e)}', 'danger')
            return redirect(url_for('submit_tool'))
    
    categories = Category.query.all()
    return render_template('submit_tool.html', categories=categories)

@app.route('/moderate-tools')
@login_required
def moderate_tools():
    if not current_user.is_moderator:
        flash('Access denied. Moderator rights required.', 'danger')
        return redirect(url_for('index'))
    
    tools = Tool.query.filter_by(is_approved=False).order_by(Tool.created_at.desc()).all()
    return render_template('moderate_tools.html', tools=tools)

@app.route('/moderate-tool/<int:tool_id>/<string:action>')
@login_required
def moderate_tool(tool_id, action):
    if not current_user.is_moderator:
        flash('Access denied. Moderator rights required.', 'danger')
        return redirect(url_for('index'))
        
    tool = Tool.query.get_or_404(tool_id)
    
    if action == 'approve':
        tool.is_approved = True
        flash('Tool approved successfully!', 'success')
    elif action == 'reject':
        db.session.delete(tool)
        flash('Tool rejected successfully!', 'success')
    else:
        flash('Invalid action!', 'danger')
        return redirect(url_for('moderate_tools'))
        
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        
    return redirect(url_for('moderate_tools'))

# Add other routes back...
