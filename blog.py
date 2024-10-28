from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import BlogPost
import bleach

blog = Blueprint('blog', __name__)

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    '*': ['class']
}

@blog.route('/blog')
def index():
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template('blog/index.html', posts=posts)

@blog.route('/blog/<slug>')
def post(slug):
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    if not post.published and not (current_user.is_authenticated and current_user.is_admin):
        flash('This blog post is not published yet.', 'warning')
        return redirect(url_for('blog.index'))
    return render_template('blog/post.html', post=post)

@blog.route('/admin/blog-posts')
@login_required
def blog_posts():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog_posts.html', blog_posts=posts)

@blog.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = bleach.clean(request.form.get('content') or '', tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        excerpt = request.form.get('excerpt')
        featured_image = request.form.get('featured_image')
        published = bool(request.form.get('published'))
        
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('blog.create_post'))
        
        post = BlogPost()
        post.title = title
        post.content = content
        post.excerpt = excerpt
        post.featured_image = featured_image
        post.published = published
        post.user_id = current_user.id
        post.slug = post.generate_slug()
        
        try:
            db.session.add(post)
            db.session.commit()
            flash('Blog post created successfully!', 'success')
            return redirect(url_for('blog.blog_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating blog post: {str(e)}', 'danger')
            return redirect(url_for('blog.create_post'))
    
    return render_template('admin/blog_post_form.html', post=None)

@blog.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = bleach.clean(request.form.get('content') or '', tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        excerpt = request.form.get('excerpt')
        featured_image = request.form.get('featured_image')
        published = bool(request.form.get('published'))
        
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('blog.edit_post', post_id=post_id))
        
        try:
            post.title = title
            if title != post.title:
                post.slug = post.generate_slug()
            post.content = content
            post.excerpt = excerpt
            post.featured_image = featured_image
            post.published = published
            
            db.session.commit()
            flash('Blog post updated successfully!', 'success')
            return redirect(url_for('blog.blog_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating blog post: {str(e)}', 'danger')
            return redirect(url_for('blog.edit_post', post_id=post_id))
    
    return render_template('admin/blog_post_form.html', post=post)

@blog.route('/blog/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    post = BlogPost.query.get_or_404(post_id)
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Blog post deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting blog post: {str(e)}', 'danger')
    
    return redirect(url_for('blog.blog_posts'))

@blog.route('/blog/toggle/<int:post_id>')
@login_required
def toggle_post(post_id):
    if not current_user.is_admin:
        flash('Access denied. Admin rights required.', 'danger')
        return redirect(url_for('index'))
    
    post = BlogPost.query.get_or_404(post_id)
    
    try:
        post.published = not post.published
        db.session.commit()
        status = 'published' if post.published else 'unpublished'
        flash(f'Blog post {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling blog post status: {str(e)}', 'danger')
    
    return redirect(url_for('blog.blog_posts'))
