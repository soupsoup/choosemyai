from app import app, db
from models import AppearanceSettings
from sqlalchemy import text

def migrate_appearance_settings():
    with app.app_context():
        # Add missing columns if they don't exist
        connection = db.engine.connect()
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('appearance_settings')]
        
        # New columns with their default values
        new_columns = {
            'container_background_color': '#2c3034',
            'container_border_color': '#373b3e',
            'search_box_background_color': '#2c3034',
            'search_box_border_color': '#373b3e',
            'category_item_background_color': '#2c3034',
            'category_item_hover_color': '#373b3e',
            'category_item_text_color': '#ffffff',
            'category_item_hover_text_color': '#ffffff'
        }
        
        try:
            # Start a transaction
            trans = connection.begin()
            
            # Add missing columns
            for column_name, default_value in new_columns.items():
                if column_name not in existing_columns:
                    sql = text(f'ALTER TABLE appearance_settings ADD COLUMN IF NOT EXISTS {column_name} VARCHAR(7) DEFAULT :default')
                    connection.execute(sql, {'default': default_value})
            
            # Commit the transaction
            trans.commit()
            
            # Update any existing rows with default values where columns are null
            for column_name, default_value in new_columns.items():
                sql = text(f'UPDATE appearance_settings SET {column_name} = :default WHERE {column_name} IS NULL')
                connection.execute(sql, {'default': default_value})
                connection.commit()
                
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            if trans:
                trans.rollback()
            raise
        finally:
            connection.close()

if __name__ == '__main__':
    migrate_appearance_settings()
