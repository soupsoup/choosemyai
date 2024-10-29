from app import app, db
from models import User, Category, Tool, Comment, ToolVote, CommentVote, AppearanceSettings, BlogPost

def init_db():
    with app.app_context():
        # Drop all tables first to ensure clean state
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create default appearance settings
        default_settings = AppearanceSettings()
        db.session.add(default_settings)
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_moderator=True
        )
        admin.set_password('admin123')  # Set a default password
        db.session.add(admin)
        
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
