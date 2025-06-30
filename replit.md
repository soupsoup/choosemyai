# AI Tools Directory - Project Documentation

## Overview
A comprehensive AI tools directory web application built with Flask. Features user authentication, admin management interface, tool submission and moderation capabilities, appearance customization, and user management functionality.

## Current Status
- **Database**: PostgreSQL with all tables created
- **Authentication**: Working with admin user (username: admin, password: admin123)
- **Features**: All core functionality implemented including user management, tool moderation, appearance customization
- **Deployment**: Ready for GitHub deployment with production configuration files

## Recent Changes
- **2025-06-30**: Fixed admin password reset functionality
- **2025-06-30**: Created production deployment files (Procfile, runtime.txt, app.json)
- **2025-06-30**: Added GitHub deployment configuration
- **2025-06-30**: Installed gunicorn for production server

## Project Architecture
- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with tables for users, tools, categories, comments, votes, blog posts, appearance settings
- **Authentication**: Flask-Login with role-based access control
- **Frontend**: Bootstrap 5 with custom theming system
- **Deployment**: Heroku-ready with environment variable configuration

## User Preferences
- User prefers simple, everyday language explanations
- Wants comprehensive solutions with minimal back-and-forth
- Prioritizes working functionality over complex explanations

## Key Configuration
- **Admin Access**: username `admin`, password `admin123`
- **Database**: Uses environment variable `DATABASE_URL`
- **Server**: Runs on port 5000 (development), configurable for production
- **SSL**: Development server uses HTTP only; HTTPS requires production deployment

## Deployment Notes
- All necessary files created for GitHub/Heroku deployment
- Database initialization script included (init_db.py)
- Production-ready configuration with gunicorn server
- Environment variables properly configured for cloud deployment