const express = require('express');
const router = express.Router();
const { Op } = require('sequelize');
const sanitizeHtml = require('sanitize-html');
const { User, Category, Tool, Comment, ToolVote, CommentVote, AppearanceSettings } = require('../models');

// Sanitization options
const sanitizeOptions = {
  allowedTags: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre'],
  allowedAttributes: {
    'a': ['href', 'title'],
    '*': ['class']
  }
};

// Homepage
router.get('/', async (req, res) => {
  try {
    const searchQuery = req.query.search?.trim() || '';
    const categoryId = req.query.category;
    const sortBy = req.query.sort || 'votes';
    
    let whereClause = { is_approved: true };
    
    if (searchQuery) {
      whereClause = {
        ...whereClause,
        [Op.or]: [
          { name: { [Op.like]: `%${searchQuery}%` } },
          { description: { [Op.like]: `%${searchQuery}%` } }
        ]
      };
    }
    
    let includeClause = [
      {
        model: Category,
        as: 'categories',
        through: { attributes: [] }
      },
      {
        model: User,
        as: 'author',
        attributes: ['username']
      }
    ];
    
    if (categoryId) {
      includeClause[0].where = { id: categoryId };
    }
    
    let orderClause = [];
    if (sortBy === 'votes') {
      orderClause.push(['createdAt', 'DESC']); // Fallback to creation date
    } else {
      orderClause.push(['createdAt', 'DESC']);
    }
    
    const tools = await Tool.findAll({
      where: whereClause,
      include: includeClause,
      order: orderClause
    });
    
    const categories = await Category.findAll({
      order: [['name', 'ASC']]
    });
    
    res.render('index', { tools, categories, searchQuery, sortBy });
  } catch (error) {
    console.error('Error loading homepage:', error);
    res.render('index', { tools: [], categories: [], error: 'Failed to load tools' });
  }
});

// Tool detail page
router.get('/tool/:id', async (req, res) => {
  try {
    const toolId = req.params.id;
    const tool = await Tool.findByPk(toolId, {
      include: [
        {
          model: Category,
          as: 'categories',
          through: { attributes: [] }
        },
        {
          model: User,
          as: 'author',
          attributes: ['username']
        }
      ]
    });
    
    if (!tool) {
      return res.status(404).render('error', { message: 'Tool not found' });
    }
    
    if (!tool.is_approved && (!req.session.user || (req.session.user.id !== tool.user_id && !req.session.user.isModerator))) {
      return res.render('error', { message: 'This tool is not yet approved.' });
    }
    
    const comments = await Comment.findAll({
      where: { tool_id: toolId },
      include: [
        {
          model: User,
          as: 'author',
          attributes: ['username']
        }
      ],
      order: [['createdAt', 'DESC']]
    });
    
    // Get similar tools
    const similarTools = await Tool.findAll({
      include: [
        {
          model: Category,
          as: 'categories',
          where: { id: { [Op.in]: tool.categories.map(c => c.id) } },
          through: { attributes: [] }
        }
      ],
      where: {
        id: { [Op.ne]: toolId },
        is_approved: true
      },
      limit: 5,
      order: sequelize.random()
    });
    
    res.render('tool', { tool, comments, similarTools });
  } catch (error) {
    console.error('Error loading tool:', error);
    res.status(500).render('error', { message: 'Failed to load tool' });
  }
});

// Add comment
router.post('/add-comment/:toolId', requireAuth, async (req, res) => {
  try {
    const toolId = req.params.toolId;
    const content = sanitizeHtml(req.body.content || '', sanitizeOptions);
    
    if (!content.trim()) {
      req.session.flash = { type: 'danger', message: 'Comment cannot be empty' };
      return res.redirect(`/tool/${toolId}`);
    }
    
    await Comment.create({
      content,
      tool_id: toolId,
      user_id: req.session.user.id
    });
    
    req.session.flash = { type: 'success', message: 'Comment added successfully!' };
    res.redirect(`/tool/${toolId}`);
  } catch (error) {
    console.error('Error adding comment:', error);
    req.session.flash = { type: 'danger', message: 'Failed to add comment' };
    res.redirect(`/tool/${req.params.toolId}`);
  }
});

