from app import app, db
import seed_data

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()  # Clear existing tables
        db.create_all()  # Create new tables with updated schema
        seed_data.seed_data()  # Seed the database with initial data
        print("Database initialized successfully!")
