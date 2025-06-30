# Upload to GitHub: https://github.com/soupsoup/choosemyai

## Method 1: Download and Upload (Recommended)

1. **Download from Replit**:
   - Click the three dots (⋯) in the Replit file panel
   - Select "Download as zip"
   - Extract the zip file on your computer

2. **Upload to GitHub**:
   - Go to https://github.com/soupsoup/choosemyai
   - If the repo is empty, click "uploading an existing file"
   - If it has files, click "Add file" → "Upload files"
   - Drag all files from your extracted folder
   - Commit message: "Deploy AI Tools Directory to Netlify"
   - Click "Commit new files"

## Method 2: Copy Files Manually

Go to https://github.com/soupsoup/choosemyai and create these files:

### Core Files to Upload:
- `main.py` - Flask app entry point
- `app.py` - Flask application setup  
- `models.py` - Database models
- `routes.py` - Main routes
- `auth.py` - Authentication routes
- `admin.py` - Admin functionality
- `blog.py` - Blog functionality
- `api.py` - API endpoints
- `init_db.py` - Database initialization

### Admin Module:
- `admin/__init__.py` - Admin blueprint

### Templates (create templates/ folder):
- All files from templates/ directory
- Including admin/, auth/, blog/, css/ subdirectories

### Static Files (create static/ folder):
- All files from static/ directory

### Deployment Files:
- `requirements.txt` - Python dependencies
- `netlify.toml` - Netlify configuration
- `netlify/functions/app.py` - Serverless function
- `Procfile` - For Heroku (backup option)
- `runtime.txt` - Python version
- `app.json` - App configuration
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation

## After Upload: Deploy to Netlify

1. Go to [netlify.com](https://netlify.com)
2. Click "New site from Git"
3. Connect GitHub and select your repo
4. Netlify will auto-detect the configuration
5. Set environment variable `DATABASE_URL` (use Supabase or Neon)
6. Deploy!

Your site will be live at: `https://your-site-name.netlify.app`

## Database Setup
Since you'll need a PostgreSQL database, I recommend:
- **Supabase** (free): https://supabase.com
- **Neon** (free): https://neon.tech
- Copy the connection string to Netlify environment variables

## Admin Login
- Username: `admin`
- Password: `admin123`
- Change this immediately after deployment!