from flask import Blueprint, jsonify
from models import Tool, Category
from sqlalchemy import desc, func, or_
from app import db

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/tools', methods=['GET'])
def get_tools():
    tools = Tool.query.filter_by(is_approved=True).all()
    return jsonify({
        'tools': [{
            'id': tool.id,
            'name': tool.name,
            'description': tool.description,
            'url': tool.url,
            'category': {
                'id': tool.category.id,
                'name': tool.category.name
            },
            'votes': tool.vote_count,
            'created_at': tool.created_at.isoformat()
        } for tool in tools]
    })

@api.route('/tools/<int:tool_id>', methods=['GET'])
def get_tool(tool_id):
    tool = Tool.query.filter_by(id=tool_id, is_approved=True).first()
    if not tool:
        return jsonify({'error': 'Tool not found'}), 404
    
    return jsonify({
        'id': tool.id,
        'name': tool.name,
        'description': tool.description,
        'url': tool.url,
        'category': {
            'id': tool.category.id,
            'name': tool.category.name
        },
        'votes': tool.vote_count,
        'created_at': tool.created_at.isoformat(),
        'comments': [{
            'id': comment.id,
            'content': comment.content,
            'votes': comment.vote_count,
            'created_at': comment.created_at.isoformat()
        } for comment in tool.comments]
    })

@api.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'categories': [{
            'id': category.id,
            'name': category.name,
            'description': category.description
        } for category in categories]
    })

@api.route('/categories/<int:category_id>/tools', methods=['GET'])
def get_tools_by_category(category_id):
    tools = Tool.query.filter_by(category_id=category_id, is_approved=True).all()
    return jsonify({
        'tools': [{
            'id': tool.id,
            'name': tool.name,
            'description': tool.description,
            'url': tool.url,
            'votes': tool.vote_count,
            'created_at': tool.created_at.isoformat()
        } for tool in tools]
    })
