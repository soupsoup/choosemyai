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
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
