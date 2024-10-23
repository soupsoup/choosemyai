from app import app, db
from models import Category, Tool, User

def seed_data():
    # Clear existing data
    Tool.query.delete()
    Category.query.delete()
    User.query.delete()
    db.session.commit()  # Commit the deletions first
    
    # Create a moderator user
    moderator = User()
    moderator.username = "moderator"
    moderator.email = "moderator@example.com"
    moderator.is_moderator = True
    moderator.set_password("moderator123")
    db.session.add(moderator)
    db.session.commit()  # Commit to get the user ID
    
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
    
    # Create tools
    tools = [
        {
            'category': 'Text Generation',
            'name': 'ChatGPT',
            'description': 'Advanced language model for generating human-like text, writing assistance, and creative content generation.',
            'url': 'https://chat.openai.com'
        },
        {
            'category': 'Text Generation',
            'name': 'Claude',
            'description': 'AI assistant capable of complex analysis, writing, and coding with high accuracy and detailed responses.',
            'url': 'https://claude.ai'
        },
        {
            'category': 'Image Generation',
            'name': 'DALL-E',
            'description': 'Creates detailed images from natural language descriptions, capable of generating unique artistic content.',
            'url': 'https://labs.openai.com'
        },
        {
            'category': 'Image Generation',
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
        tool.category_id = category_objects[tool_data['category']].id
        tool.user_id = moderator.id
        tool.is_approved = True
        db.session.add(tool)
    
    db.session.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
