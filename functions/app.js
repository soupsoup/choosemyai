const express = require('express');
const serverless = require('serverless-http');
const session = require('express-session');
const bcrypt = require('bcryptjs');
const sanitizeHtml = require('sanitize-html');
const path = require('path');

const app = express();

// Simple in-memory data store
const dataStore = {
  users: new Map(),
  categories: new Map(),
  tools: new Map(),
  comments: new Map(),
  blogPosts: new Map(),
  nextId: { users: 1, categories: 1, tools: 1, comments: 1, blogPosts: 1 }
};

// Seed initial data
function seedData() {
  // Create admin user
  const adminUser = {
    id: dataStore.nextId.users++,
    username: 'admin',
    email: 'admin@choosemyai.com',
    password_hash: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // admin123
    is_admin: true,
    is_moderator: true,
    created_at: new Date()
  };
  dataStore.users.set(adminUser.id, adminUser);

  // Create categories
  const categories = [
    { name: 'AI Writing', description: 'AI-powered writing and content creation tools' },
    { name: 'AI Image Generation', description: 'Tools for creating images with AI' },
    { name: 'AI Video', description: 'AI video creation and editing tools' },
    { name: 'AI Chatbots', description: 'Chatbot and conversational AI tools' },
    { name: 'AI Research', description: 'Research and analysis AI tools' },
    { name: 'AI Productivity', description: 'Productivity and workflow AI tools' },
    { name: 'AI Development', description: 'AI tools for developers' },
    { name: 'AI Business', description: 'Business and marketing AI tools' }
  ].map(cat => {
    const category = { id: dataStore.nextId.categories++, ...cat, created_at: new Date() };
    dataStore.categories.set(category.id, category);
    return category;
  });

  // Create sample tools
  const sampleTools = [
    {
      name: 'ChatGPT',
      description: 'Advanced language model for conversation and text generation',
      url: 'https://chat.openai.com',
      image_url: 'https://via.placeholder.com/300x200?text=ChatGPT',
      user_id: adminUser.id,
      is_approved: true,
      category_ids: [categories[0].id, categories[4].id]
    },
    {
      name: 'Midjourney',
      description: 'AI art generation tool for creating stunning images',
      url: 'https://midjourney.com',
      image_url: 'https://via.placeholder.com/300x200?text=Midjourney',
      user_id: adminUser.id,
      is_approved: true,
      category_ids: [categories[1].id]
    },
    {
      name: 'GitHub Copilot',
      description: 'AI-powered code completion and generation tool',
      url: 'https://github.com/features/copilot',
      image_url: 'https://via.placeholder.com/300x200?text=GitHub+Copilot',
      user_id: adminUser.id,
      is_approved: true,
      category_ids: [categories[6].id]
    }
  ].map(tool => {
    const toolObj = { id: dataStore.nextId.tools++, ...tool, created_at: new Date() };
    dataStore.tools.set(toolObj.id, toolObj);
    return toolObj;
  });

  // Create sample blog post
  const blogPost = {
    id: dataStore.nextId.blogPosts++,
    title: 'Welcome to ChooseMyAI',
    slug: 'welcome-to-choosemyai',
    content: `
      <h1>Welcome to ChooseMyAI!</h1>
      <p>This is your comprehensive directory of AI tools and resources. Here you can discover, rate, and review the best AI tools available today.</p>
      <h2>Getting Started</h2>
      <ul>
        <li>Browse tools by category</li>
        <li>Search for specific tools</li>
        <li>Submit your own AI tools</li>
        <li>Rate and comment on tools</li>
      </ul>
      <p>Happy exploring!</p>
    `,
    published: true,
    user_id: adminUser.id,
    excerpt: 'Welcome to your comprehensive directory of AI tools and resources.',
    created_at: new Date()
  };
  dataStore.blogPosts.set(blogPost.id, blogPost);
}

// Initialize data
seedData();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
  secret: 'choosemyai-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: { secure: false }
}));

// Set view engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../templates'));

// Static files
app.use('/static', express.static(path.join(__dirname, '../static')));

