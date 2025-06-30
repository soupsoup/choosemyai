# Deploy AI Tools Directory to Netlify

## Step 1: Download Your Code
1. In Replit, click the three dots menu (⋯) in the file browser
2. Select "Download as zip"
3. Extract the zip file on your computer

## Step 2: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click "New repository" (green button)
3. Name it: `ai-tools-directory`
4. Make it Public
5. Don't initialize with README (we have one)
6. Click "Create repository"

## Step 3: Upload to GitHub

**Option A: Using GitHub Web Interface (Easier)**
1. On your new repo page, click "uploading an existing file"
2. Drag and drop all files from your extracted folder
3. Commit message: "Initial commit - AI Tools Directory"
4. Click "Commit new files"

**Option B: Using Git Commands (if you have Git installed)**
```bash
cd path/to/your/extracted/folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/ai-tools-directory.git
git push -u origin main
```

## Step 4: Deploy to Netlify

1. Go to [netlify.com](https://netlify.com)
2. Sign up/login (you can use GitHub account)
3. Click "New site from Git"
4. Choose "GitHub" and authorize Netlify
5. Select your `ai-tools-directory` repository
6. Netlify will auto-detect settings from `netlify.toml`
7. Click "Deploy site"

## Step 5: Set Up Database

Since Netlify doesn't include PostgreSQL, you need a database service:

**Recommended: Supabase (Free)**
1. Go to [supabase.com](https://supabase.com)
2. Sign up and create new project
3. Go to Settings > Database
4. Copy the connection string (looks like: `postgresql://postgres:[password]@[host]:5432/postgres`)

**Alternative: Neon (Free)**
1. Go to [neon.tech](https://neon.tech)
2. Sign up and create database
3. Copy connection string

## Step 6: Configure Environment Variables

1. In Netlify dashboard, go to your site
2. Click "Site settings" > "Environment variables"
3. Add variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string from Step 5
4. Click "Save"

## Step 7: Initialize Database

1. In Netlify dashboard, go to "Functions" tab
2. You'll need to run the database initialization manually
3. Or use the database provider's SQL editor to run:

```sql
-- Copy the content from init_db.py and run the SQL commands
-- This creates all necessary tables
```

## Step 8: Test Your Site

1. Your site will be available at: `https://YOUR-SITE-NAME.netlify.app`
2. Login with:
   - Username: `admin`
   - Password: `admin123`

## Important Notes

- Change the admin password immediately after deployment
- The site will have HTTPS automatically (fixes your SSL issue!)
- Netlify provides custom domains if needed
- Database needs to be set up separately (unlike Heroku)

## If You Need Help

The most common issue is database connection. Make sure:
1. DATABASE_URL is correctly set in Netlify environment variables
2. Database service (Supabase/Neon) is running
3. Connection string includes username, password, and correct host

Your site should work perfectly once these steps are complete!