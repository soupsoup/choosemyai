from app import app, db
from models import AppearanceSettings

def update_appearance_schema():
    with app.app_context():
        # 1. Backup existing settings
        existing_settings = AppearanceSettings.query.first()
        settings_backup = {c.name: getattr(existing_settings, c.name) 
                          for c in existing_settings.__table__.columns} if existing_settings else None
        
        # 2. Drop and recreate the appearance_settings table
        AppearanceSettings.__table__.drop(db.engine, checkfirst=True)
        AppearanceSettings.__table__.create(db.engine)
        
        # 3. Restore settings with new defaults
        if settings_backup:
            new_settings = AppearanceSettings()
            for key, value in settings_backup.items():
                if hasattr(new_settings, key):
                    setattr(new_settings, key, value)
            
            # Set defaults for new columns if they don't exist in backup
            defaults = {
                'comment_box_background_color': '#2c3034',
                'comment_box_text_color': '#ffffff',
                'container_background_color': '#2c3034',
                'container_border_color': '#373b3e',
                'search_box_background_color': '#2c3034',
                'search_box_border_color': '#373b3e',
                'category_item_background_color': '#2c3034',
                'category_item_hover_color': '#373b3e',
                'category_item_text_color': '#ffffff',
                'category_item_hover_text_color': '#ffffff'
            }
            
            for key, value in defaults.items():
                if key not in settings_backup:
                    setattr(new_settings, key, value)
            
            db.session.add(new_settings)
            db.session.commit()
        else:
            # Create new settings with defaults
            new_settings = AppearanceSettings()
            db.session.add(new_settings)
            db.session.commit()
        
        print("Appearance settings schema updated successfully!")

if __name__ == "__main__":
    update_appearance_schema()
