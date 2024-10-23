from app import app, db
from models import Category, Tool

def seed_data():
    # Clear existing data
    Tool.query.delete()
    Category.query.delete()
    
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
        cat = Category(name=name, description=description)
        db.session.add(cat)
        category_objects[name] = cat
    
    # Create tools
    tools = [
        # Text Generation
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
        # Image Generation
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
        },
        # Code Assistant
        {
            'category': 'Code Assistant',
            'name': 'GitHub Copilot',
            'description': 'AI pair programmer that suggests code completions in real-time across multiple programming languages.',
            'url': 'https://github.com/features/copilot'
        },
        {
            'category': 'Code Assistant',
            'name': 'Tabnine',
            'description': 'AI code completion tool that learns your coding patterns to provide accurate suggestions.',
            'url': 'https://www.tabnine.com'
        },
        # Data Analysis
        {
            'category': 'Data Analysis',
            'name': 'Obviously AI',
            'description': 'No-code AI platform for predictive analytics and automated machine learning.',
            'url': 'https://www.obviously.ai'
        },
        {
            'category': 'Data Analysis',
            'name': 'DataRobot',
            'description': 'Enterprise AI platform for automated machine learning and predictive modeling.',
            'url': 'https://www.datarobot.com'
        },
        # Chat Bots
        {
            'category': 'Chat Bots',
            'name': 'BotPress',
            'description': 'Open-source platform for building, deploying, and managing conversational AI assistants.',
            'url': 'https://botpress.com'
        },
        {
            'category': 'Chat Bots',
            'name': 'Rasa',
            'description': 'Open source machine learning framework for automated text and voice-based conversations.',
            'url': 'https://rasa.com'
        }
    ]
    
    for tool_data in tools:
        tool = Tool(
            name=tool_data['name'],
            description=tool_data['description'],
            url=tool_data['url'],
            category=category_objects[tool_data['category']]
        )
        db.session.add(tool)
    
    db.session.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
