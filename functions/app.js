const express = require('express');
const serverless = require('serverless-http');
const session = require('express-session');
const bcrypt = require('bcryptjs');
const sanitizeHtml = require('sanitize-html');
const path = require('path');
const db = require('../utils/database');

const app = express();

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
app.get('/', async (req, res) => {
  try {
    const tools = await db.getAllTools({ is_approved: true });
    const categories = await db.getAllCategories();
    res.render('index', { tools, categories, user: req.session.user });
  } catch (error) {
    console.error('Error loading homepage:', error);
    res.render('index', { tools: [], categories: [], user: req.session.user, error: 'Failed to load tools' });
  }
});

app.get('/auth/login', (req, res) => {
  res.render('auth/login', { user: req.session.user });
});

app.post('/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    const user = await db.findUser({ username });
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
  } catch (error) {
    console.error('Login error:', error);
    req.session.flash = { type: 'danger', message: 'Login failed' };
    res.redirect('/auth/login');
  }
});

app.get('/auth/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

app.get('/tool/:id', async (req, res) => {
  try {
    const tool = await db.findTool(parseInt(req.params.id));
    if (!tool) {
      return res.status(404).render('error', { message: 'Tool not found' });
    }
    
    const comments = await db.getComments({ tool_id: tool.id });
    
    res.render('tool', { tool, comments, user: req.session.user });
  } catch (error) {
    console.error('Error loading tool:', error);
    res.status(500).render('error', { message: 'Failed to load tool' });
  }
});

app.get('/admin', requireAdmin, async (req, res) => {
  try {
    const userCount = await db.countUsers();
    const toolCount = await db.countTools();
    const categoryCount = await db.countCategories();
    const blogPostCount = await db.countBlogPosts();
    
    res.render('admin/dashboard', { 
      userCount, toolCount, categoryCount, blogPostCount, 
      user: req.session.user 
    });
  } catch (error) {
    console.error('Admin dashboard error:', error);
    res.render('error', { message: 'Failed to load admin dashboard' });
  }
});

app.get('/admin/tools', requireAdmin, async (req, res) => {
  try {
    const tools = await db.getAllTools();
    res.render('admin/manage_tools', { tools, user: req.session.user });
  } catch (error) {
    console.error('Manage tools error:', error);
    res.render('error', { message: 'Failed to load tools' });
  }
});

app.get('/admin/categories', requireAdmin, async (req, res) => {
  try {
    const categories = await db.getAllCategories();
    res.render('admin/categories', { categories, user: req.session.user });
  } catch (error) {
    console.error('Manage categories error:', error);
    res.render('error', { message: 'Failed to load categories' });
  }
});

app.post('/admin/categories', requireAdmin, async (req, res) => {
  try {
    const { name, description } = req.body;
    
    if (!name) {
      req.session.flash = { type: 'danger', message: 'Category name is required' };
      return res.redirect('/admin/categories');
    }
    
    await db.createCategory({ name, description });
    
    req.session.flash = { type: 'success', message: 'Category added successfully!' };
    res.redirect('/admin/categories');
  } catch (error) {
    console.error('Add category error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to add category' };
    res.redirect('/admin/categories');
  }
});

app.post('/admin/delete-category/:id', requireAdmin, async (req, res) => {
  try {
    await db.deleteCategory(parseInt(req.params.id));
    
    req.session.flash = { type: 'success', message: 'Category deleted successfully!' };
    res.redirect('/admin/categories');
  } catch (error) {
    console.error('Delete category error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to delete category' };
    res.redirect('/admin/categories');
  }
});

app.get('/blog', async (req, res) => {
  try {
    const posts = await db.getAllBlogPosts();
    res.render('blog/index', { posts, user: req.session.user });
  } catch (error) {
    console.error('Blog index error:', error);
    res.render('error', { message: 'Failed to load blog posts' });
  }
});

app.get('/blog/post/:id', async (req, res) => {
  try {
    const post = await db.findBlogPost(parseInt(req.params.id));
    if (!post) {
      return res.status(404).render('error', { message: 'Blog post not found' });
    }
    
    res.render('blog/post', { post, user: req.session.user });
  } catch (error) {
    console.error('Blog post error:', error);
    res.render('error', { message: 'Failed to load blog post' });
  }
});

// API routes
app.get('/api/tools', async (req, res) => {
  try {
    const tools = await db.getAllTools({ is_approved: true });
    res.json(tools);
  } catch (error) {
    console.error('API tools error:', error);
    res.status(500).json({ error: 'Failed to fetch tools' });
  }
});

app.get('/api/categories', async (req, res) => {
  try {
    const categories = await db.getAllCategories();
    res.json(categories);
  } catch (error) {
    console.error('API categories error:', error);
    res.status(500).json({ error: 'Failed to fetch categories' });
  }
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
 