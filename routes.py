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

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure bleach with allowed tags and attributes
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

def validate_media_urls(tool):
    """Validate and log media URLs for a tool"""
    issues = []
    
    if tool.image_url:
        app.logger.info(f'Validating image URL for tool {tool.id}: {tool.image_url}')
        if not is_valid_image_url(tool.image_url):
            issues.append(f'Invalid image URL format: {tool.image_url}')
            app.logger.warning(f'Invalid image URL format for tool {tool.id}: {tool.image_url}')
    
    if tool.youtube_url:
        app.logger.info(f'Validating YouTube URL for tool {tool.id}: {tool.youtube_url}')
        if not is_valid_youtube_url(tool.youtube_url):
            issues.append(f'Invalid YouTube URL format: {tool.youtube_url}')
            app.logger.warning(f'Invalid YouTube URL format for tool {tool.id}: {tool.youtube_url}')
        else:
            app.logger.info(f'Generated YouTube embed URL: {tool.youtube_embed_url}')
    
    return issues

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
    
    return render_template('index.html', categories=categories, tools=tools)

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    sort_by = request.args.get('sort', 'votes')
    search_query = request.args.get('search', '').strip()
    
    query = Tool.query.join(Tool.categories).filter(Category.id == category_id, Tool.is_approved == True)
    
    if search_query:
        query = query.filter(
            or_(
                Tool.name.ilike(f'%{search_query}%'),
                Tool.description.ilike(f'%{search_query}%')
            )
        )
    
    if sort_by == 'votes':
        query = query.join(ToolVote, Tool.id == ToolVote.tool_id, isouter=True)\
                    .group_by(Tool.id)\
                    .order_by(desc(func.coalesce(func.sum(ToolVote.value), 0)))
    else:
        query = query.order_by(desc(Tool.created_at))
    
    tools = query.all()
    return render_template('category.html', category=category, tools=tools)

@app.route('/tool/<int:tool_id>')
def tool(tool_id):
    tool = Tool.query.get_or_404(tool_id)
    if not tool.is_approved and (not current_user.is_authenticated or 
                                (current_user.id != tool.user_id and not current_user.is_moderator)):
        flash('This tool is not yet approved.', 'warning')
        return redirect(url_for('index'))
    
    sort_by = request.args.get('sort', 'votes')
    
    if sort_by == 'votes':
        comments = Comment.query\
            .filter_by(tool_id=tool_id)\
            .join(CommentVote, Comment.id == CommentVote.comment_id, isouter=True)\
            .group_by(Comment.id)\
            .order_by(desc(func.coalesce(func.sum(CommentVote.value), 0)))\
            .all()
    else:
        comments = Comment.query\
            .filter_by(tool_id=tool_id)\
            .order_by(desc(Comment.created_at))\
            .all()
    
    similar_tools = Tool.query\
        .join(Tool.categories)\
        .filter(Tool.id != tool_id, Tool.is_approved == True, Category.id.in_([c.id for c in tool.categories]))\
        .group_by(Tool.id)\
        .order_by(desc(func.count(Category.id)))\
        .limit(5)\
        .all()
    
    return render_template('tool.html', tool=tool, comments=comments, similar_tools=similar_tools)

@app.route('/tool/<int:tool_id>/comment', methods=['POST'])
@login_required
def add_comment(tool_id):
    content = request.form.get('content')
    if content:
        clean_content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        comment = Comment()
        comment.content = clean_content
        comment.tool_id = tool_id
        comment.user_id = current_user.id
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('tool', tool_id=tool_id))

@app.route('/vote/tool/<int:tool_id>/<int:value>', methods=['POST'])
@login_required
def vote_tool(tool_id, value):
    if value not in [-1, 1]:
        return jsonify({'error': 'Invalid vote value'}), 400
    
    existing_vote = ToolVote.query.filter_by(tool_id=tool_id, user_id=current_user.id).first()
    if existing_vote:
        existing_vote.value = value
    else:
        vote = ToolVote()
        vote.tool_id = tool_id
        vote.user_id = current_user.id
        vote.value = value
        db.session.add(vote)
    
    db.session.commit()
    tool = Tool.query.get_or_404(tool_id)
    return jsonify({'votes': tool.vote_count})

@app.route('/vote/comment/<int:comment_id>/<int:value>', methods=['POST'])
@login_required
def vote_comment(comment_id, value):
    if value not in [-1, 1]:
        return jsonify({'error': 'Invalid vote value'}), 400
    
    existing_vote = CommentVote.query.filter_by(comment_id=comment_id, user_id=current_user.id).first()
    if existing_vote:
        existing_vote.value = value
    else:
        vote = CommentVote()
        vote.comment_id = comment_id
        vote.user_id = current_user.id
        vote.value = value
        db.session.add(vote)
    
    db.session.commit()
    comment = Comment.query.get_or_404(comment_id)
    return jsonify({'votes': comment.vote_count})

