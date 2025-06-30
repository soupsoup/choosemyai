# Supabase Setup Guide for ChooseMyAI

This guide will help you set up Supabase as your database for the ChooseMyAI application.

## 🚀 Quick Start

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `choosemyai` (or your preferred name)
   - **Database Password**: Choose a strong password
   - **Region**: Select the region closest to your users
5. Click "Create new project"

### 2. Set Up the Database Schema

1. In your Supabase dashboard, go to the **SQL Editor**
2. Copy the contents of `supabase-schema.sql`
3. Paste it into the SQL editor and click "Run"
4. This will create all the necessary tables, indexes, and sample data

### 3. Get Your API Keys

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://your-project.supabase.co`)
   - **Anon public key** (starts with `eyJ...`)

### 4. Configure Environment Variables

#### For Netlify Deployment:

1. Go to your Netlify dashboard
2. Navigate to your site → **Site settings** → **Environment variables**
3. Add the following variables:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   ```

#### For Local Development:

1. Create a `.env` file in your project root:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   ```

### 5. Deploy Your Application

1. Push your changes to GitHub
2. Netlify will automatically redeploy with the new environment variables
3. Your app will now use Supabase as the database!

## 📊 Database Features

### Tables Created:
- **users** - User accounts and authentication
- **categories** - AI tool categories
- **tools** - AI tools directory
- **tool_categories** - Many-to-many relationship between tools and categories
- **comments** - User comments on tools
- **blog_posts** - Blog content
- **tool_votes** - User votes on tools
- **comment_votes** - User votes on comments
- **appearance_settings** - Site customization settings

### Sample Data Included:
- **Admin User**: `admin` / `admin123`
- **8 Default Categories**: AI Writing, AI Image Generation, etc.
- **3 Sample Tools**: ChatGPT, Midjourney, GitHub Copilot
- **1 Sample Blog Post**: Welcome to ChooseMyAI

## 🔐 Security Features

### Row Level Security (RLS):
- Public read access to approved tools and published blog posts
- Users can only create/update their own content
- Admins and moderators have full access
- Secure authentication and authorization

### Policies:
- **Public Access**: Browse tools, categories, and published blog posts
- **User Access**: Create tools, comments, and vote
- **Admin Access**: Full CRUD operations on all data

## 🛠️ Development

### Local Development:
```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Start development server
npm run dev
```

### Database Operations:
- The app automatically uses Supabase when environment variables are set
- Falls back to in-memory database for development/testing
- All database operations are handled through the `utils/database.js` service

## 📈 Monitoring

### Supabase Dashboard:
- **Table Editor**: View and edit data directly
- **SQL Editor**: Run custom queries
- **Logs**: Monitor API requests and errors
- **Analytics**: Track usage and performance

### Key Metrics to Monitor:
- API request count
- Database query performance
- Error rates
- User authentication events

## 🔧 Troubleshooting

### Common Issues:

1. **"Supabase environment variables not found"**
   - Check that `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set correctly
   - Verify the environment variables in Netlify dashboard

2. **"Permission denied" errors**
   - Check Row Level Security policies in Supabase
   - Verify user authentication is working

3. **"Table does not exist" errors**
   - Run the `supabase-schema.sql` script in Supabase SQL Editor
   - Check that all tables were created successfully

### Getting Help:
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
- [GitHub Issues](https://github.com/your-repo/issues)

## 🚀 Production Considerations

### Performance:
- Supabase automatically handles connection pooling
- Use indexes for frequently queried columns
- Monitor query performance in the dashboard

### Scaling:
- Supabase handles database scaling automatically
- Consider using read replicas for high-traffic applications
- Implement caching for frequently accessed data

### Backup:
- Supabase provides automatic daily backups
- Point-in-time recovery available
- Export data using the dashboard or API

## 📝 Next Steps

1. **Customize the Schema**: Modify tables to match your specific needs
2. **Add Authentication**: Implement user registration and login
3. **Set Up Email**: Configure email notifications
4. **Add Analytics**: Track user behavior and tool usage
5. **Implement Caching**: Add Redis or similar for better performance

---

**Need help?** Check the [Supabase documentation](https://supabase.com/docs) or reach out to the community! 