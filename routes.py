from flask import render_template, request, redirect, url_for, jsonify, flash, send_from_directory, send_file, make_response
from flask_login import current_user, login_required
from app import app, db
from models import Category, Tool, Comment, ToolVote, CommentVote, AppearanceSettings, BlogPost
from sqlalchemy import desc, func, or_
import bleach
import re
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    '*': ['class']
}

@app.route('/static/css/custom.css')
def custom_css():
    settings = AppearanceSettings.get_settings()
    css = render_template('css/custom.css', appearance_settings=settings)
    response = make_response(css)
    response.headers['Content-Type'] = 'text/css'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    try:
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
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Database error: {str(e)}")
        flash('An error occurred while loading the page. Please try again.', 'danger')
        return render_template('index.html', tools=[], categories=[])

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
        
        tool = Tool()
        tool.name = name
        tool.description = description
        tool.url = url
        tool.image_url = image_url
        tool.youtube_url = youtube_url
        tool.user_id = current_user.id
        
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        if not categories:
            flash('Please select at least one valid category', 'danger')
            return redirect(url_for('submit_tool'))
        tool.categories = categories
        
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

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    tools = Tool.query.filter_by(is_approved=True)\
                     .filter(Tool.categories.contains(category))\
                     .order_by(desc(Tool.created_at))\
                     .all()
    return render_template('category.html', category=category, tools=tools)

@app.route('/tool/<int:tool_id>')
def tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    if not tool.is_approved and not (current_user.is_authenticated and (current_user.is_moderator or current_user.id == tool.user_id)):
        flash('This tool is not yet approved.', 'warning')
        return redirect(url_for('index'))
    
    comments = Comment.query.filter_by(tool_id=tool_id)\
                           .order_by(desc(Comment.created_at))\
                           .all()
    
    similar_tools = Tool.query.join(Tool.categories)\
        .filter(Tool.id != tool_id)\
        .filter(Tool.is_approved == True)\
        .filter(Category.id.in_([c.id for c in tool.categories]))\
        .group_by(Tool.id)\
        .order_by(func.random())\
        .limit(5)\
        .all()
    
    return render_template('tool.html', tool=tool, comments=comments, similar_tools=similar_tools)

@app.route('/add-comment/<int:tool_id>', methods=['POST'])
@login_required
def add_comment(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    content = bleach.clean(request.form.get('content') or '', tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('tool', tool_id=tool_id))
    
    comment = Comment(content=content, tool_id=tool_id, user_id=current_user.id)
    
    try:
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding comment: {str(e)}', 'danger')
    
    return redirect(url_for('tool', tool_id=tool_id))

@app.route('/remove-tool/<int:tool_id>')
@login_required
def remove_tool(tool_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tool = Tool.query.get_or_404(tool_id)
    
    try:
        db.session.delete(tool)
        db.session.commit()
        flash('Tool removed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing tool: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/edit-tool/<int:tool_id>', methods=['GET', 'POST'])
@login_required
def edit_tool(tool_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tool = Tool.query.get_or_404(tool_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = bleach.clean(request.form.get('description') or '', tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        url = request.form.get('url')
        image_url = request.form.get('image_url')
        youtube_url = request.form.get('youtube_url')
        category_ids = request.form.getlist('categories')
        
        if not name or not description or not url or not category_ids:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('edit_tool', tool_id=tool_id))
        
        try:
            tool.name = name
            tool.description = description
            tool.url = url
            tool.image_url = image_url
            tool.youtube_url = youtube_url
            
            categories = Category.query.filter(Category.id.in_(category_ids)).all()
            if not categories:
                flash('Please select at least one valid category', 'danger')
                return redirect(url_for('edit_tool', tool_id=tool_id))
            tool.categories = categories
            
            resource_titles = request.form.getlist('resource_titles[]')
            resource_urls = request.form.getlist('resource_urls[]')
            resources = []
            for title, url in zip(resource_titles, resource_urls):
                if title and url:
                    resources.append({'title': title, 'url': url})
            tool.resources = json.dumps(resources)
            
            db.session.commit()
            flash('Tool updated successfully!', 'success')
            return redirect(url_for('tool', tool_id=tool_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating tool: {str(e)}', 'danger')
            return redirect(url_for('edit_tool', tool_id=tool_id))
    
    categories = Category.query.all()
    return render_template('admin/edit_tool.html', tool=tool, categories=categories)