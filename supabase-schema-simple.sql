-- ChooseMyAI Database Schema for Supabase (Simplified)
-- Run this in your Supabase SQL Editor

-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(256) NOT NULL,
  is_moderator BOOLEAN DEFAULT FALSE,
  is_admin BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tools table
CREATE TABLE tools (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  url VARCHAR(500) NOT NULL,
  image_url VARCHAR(500),
  youtube_url VARCHAR(500),
  is_approved BOOLEAN DEFAULT FALSE,
  resources TEXT,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tool-Category relationship table
CREATE TABLE tool_categories (
  id SERIAL PRIMARY KEY,
  tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
  category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(tool_id, category_id)
);

-- Comments table
CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Blog posts table
CREATE TABLE blog_posts (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  slug VARCHAR(200) UNIQUE NOT NULL,
  content TEXT NOT NULL,
  published BOOLEAN DEFAULT FALSE,
  featured_image VARCHAR(500),
  excerpt TEXT,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tool votes table
CREATE TABLE tool_votes (
  id SERIAL PRIMARY KEY,
  tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  value INTEGER NOT NULL CHECK (value IN (-1, 1)), -- -1 for downvote, 1 for upvote
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(tool_id, user_id)
);

-- Comment votes table
CREATE TABLE comment_votes (
  id SERIAL PRIMARY KEY,
  comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  value INTEGER NOT NULL CHECK (value IN (-1, 1)), -- -1 for downvote, 1 for upvote
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(comment_id, user_id)
);

-- Appearance settings table
CREATE TABLE appearance_settings (
  id SERIAL PRIMARY KEY,
  primary_color VARCHAR(7) DEFAULT '#0d6efd',
  secondary_color VARCHAR(7) DEFAULT '#6c757d',
  background_color VARCHAR(7) DEFAULT '#212529',
  font_color VARCHAR(7) DEFAULT '#ffffff',
  font_family TEXT DEFAULT 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif',
  header_background VARCHAR(7) DEFAULT '#0d6efd',
  footer_background VARCHAR(7) DEFAULT '#6c757d',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_tools_user_id ON tools(user_id);
CREATE INDEX idx_tools_is_approved ON tools(is_approved);
CREATE INDEX idx_tool_categories_tool_id ON tool_categories(tool_id);
CREATE INDEX idx_tool_categories_category_id ON tool_categories(category_id);
CREATE INDEX idx_comments_tool_id ON comments(tool_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_blog_posts_user_id ON blog_posts(user_id);
CREATE INDEX idx_blog_posts_published ON blog_posts(published);
CREATE INDEX idx_tool_votes_tool_id ON tool_votes(tool_id);
CREATE INDEX idx_tool_votes_user_id ON tool_votes(user_id);
CREATE INDEX idx_comment_votes_comment_id ON comment_votes(comment_id);
CREATE INDEX idx_comment_votes_user_id ON comment_votes(user_id);

-- Insert default appearance settings
INSERT INTO appearance_settings (primary_color, secondary_color, background_color, font_color, header_background, footer_background) 
VALUES ('#0d6efd', '#6c757d', '#212529', '#ffffff', '#0d6efd', '#6c757d');

-- Insert default categories
INSERT INTO categories (name, description) VALUES
  ('AI Writing', 'AI-powered writing and content creation tools'),
  ('AI Image Generation', 'Tools for creating images with AI'),
  ('AI Video', 'AI video creation and editing tools'),
  ('AI Audio', 'AI audio generation and processing tools'),
  ('AI Chatbots', 'Chatbot and conversational AI tools'),
  ('AI Research', 'Research and analysis AI tools'),
  ('AI Productivity', 'Productivity and workflow AI tools'),
  ('AI Development', 'AI tools for developers'),
  ('AI Business', 'Business and marketing AI tools');

-- Insert admin user (password: admin123)
-- Note: You should change this password after setup
INSERT INTO users (username, email, password_hash, is_admin, is_moderator) 
VALUES ('admin', 'admin@choosemyai.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', true, true);

-- Insert sample tools
INSERT INTO tools (name, description, url, image_url, user_id, is_approved) VALUES
  ('ChatGPT', 'Advanced language model for conversation and text generation', 'https://chat.openai.com', 'https://via.placeholder.com/300x200?text=ChatGPT', 1, true),
  ('Midjourney', 'AI art generation tool for creating stunning images', 'https://midjourney.com', 'https://via.placeholder.com/300x200?text=Midjourney', 1, true),
  ('GitHub Copilot', 'AI-powered code completion and generation tool', 'https://github.com/features/copilot', 'https://via.placeholder.com/300x200?text=GitHub+Copilot', 1, true);

-- Associate tools with categories
INSERT INTO tool_categories (tool_id, category_id) VALUES
  (1, 1), -- ChatGPT - AI Writing
  (1, 6), -- ChatGPT - AI Research
  (2, 2), -- Midjourney - AI Image Generation
  (3, 8); -- GitHub Copilot - AI Development

-- Insert sample blog post
INSERT INTO blog_posts (title, slug, content, published, user_id, excerpt) VALUES
  ('Welcome to ChooseMyAI', 'welcome-to-choosemyai', 
   '<h1>Welcome to ChooseMyAI!</h1><p>This is your comprehensive directory of AI tools and resources. Here you can discover, rate, and review the best AI tools available today.</p><h2>Getting Started</h2><ul><li>Browse tools by category</li><li>Search for specific tools</li><li>Submit your own AI tools</li><li>Rate and comment on tools</li></ul><p>Happy exploring!</p>', 
   true, 1, 'Welcome to your comprehensive directory of AI tools and resources.');

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tools_updated_at BEFORE UPDATE ON tools FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE ON blog_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tool_votes_updated_at BEFORE UPDATE ON tool_votes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comment_votes_updated_at BEFORE UPDATE ON comment_votes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appearance_settings_updated_at BEFORE UPDATE ON appearance_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 