@app.route('/submit-tool', methods=['GET', 'POST'])
@login_required
def submit_tool():
    if request.method == 'POST':
        image_url = request.form.get('image_url', '').strip()
        youtube_url = request.form.get('youtube_url', '').strip()
        category_ids = request.form.getlist('categories')
        
        if not category_ids:
            flash('Please select at least one category', 'danger')
            categories = Category.query.all()
            return render_template('submit_tool.html', categories=categories)
        
        if image_url and not is_valid_image_url(image_url):
            flash('Invalid image URL. Please provide a URL ending with .jpg, .jpeg, .png, .gif, or .webp', 'danger')
            categories = Category.query.all()
            return render_template('submit_tool.html', categories=categories)
            
        if youtube_url and not is_valid_youtube_url(youtube_url):
            flash('Invalid YouTube URL. Please provide a valid YouTube video URL', 'danger')
            categories = Category.query.all()
            return render_template('submit_tool.html', categories=categories)
        
        clean_description = bleach.clean(
            request.form['description'],
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES
        )
        
        tool = Tool()
        tool.name = request.form['name']
        tool.description = clean_description
        tool.url = request.form['url']
        tool.image_url = image_url or None
        tool.youtube_url = youtube_url or None
        tool.user_id = current_user.id
        tool.is_approved = False
        
        # Add selected categories
        selected_categories = Category.query.filter(Category.id.in_(category_ids)).all()
        tool.categories = selected_categories
        
        db.session.add(tool)
        db.session.commit()
        
        app.logger.info(f'New tool submitted - ID: {tool.id}, Name: {tool.name}, Categories: {[c.name for c in tool.categories]}')
        
        flash('Tool submitted successfully! It will be visible after moderation.', 'success')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('submit_tool.html', categories=categories)

@app.route('/moderate-tools')
@login_required
def moderate_tools():
    if not current_user.is_moderator:
        flash('Access denied. Moderator rights required.', 'danger')
        return redirect(url_for('index'))
    
    pending_tools = Tool.query.filter_by(is_approved=False).order_by(Tool.created_at.desc()).all()
    
    # Add debug logging for tools
    for tool in pending_tools:
        app.logger.info(f'Processing pending tool - ID: {tool.id}, Name: {tool.name}')
        app.logger.info(f'Categories: {[c.name for c in tool.categories]}')
        app.logger.info(f'Image URL: {tool.image_url}')
        app.logger.info(f'YouTube URL: {tool.youtube_url}')
        
        if tool.youtube_url:
            app.logger.info(f'YouTube Embed URL: {tool.youtube_embed_url}')
        
        issues = validate_media_urls(tool)
        if issues:
            for issue in issues:
                app.logger.warning(f'Tool {tool.id} - {issue}')
    
    return render_template('moderate_tools.html', tools=pending_tools)

@app.route('/moderate-tool/<int:tool_id>/<action>')
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
        flash('Tool rejected and removed.', 'success')
    
    db.session.commit()
    return redirect(url_for('moderate_tools'))

@app.route('/remove-tool/<int:tool_id>')
@login_required
def remove_tool(tool_id):
    if not current_user.is_moderator:
        flash('Access denied. Moderator rights required.', 'danger')
        return redirect(url_for('index'))
    
    tool = Tool.query.get_or_404(tool_id)
    db.session.delete(tool)
    db.session.commit()
    
    flash('Tool has been permanently removed.', 'success')
    return redirect(url_for('index'))

@app.route('/edit-tool/<int:tool_id>', methods=['GET', 'POST'])
@login_required
def edit_tool(tool_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    tool = Tool.query.get_or_404(tool_id)
    categories = Category.query.all()
    
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
        
        tool.name = request.form['name']
        tool.description = clean_description
        tool.url = request.form['url']
        tool.image_url = image_url or None
        tool.youtube_url = youtube_url or None
        
        # Update categories
        selected_categories = Category.query.filter(Category.id.in_(category_ids)).all()
        tool.categories = selected_categories
        
        db.session.commit()
        
        app.logger.info(f'Tool updated - ID: {tool.id}, Name: {tool.name}, Categories: {[c.name for c in tool.categories]}')
        
        flash('Tool updated successfully!', 'success')
        return redirect(url_for('tool', tool_id=tool.id))
    
    return render_template('admin/edit_tool.html', tool=tool, categories=categories)