// Helper functions
function requireAuth(req, res, next) {
  if (!req.session.user) {
    req.session.returnTo = req.originalUrl;
    return res.redirect('/auth/login');
  }
  next();
}

function requireAdmin(req, res, next) {
  if (!req.session.user) {
    req.session.returnTo = req.originalUrl;
    return res.redirect('/auth/login');
  }
  if (!req.session.user.isAdmin) {
    req.session.flash = { type: 'danger', message: 'Access denied. Admin privileges required.' };
    return res.redirect('/');
  }
  next();
}

// Routes
app.get('/', (req, res) => {
  const tools = Array.from(dataStore.tools.values()).filter(tool => tool.is_approved);
  const categories = Array.from(dataStore.categories.values());
  res.render('index', { tools, categories, user: req.session.user });
});

app.get('/auth/login', (req, res) => {
  res.render('auth/login', { user: req.session.user });
});

app.post('/auth/login', async (req, res) => {
  const { username, password } = req.body;
  
  const user = Array.from(dataStore.users.values()).find(u => u.username === username);
  if (!user || !(await bcrypt.compare(password, user.password_hash))) {
    req.session.flash = { type: 'danger', message: 'Invalid username or password' };
    return res.redirect('/auth/login');
  }
  
  req.session.user = {
    id: user.id,
    username: user.username,
    email: user.email,
    isModerator: user.is_moderator,
    isAdmin: user.is_admin
  };
  
  res.redirect('/');
});

app.get('/auth/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

app.get('/tool/:id', (req, res) => {
  const tool = dataStore.tools.get(parseInt(req.params.id));
  if (!tool) {
    return res.status(404).render('error', { message: 'Tool not found' });
  }
  
  const comments = Array.from(dataStore.comments.values()).filter(c => c.tool_id === tool.id);
  const categories = Array.from(dataStore.categories.values()).filter(c => tool.category_ids.includes(c.id));
  
  res.render('tool', { tool, comments, categories, user: req.session.user });
});

app.get('/admin', requireAdmin, (req, res) => {
  const userCount = dataStore.users.size;
  const toolCount = dataStore.tools.size;
  const categoryCount = dataStore.categories.size;
  const blogPostCount = dataStore.blogPosts.size;
  
  res.render('admin/dashboard', { 
    userCount, toolCount, categoryCount, blogPostCount, 
    user: req.session.user 
  });
});

app.get('/admin/tools', requireAdmin, (req, res) => {
  const tools = Array.from(dataStore.tools.values()).map(tool => ({
    ...tool,
    author: dataStore.users.get(tool.user_id),
    categories: Array.from(dataStore.categories.values()).filter(c => tool.category_ids.includes(c.id))
  }));
  
  res.render('admin/manage_tools', { tools, user: req.session.user });
});

app.get('/admin/categories', requireAdmin, (req, res) => {
  const categories = Array.from(dataStore.categories.values());
  res.render('admin/categories', { categories, user: req.session.user });
});

app.get('/blog', (req, res) => {
  const posts = Array.from(dataStore.blogPosts.values()).map(post => ({
    ...post,
    author: dataStore.users.get(post.user_id)
  }));
  res.render('blog/index', { posts, user: req.session.user });
});

app.get('/blog/post/:id', (req, res) => {
  const post = dataStore.blogPosts.get(parseInt(req.params.id));
  if (!post) {
    return res.status(404).render('error', { message: 'Blog post not found' });
  }
  
  const author = dataStore.users.get(post.user_id);
  res.render('blog/post', { post: { ...post, author }, user: req.session.user });
});

// API routes
app.get('/api/tools', (req, res) => {
  const tools = Array.from(dataStore.tools.values())
    .filter(tool => tool.is_approved)
    .map(tool => ({
      ...tool,
      author: dataStore.users.get(tool.user_id),
      categories: Array.from(dataStore.categories.values()).filter(c => tool.category_ids.includes(c.id))
    }));
  res.json(tools);
});

app.get('/api/categories', (req, res) => {
  const categories = Array.from(dataStore.categories.values());
  res.json(categories);
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).render('error', { message: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).render('error', { message: 'Page not found' });
});

module.exports.handler = serverless(app);
 