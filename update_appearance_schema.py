from app import app, db
from models import AppearanceSettings

def update_appearance_schema():
    with app.app_context():
        try:
            # Drop and recreate the appearance_settings table
            AppearanceSettings.__table__.drop(db.engine, checkfirst=True)
            AppearanceSettings.__table__.create(db.engine)
            
            # Create new settings with defaults
            new_settings = AppearanceSettings()
            db.session.add(new_settings)
            db.session.commit()
            
            print("Appearance settings schema updated successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during schema update: {e}")
            raise

if __name__ == "__main__":
    update_appearance_schema()
