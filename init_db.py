from app import app, db
from models import User, Category, Tool, Comment, ToolVote, CommentVote, AppearanceSettings, BlogPost

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
