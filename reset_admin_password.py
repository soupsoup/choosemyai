#!/usr/bin/env python3
"""Reset admin password script"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    with app.app_context():
        # Find admin user
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            # Set new password
            new_password = 'admin123'
            admin_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"Admin password reset successfully!")
            print(f"Username: admin")
            print(f"Password: {new_password}")
        else:
            print("Admin user not found!")

if __name__ == '__main__':
    reset_admin_password()