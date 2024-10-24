from app import app, db
from models import Category, Tool, User, AppearanceSettings

def seed_data():
    # Clear existing data
    Tool.query.delete()
    Category.query.delete()
    User.query.delete()
    AppearanceSettings.query.delete()
    db.session.commit()  # Commit the deletions first
    
    # Create default appearance settings
    settings = AppearanceSettings()
    db.session.add(settings)
    
    # Create a moderator user
    moderator = User()
    moderator.username = "moderator"
    moderator.email = "moderator@example.com"
    moderator.is_moderator = True
    moderator.set_password("moderator123")
    db.session.add(moderator)

    # Create an admin user
    admin = User()
    admin.username = "admin"
    admin.email = "admin@example.com"
    admin.is_moderator = True
    admin.is_admin = True
    admin.set_password("admin123")
    db.session.add(admin)
    
    db.session.commit()  # Commit to get the user IDs
    
    # Create categories
    categories = {
        'Text Generation': 'AI tools for generating and manipulating text content',
        'Image Generation': 'AI tools for creating and editing images',
        'Code Assistant': 'AI-powered coding and development tools',
        'Data Analysis': 'AI tools for analyzing and visualizing data',
        'Chat Bots': 'AI-powered conversational agents and virtual assistants'
    }
    
    category_objects = {}
    for name, description in categories.items():
        cat = Category()
        cat.name = name
        cat.description = description
        db.session.add(cat)
        db.session.commit()  # Commit each category to get its ID
        category_objects[name] = cat
    
    # Create tools with multiple categories
    tools = [
        {
            'categories': ['Text Generation', 'Chat Bots'],
            'name': 'ChatGPT',
            'description': 'Advanced language model for generating human-like text, writing assistance, and creative content generation.',
            'url': 'https://chat.openai.com'
        },
        {
            'categories': ['Text Generation', 'Chat Bots', 'Code Assistant'],
            'name': 'Claude',
            'description': 'AI assistant capable of complex analysis, writing, and coding with high accuracy and detailed responses.',
            'url': 'https://claude.ai'
        },
        {
            'categories': ['Image Generation'],
            'name': 'DALL-E',
            'description': 'Creates detailed images from natural language descriptions, capable of generating unique artistic content.',
            'url': 'https://labs.openai.com'
        },
        {
            'categories': ['Image Generation'],
            'name': 'Midjourney',
            'description': 'AI art generator known for high-quality, artistic image creation from text descriptions.',
            'url': 'https://www.midjourney.com'
        }
    ]
    
    for tool_data in tools:
        tool = Tool()
        tool.name = tool_data['name']
        tool.description = tool_data['description']
        tool.url = tool_data['url']
        tool.user_id = moderator.id
        tool.is_approved = True
        tool.categories = [category_objects[cat_name] for cat_name in tool_data['categories']]
        db.session.add(tool)
    
    db.session.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
