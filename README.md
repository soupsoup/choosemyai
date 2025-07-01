# AI Tools Directory

A modern web-based AI tools directory built with Flask, featuring user authentication, admin management, tool submission and moderation capabilities, and appearance customization.

## Features

- **User Management**: Registration, login, role-based access control
- **Tool Directory**: Submit, browse, and vote on AI tools
- **Admin Panel**: Comprehensive admin interface for managing users, tools, and site appearance
- **Blog System**: Create and manage blog posts
- **Appearance Customization**: Full theme customization with color and font controls
- **Category Management**: Organize tools by categories
- **Comment System**: User comments and voting on tools
- **Import/Export**: Backup and restore functionality

## Technologies

- **Backend**: Python Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Authentication**: Flask-Login
- **Deployment**: Heroku-ready with Gunicorn

## Quick Start

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-tools-directory.git
   cd ai-tools-directory
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/dbname"
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the application:
   ```bash
   python main.py
   ```

### Deploy to Netlify

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/ai-tools-directory.git
   git push -u origin main
   ```

2. **Connect to Netlify**:
   - Go to [netlify.com](https://netlify.com) and sign up/login
   - Click "New site from Git"
   - Connect your GitHub account
   - Select your repository
   - Netlify will automatically detect the `netlify.toml` configuration

3. **Set Environment Variables**:
   - In Netlify dashboard, go to Site settings > Environment variables
   - Add `DATABASE_URL` with your PostgreSQL connection string
   - Consider using [Supabase](https://supabase.com) or [Neon](https://neon.tech) for PostgreSQL hosting

4. **Deploy**:
   - Netlify will automatically build and deploy
   - Your site will be available at `https://your-site-name.netlify.app`

### Alternative: Deploy to Heroku

1. Create a Heroku app:
   ```bash
   heroku create your-app-name
   ```

2. Add PostgreSQL addon:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

4. Initialize the database:
   ```bash
   heroku run python init_db.py
   ```

## Admin Access

Default admin credentials:
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the admin password immediately after deployment!

## Configuration

The application uses environment variables for configuration:

- `DATABASE_URL`: PostgreSQL database connection string
- `FLASK_ENV`: Set to 'production' for production deployments

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please use the GitHub Issues page.# Force deployment - Mon Jun 30 21:45:18 EDT 2025
