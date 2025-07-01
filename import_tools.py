#!/usr/bin/env python3
"""
Script to import AI tools from a JSON file into the database.
Usage: python import_tools.py <json_file_path>
"""

import json
import sys
import os
from datetime import datetime

# Add the current directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from models import Tool, Category, User
except ImportError as e:
    print(f"Error importing models: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)

def get_or_create_category(name, description=""):
    """Get an existing category or create a new one."""
    category = Category.query.filter_by(name=name).first()
    if not category:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        print(f"Created new category: {name}")
    return category

def get_admin_user():
    """Get the admin user for tool ownership."""
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        # Create admin user if it doesn't exist
        admin = User(
            username="admin",
            email="admin@choosemyai.com",
            is_admin=True,
            is_moderator=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Created admin user")
    return admin

def import_tools_from_json(json_file_path):
    """Import tools from a JSON file."""
    
    if not os.path.exists(json_file_path):
        print(f"Error: File {json_file_path} not found.")
        return False
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Handle different JSON structures
    tools_data = []
    if isinstance(data, list):
        tools_data = data
    elif isinstance(data, dict):
        # Check for common keys that might contain the tools array
        if 'tools' in data:
            tools_data = data['tools']
        elif 'data' in data:
            tools_data = data['data']
        elif 'items' in data:
            tools_data = data['items']
        else:
            # Assume the dict itself is a single tool
            tools_data = [data]
    else:
        print("Error: JSON must be an array of tools or an object containing tools.")
        return False
    
    admin_user = get_admin_user()
    imported_count = 0
    skipped_count = 0
    
    for tool_data in tools_data:
        try:
            # Check if tool already exists
            existing_tool = Tool.query.filter_by(name=tool_data.get('name', '')).first()
            if existing_tool:
                print(f"Skipping existing tool: {tool_data.get('name', 'Unknown')}")
                skipped_count += 1
                continue
            
            # Create new tool
            tool = Tool()
            
            # Required fields
            tool.name = tool_data.get('name', 'Unknown Tool')
            tool.description = tool_data.get('description', 'No description provided')
            tool.url = tool_data.get('url', tool_data.get('website', ''))
            
            # Optional fields
            tool.image_url = tool_data.get('image_url', tool_data.get('logo', tool_data.get('icon', '')))
            tool.youtube_url = tool_data.get('youtube_url', tool_data.get('video', ''))
            tool.resources = tool_data.get('resources', tool_data.get('additional_info', ''))
            
            # Set approval status (default to True for imported tools)
            tool.is_approved = tool_data.get('is_approved', True)
            
            # Set user
            tool.user_id = admin_user.id
            
            # Handle categories
            categories = tool_data.get('categories', tool_data.get('category', []))
            if isinstance(categories, str):
                categories = [categories]
            
            tool_categories = []
            for cat_name in categories:
                category = get_or_create_category(cat_name)
                tool_categories.append(category)
            
            tool.categories = tool_categories
            
            db.session.add(tool)
            db.session.commit()
            
            print(f"Imported tool: {tool.name}")
            imported_count += 1
            
        except Exception as e:
            print(f"Error importing tool {tool_data.get('name', 'Unknown')}: {e}")
            db.session.rollback()
            continue
    
    print(f"\nImport completed!")
    print(f"Imported: {imported_count} tools")
    print(f"Skipped: {skipped_count} tools (already exist)")
    
    return True

def print_sample_json():
    """Print a sample JSON structure for reference."""
    sample = {
        "tools": [
            {
                "name": "Example AI Tool",
                "description": "This is an example AI tool description",
                "url": "https://example.com",
                "image_url": "https://example.com/logo.png",
                "youtube_url": "https://youtube.com/watch?v=example",
                "categories": ["AI Writing", "AI Productivity"],
                "resources": "Additional information about the tool",
                "is_approved": True
            }
        ]
    }
    
    print("Sample JSON structure:")
    print(json.dumps(sample, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_tools.py <json_file_path>")
        print("\nOr use 'python import_tools.py --sample' to see the expected JSON format")
        sys.exit(1)
    
    if sys.argv[1] == "--sample":
        print_sample_json()
        sys.exit(0)
    
    json_file = sys.argv[1]
    
    with app.app_context():
        success = import_tools_from_json(json_file)
        if success:
            print("Import completed successfully!")
        else:
            print("Import failed!")
            sys.exit(1) 