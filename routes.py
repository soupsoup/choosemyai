from flask import render_template, request, redirect, url_for, jsonify, flash
from flask_login import current_user, login_required
from app import app, db
from models import Category, Tool, Comment, ToolVote, CommentVote
from sqlalchemy import desc, func
from auth import auth

app.register_blueprint(auth)

@app.route('/')
def index():
    sort_by = request.args.get('sort', 'votes')
    categories = Category.query.all()
    
    if sort_by == 'votes':
        tools = Tool.query\
            .filter_by(is_approved=True)\
            .join(ToolVote, Tool.id == ToolVote.tool_id, isouter=True)\
            .group_by(Tool.id)\
            .order_by(desc(func.coalesce(func.sum(ToolVote.value), 0)))\
            .all()
    else:  # sort by date
        tools = Tool.query\
            .filter_by(is_approved=True)\
            .order_by(desc(Tool.created_at))\
            .all()
    
    return render_template('index.html', categories=categories, tools=tools)

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    sort_by = request.args.get('sort', 'votes')
    
    if sort_by == 'votes':
        tools = Tool.query\
            .filter_by(category_id=category_id, is_approved=True)\
            .join(ToolVote, Tool.id == ToolVote.tool_id, isouter=True)\
            .group_by(Tool.id)\
            .order_by(desc(func.coalesce(func.sum(ToolVote.value), 0)))\
            .all()
    else:  # sort by date
        tools = Tool.query\
            .filter_by(category_id=category_id, is_approved=True)\
            .order_by(desc(Tool.created_at))\
            .all()
    
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
    else:  # sort by date
        comments = Comment.query\
            .filter_by(tool_id=tool_id)\
            .order_by(desc(Comment.created_at))\
            .all()
    
    return render_template('tool.html', tool=tool, comments=comments)

@app.route('/tool/<int:tool_id>/comment', methods=['POST'])
@login_required
def add_comment(tool_id):
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, tool_id=tool_id, user_id=current_user.id)
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
        vote = ToolVote(tool_id=tool_id, user_id=current_user.id, value=value)
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
        vote = CommentVote(comment_id=comment_id, user_id=current_user.id, value=value)
        db.session.add(vote)
    
    db.session.commit()
    comment = Comment.query.get_or_404(comment_id)
    return jsonify({'votes': comment.vote_count})

@app.route('/submit-tool', methods=['GET', 'POST'])
@login_required
def submit_tool():
    if request.method == 'POST':
        tool = Tool(
            name=request.form['name'],
            description=request.form['description'],
            url=request.form['url'],
            category_id=request.form['category'],
            user_id=current_user.id,
            is_approved=False
        )
        db.session.add(tool)
        db.session.commit()
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
