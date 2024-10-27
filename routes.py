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

# Add other routes back...
