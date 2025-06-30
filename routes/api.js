const express = require('express');
const router = express.Router();
const { Tool, Category, User, Comment, ToolVote, CommentVote } = require('../models');
const { Op } = require('sequelize');

// Get all tools
router.get('/tools', async (req, res) => {
  try {
    const tools = await Tool.findAll({
      where: { is_approved: true },
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
      ],
      order: [['createdAt', 'DESC']]
    });
    
    res.json(tools);
  } catch (error) {
    console.error('API tools error:', error);
    res.status(500).json({ error: 'Failed to fetch tools' });
  }
});

// Get tool by ID
router.get('/tools/:id', async (req, res) => {
  try {
    const tool = await Tool.findByPk(req.params.id, {
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
        },
        {
          model: Comment,
          as: 'comments',
          include: [
            {
              model: User,
              as: 'author',
              attributes: ['username']
            }
          ],
          order: [['createdAt', 'DESC']]
        }
      ]
    });
    
    if (!tool) {
      return res.status(404).json({ error: 'Tool not found' });
    }
    
    res.json(tool);
  } catch (error) {
    console.error('API tool error:', error);
    res.status(500).json({ error: 'Failed to fetch tool' });
  }
});

// Search tools
router.get('/search', async (req, res) => {
  try {
    const { q, category } = req.query;
    
    let whereClause = { is_approved: true };
    
    if (q) {
      whereClause = {
        ...whereClause,
        [Op.or]: [
          { name: { [Op.like]: `%${q}%` } },
          { description: { [Op.like]: `%${q}%` } }
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
    
    if (category) {
      includeClause[0].where = { id: category };
    }
    
    const tools = await Tool.findAll({
      where: whereClause,
      include: includeClause,
      order: [['createdAt', 'DESC']]
    });
    
    res.json(tools);
  } catch (error) {
    console.error('API search error:', error);
    res.status(500).json({ error: 'Failed to search tools' });
  }
});

// Get categories
router.get('/categories', async (req, res) => {
  try {
    const categories = await Category.findAll({
      order: [['name', 'ASC']]
    });
    res.json(categories);
  } catch (error) {
    console.error('API categories error:', error);
    res.status(500).json({ error: 'Failed to fetch categories' });
  }
});

// Vote on tool
router.post('/vote-tool/:toolId', async (req, res) => {
  try {
    if (!req.session.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
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
    console.error('API vote tool error:', error);
    res.status(500).json({ error: 'Failed to vote' });
  }
});

// Vote on comment
router.post('/vote-comment/:commentId', async (req, res) => {
  try {
    if (!req.session.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
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
    console.error('API vote comment error:', error);
    res.status(500).json({ error: 'Failed to vote' });
  }
});

// Add comment
router.post('/comment/:toolId', async (req, res) => {
  try {
    if (!req.session.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    const toolId = req.params.toolId;
    const content = req.body.content;
    
    if (!content || !content.trim()) {
      return res.status(400).json({ error: 'Comment content is required' });
    }
    
    const comment = await Comment.create({
      content: content.trim(),
      tool_id: toolId,
      user_id: req.session.user.id
    });
    
    const commentWithAuthor = await Comment.findByPk(comment.id, {
      include: [
        {
          model: User,
          as: 'author',
          attributes: ['username']
        }
      ]
    });
    
    res.json(commentWithAuthor);
  } catch (error) {
    console.error('API add comment error:', error);
    res.status(500).json({ error: 'Failed to add comment' });
  }
});

// Get user profile
router.get('/user/profile', async (req, res) => {
  try {
    if (!req.session.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    const user = await User.findByPk(req.session.user.id, {
      attributes: { exclude: ['password_hash'] }
    });
    
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    res.json(user);
  } catch (error) {
    console.error('API user profile error:', error);
    res.status(500).json({ error: 'Failed to fetch user profile' });
  }
});

// Get user's tools
router.get('/user/tools', async (req, res) => {
  try {
    if (!req.session.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    const tools = await Tool.findAll({
      where: { user_id: req.session.user.id },
      include: [
        {
          model: Category,
          as: 'categories',
          through: { attributes: [] }
        }
      ],
      order: [['createdAt', 'DESC']]
    });
    
    res.json(tools);
  } catch (error) {
    console.error('API user tools error:', error);
    res.status(500).json({ error: 'Failed to fetch user tools' });
  }
});

module.exports = router; 