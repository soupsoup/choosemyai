from flask import render_template, request, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required
from app import app, db
from models import Category, Tool, Comment, ToolVote, CommentVote, AppearanceSettings
from sqlalchemy import desc, func, or_
from auth import auth
from admin import admin
import bleach
import re
import logging
import json

logging.basicConfig(level=logging.INFO)

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    '*': ['class']
}

app.register_blueprint(auth)
app.register_blueprint(admin)

@app.template_filter('parse_json')
def parse_json(value):
    try:
        return json.loads(value) if value else []
    except:
        return []

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
    
    return render_template('index.html', categories=categories, tools=tools)

@app.route('/submit-tool', methods=['GET', 'POST'])
@login_required
def submit_tool():
    categories = Category.query.all()
    if request.method == 'POST':
        # Handle form submission
        clean_description = bleach.clean(
            request.form['description'],
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES
        )
        
        tool = Tool()
        tool.name = request.form['name']
        tool.description = clean_description
        tool.url = request.form['url']
        tool.image_url = request.form.get('image_url') or None
        tool.youtube_url = request.form.get('youtube_url') or None
        tool.user_id = current_user.id
        
        # Process learning resources
        resources = []
        resource_titles = request.form.getlist('resource_titles[]')
        resource_urls = request.form.getlist('resource_urls[]')
        for title, url in zip(resource_titles, resource_urls):
            if title.strip() and url.strip():
                resources.append({'title': title.strip(), 'url': url.strip()})
        tool.resources = json.dumps(resources) if resources else None
        
        # Handle categories
        category_ids = request.form.getlist('categories')
        if not category_ids:
            flash('Please select at least one category', 'danger')
            return render_template('submit_tool.html', categories=categories)
            
        selected_categories = Category.query.filter(Category.id.in_(category_ids)).all()
        tool.categories = selected_categories
        
        db.session.add(tool)
        db.session.commit()
        
        flash('Tool submitted successfully! It will be reviewed by a moderator.', 'success')
        return redirect(url_for('index'))
    
    return render_template('submit_tool.html', categories=categories)

@app.route('/edit-tool/<int:tool_id>', methods=['GET', 'POST'])
@login_required
def edit_tool(tool_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tool = Tool.query.get_or_404(tool_id)
    categories = Category.query.all()
    
    # Add debug log for tool resources
    app.logger.info(f'Tool resources: {tool.resources}')
    
    if request.method == 'POST':
        image_url = request.form.get('image_url', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        category_ids = request.form.getlist('categories')
        
        if not category_ids:
            flash('Please select at least one category', 'danger')
            return render_template('admin/edit_tool.html', tool=tool, categories=categories)
        
        if image_url and not is_valid_image_url(image_url):
            flash('Invalid image URL. Please provide a URL ending with .jpg, .jpeg, .png, .gif, or .webp', 'danger')
            return render_template('admin/edit_tool.html', tool=tool, categories=categories)
            
        if youtube_url and not is_valid_youtube_url(youtube_url):
            flash('Invalid YouTube URL. Please provide a valid YouTube video URL', 'danger')
            return render_template('admin/edit_tool.html', tool=tool, categories=categories)
        
        clean_description = bleach.clean(
            request.form['description'],
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES
        )
        
        # Process learning resources
        resources = []
        resource_titles = request.form.getlist('resource_titles[]')
        resource_urls = request.form.getlist('resource_urls[]')
        for title, url in zip(resource_titles, resource_urls):
            if title.strip() and url.strip():
                resources.append({'title': title.strip(), 'url': url.strip()})
        
        tool.name = request.form['name']
        tool.description = clean_description
        tool.url = request.form['url']
        tool.image_url = image_url or None
        tool.youtube_url = youtube_url or None
        tool.resources = json.dumps(resources) if resources else None
        
        selected_categories = Category.query.filter(Category.id.in_(category_ids)).all()
        tool.categories = selected_categories
        
        db.session.commit()
        
        flash('Tool updated successfully!', 'success')
        return redirect(url_for('tool', tool_id=tool.id))
    
    return render_template('admin/edit_tool.html', tool=tool, categories=categories)

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
