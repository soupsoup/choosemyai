from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
import re

# Association table for Tool-Category many-to-many relationship
tool_categories = db.Table('tool_categories',
    db.Column('tool_id', db.Integer, db.ForeignKey('tool.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_moderator = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    tools = db.relationship('Tool', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    blog_posts = db.relationship('BlogPost', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500))
    youtube_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='tool', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('ToolVote', backref='tool', lazy='dynamic', cascade='all, delete-orphan')
    is_approved = db.Column(db.Boolean, default=False)
    categories = db.relationship('Category', secondary=tool_categories, lazy='subquery',
                                backref=db.backref('tools', lazy=True))
    resources = db.Column(db.Text)  # Store as JSON string of resource entries

    @property
    def vote_count(self):
        return db.session.query(db.func.sum(ToolVote.value)).filter(ToolVote.tool_id == self.id).scalar() or 0
    
    @property
    def youtube_embed_url(self):
        if not self.youtube_url:
            return None
        
        youtube_regex = (
            r'(?:https?:\/\/)?'
            r'(?:www\.)?'
            r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|'
            r'youtu\.be\/)([a-zA-Z0-9_-]{11})'
        )
        
        match = re.search(youtube_regex, self.youtube_url)
        if match:
            video_id = match.group(1)
            return f'https://www.youtube.com/embed/{video_id}'
        return None

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    votes = db.relationship('CommentVote', backref='comment', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def vote_count(self):
        return db.session.query(db.func.sum(CommentVote.value)).filter(CommentVote.comment_id == self.id).scalar() or 0

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    featured_image = db.Column(db.String(500))
    excerpt = db.Column(db.Text)

    def generate_slug(self):
        base_slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        base_slug = re.sub(r'[-\s]+', '-', base_slug).strip('-')
        slug = base_slug
        counter = 1
        
        while BlogPost.query.filter_by(slug=slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug

class ToolVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CommentVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AppearanceSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    primary_color = db.Column(db.String(7), default='#0d6efd')
    secondary_color = db.Column(db.String(7), default='#6c757d')
    background_color = db.Column(db.String(7), default='#212529')
    font_color = db.Column(db.String(7), default='#ffffff')
    font_family = db.Column(db.Text, default='system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif')
    header_background = db.Column(db.String(7), default='#212529')
    secondary_text_color = db.Column(db.String(7), default='#6c757d')
    button_background_color = db.Column(db.String(7), default='#0d6efd')
    button_hover_background_color = db.Column(db.String(7), default='#0b5ed7')
    button_text_color = db.Column(db.String(7), default='#ffffff')
    button_hover_text_color = db.Column(db.String(7), default='#ffffff')
    link_color = db.Column(db.String(7), default='#0d6efd')
    link_hover_color = db.Column(db.String(7), default='#0a58ca')
    nav_link_color = db.Column(db.String(7), default='#ffffff')
    nav_link_hover_color = db.Column(db.String(7), default='#e9ecef')
    # Container color settings
    container_background_color = db.Column(db.String(7), default='#2c3034')
    container_border_color = db.Column(db.String(7), default='#373b3e')
    search_box_background_color = db.Column(db.String(7), default='#2c3034')
    search_box_border_color = db.Column(db.String(7), default='#373b3e')
    category_item_background_color = db.Column(db.String(7), default='#2c3034')
    category_item_hover_color = db.Column(db.String(7), default='#373b3e')
    category_item_text_color = db.Column(db.String(7), default='#ffffff')
    category_item_hover_text_color = db.Column(db.String(7), default='#ffffff')
    # Comment box colors
    comment_box_background_color = db.Column(db.String(7), default='#2c3034')
    comment_box_text_color = db.Column(db.String(7), default='#ffffff')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_settings():
        settings = AppearanceSettings.query.first()
        if not settings:
            settings = AppearanceSettings()
            db.session.add(settings)
            db.session.commit()
        return settings
