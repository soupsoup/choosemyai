#!/usr/bin/env python3
"""
Script to import AI tools from a JSON file into Supabase database.
Usage: python import_tools_supabase.py <json_file_path>
"""

import json
import sys
import os
from datetime import datetime
from supabase import create_client, Client

def get_supabase_client():
    """Create and return a Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables must be set.")
        print("Please set these variables with your Supabase project credentials.")
        sys.exit(1)
    
    return create_client(url, key)

def get_or_create_category(supabase: Client, name: str, description: str = ""):
    """Get an existing category or create a new one."""
    # Check if category exists
    result = supabase.table('categories').select('*').eq('name', name).execute()
    
    if result.data:
        return result.data[0]
    
    # Create new category
    new_category = {
        'name': name,
        'description': description
    }
    
    result = supabase.table('categories').insert(new_category).execute()
    if result.data:
        print(f"Created new category: {name}")
        return result.data[0]
    else:
        print(f"Error creating category {name}: {result}")
        return None

def get_admin_user(supabase: Client):
    """Get the admin user for tool ownership."""
    result = supabase.table('users').select('*').eq('is_admin', True).limit(1).execute()
    
    if result.data:
        return result.data[0]
    
    print("Error: No admin user found. Please create an admin user first.")
    return None

def import_tools_from_json(json_file_path: str):
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
    
    # Initialize Supabase client
    supabase = get_supabase_client()
    
    # Get admin user
    admin_user = get_admin_user(supabase)
    if not admin_user:
        return False
    
    imported_count = 0
    skipped_count = 0
    
    for tool_data in tools_data:
        try:
            # Check if tool already exists
            existing_tool = supabase.table('tools').select('*').eq('name', tool_data.get('name', '')).execute()
            if existing_tool.data:
                print(f"Skipping existing tool: {tool_data.get('name', 'Unknown')}")
                skipped_count += 1
                continue
            
            # Create new tool
            tool = {
                'name': tool_data.get('name', 'Unknown Tool'),
                'description': tool_data.get('description', 'No description provided'),
                'url': tool_data.get('url', tool_data.get('website', '')),
                'image_url': tool_data.get('image_url', tool_data.get('logo', tool_data.get('icon', ''))),
                'youtube_url': tool_data.get('youtube_url', tool_data.get('video', '')),
                'resources': json.dumps(tool_data.get('resources', [])) if isinstance(tool_data.get('resources', []), list) else str(tool_data.get('resources', '')),
                'is_approved': tool_data.get('is_approved', True),
                'user_id': admin_user['id']
            }
            
            # Insert tool
            tool_result = supabase.table('tools').insert(tool).execute()
            if not tool_result.data:
                print(f"Error inserting tool {tool['name']}: {tool_result}")
                continue
            
            inserted_tool = tool_result.data[0]
            
            # Handle categories
            categories = tool_data.get('categories', tool_data.get('category', []))
            if isinstance(categories, str):
                categories = [categories]
            
            # Map common category names to match existing categories
            category_mapping = {
                'Image Generator': 'AI Image Generation',
                'Text Generator': 'AI Writing',
                'Video Generator': 'AI Video',
                'Audio Generator': 'AI Audio',
                'Code Assistants': 'AI Development',
                'Data Analysis': 'AI Research',
                'Marketing': 'AI Business',
                'Social Media': 'AI Business',
                'SEO': 'AI Business',
                'Workflow Automation': 'AI Productivity'
            }
            
            for cat_name in categories:
                # Use mapping if available, otherwise use original name
                mapped_name = category_mapping.get(cat_name, cat_name)
                category = get_or_create_category(supabase, mapped_name)
                
                if category:
                    # Create tool-category relationship
                    tool_category = {
                        'tool_id': inserted_tool['id'],
                        'category_id': category['id']
                    }
                    
                    # Check if relationship already exists
                    existing_rel = supabase.table('tool_categories').select('*').eq('tool_id', inserted_tool['id']).eq('category_id', category['id']).execute()
                    if not existing_rel.data:
                        supabase.table('tool_categories').insert(tool_category).execute()
            
            print(f"Imported tool: {tool['name']}")
            imported_count += 1
            
        except Exception as e:
            print(f"Error importing tool {tool_data.get('name', 'Unknown')}: {e}")
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
        print("Usage: python import_tools_supabase.py <json_file_path>")
        print("\nOr use 'python import_tools_supabase.py --sample' to see the expected JSON format")
        print("\nMake sure to set the following environment variables:")
        print("export SUPABASE_URL=your_supabase_url")
        print("export SUPABASE_ANON_KEY=your_supabase_anon_key")
        sys.exit(1)
    
    if sys.argv[1] == "--sample":
        print_sample_json()
        sys.exit(0)
    
    json_file = sys.argv[1]
    success = import_tools_from_json(json_file)
    if success:
        print("Import completed successfully!")
    else:
        print("Import failed!")
        sys.exit(1) 