// Category page
router.get('/category/:id', async (req, res) => {
  try {
    const categoryId = req.params.id;
    const category = await Category.findByPk(categoryId);
    
    if (!category) {
      return res.status(404).render('error', { message: 'Category not found' });
    }
    
    const tools = await Tool.findAll({
      where: { is_approved: true },
      include: [
        {
          model: Category,
          as: 'categories',
          where: { id: categoryId },
          through: { attributes: [] }
        },
        {
          model: User,
          as: 'author',
          attributes: ['username']
        }
      ],
      order: [['createdAt', 'DESC']]
    });
    
    res.render('category', { category, tools });
  } catch (error) {
    console.error('Error loading category:', error);
    res.status(500).render('error', { message: 'Failed to load category' });
  }
});

// Submit tool page
router.get('/submit-tool', requireAuth, async (req, res) => {
  try {
    const categories = await Category.findAll({ order: [['name', 'ASC']] });
    res.render('submit_tool', { categories });
  } catch (error) {
    console.error('Error loading submit tool page:', error);
    res.render('error', { message: 'Failed to load submit tool page' });
  }
});

// Submit tool
router.post('/submit-tool', requireAuth, async (req, res) => {
  try {
    const { name, description, url, image_url, youtube_url, categories } = req.body;
    
    if (!name || !description || !url || !categories || categories.length === 0) {
      req.session.flash = { type: 'danger', message: 'Please fill in all required fields' };
      return res.redirect('/submit-tool');
    }
    
    const sanitizedDescription = sanitizeHtml(description, sanitizeOptions);
    
    const tool = await Tool.create({
      name,
      description: sanitizedDescription,
      url,
      image_url,
      youtube_url,
      user_id: req.session.user.id
    });
    
    // Add categories
    const categoryIds = Array.isArray(categories) ? categories : [categories];
    const categoryInstances = await Category.findAll({ where: { id: categoryIds } });
    await tool.addCategories(categoryInstances);
    
    req.session.flash = { type: 'success', message: 'Tool submitted successfully! It will be reviewed by moderators.' };
    res.redirect('/');
  } catch (error) {
    console.error('Error submitting tool:', error);
    req.session.flash = { type: 'danger', message: 'Failed to submit tool' };
    res.redirect('/submit-tool');
  }
});

// Vote on tool
router.post('/vote-tool/:toolId', requireAuth, async (req, res) => {
  try {
    const toolId = req.params.toolId;
    const value = parseInt(req.body.value); // 1 for upvote, -1 for downvote
    
    if (![-1, 1].includes(value)) {
      return res.status(400).json({ error: 'Invalid vote value' });
    }
    
    const [vote, created] = await ToolVote.findOrCreate({
      where: {
        tool_id: toolId,
        user_id: req.session.user.id
      },
      defaults: { value }
    });
    
    if (!created) {
      vote.value = value;
      await vote.save();
    }
    
    res.json({ success: true });
  } catch (error) {
    console.error('Error voting on tool:', error);
    res.status(500).json({ error: 'Failed to vote' });
  }
});

// Vote on comment
router.post('/vote-comment/:commentId', requireAuth, async (req, res) => {
  try {
    const commentId = req.params.commentId;
    const value = parseInt(req.body.value); // 1 for upvote, -1 for downvote
    
    if (![-1, 1].includes(value)) {
      return res.status(400).json({ error: 'Invalid vote value' });
    }
    
    const [vote, created] = await CommentVote.findOrCreate({
      where: {
        comment_id: commentId,
        user_id: req.session.user.id
      },
      defaults: { value }
    });
    
    if (!created) {
      vote.value = value;
      await vote.save();
    }
    
    res.json({ success: true });
  } catch (error) {
    console.error('Error voting on comment:', error);
    res.status(500).json({ error: 'Failed to vote' });
  }
});

// Static files
router.get('/ads.txt', (req, res) => {
  res.sendFile('ads.txt', { root: './static' });
});

router.get('/custom.css', async (req, res) => {
  try {
    const settings = await AppearanceSettings.getSettings();
    res.set('Content-Type', 'text/css');
    res.set('Cache-Control', 'private, max-age=0, must-revalidate');
    res.set('ETag', `"${settings.updatedAt.getTime()}"`);
    res.render('css/custom', { appearance_settings: settings });
  } catch (error) {
    console.error('Error serving custom CSS:', error);
    res.status(500).send('/* Error loading custom CSS */');
  }
});

module.exports = router; 