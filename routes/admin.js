const express = require('express');
const router = express.Router();
const { User, Category, Tool, BlogPost, AppearanceSettings } = require('../models');

// Admin dashboard
router.get('/', requireAdmin, async (req, res) => {
  try {
    const userCount = await User.count();
    const toolCount = await Tool.count();
    const categoryCount = await Category.count();
    const blogPostCount = await BlogPost.count();
    
    res.render('admin/dashboard', {
      userCount,
      toolCount,
      categoryCount,
      blogPostCount
    });
  } catch (error) {
    console.error('Admin dashboard error:', error);
    res.render('error', { message: 'Failed to load admin dashboard' });
  }
});

// Manage users
router.get('/users', requireAdmin, async (req, res) => {
  try {
    const users = await User.findAll({
      order: [['createdAt', 'DESC']]
    });
    res.render('admin/manage_users', { users });
  } catch (error) {
    console.error('Manage users error:', error);
    res.render('error', { message: 'Failed to load users' });
  }
});

// Manage tools
router.get('/tools', requireModerator, async (req, res) => {
  try {
    const tools = await Tool.findAll({
      include: [
        {
          model: User,
          as: 'author',
          attributes: ['username']
        },
        {
          model: Category,
          as: 'categories',
          through: { attributes: [] }
        }
      ],
      order: [['createdAt', 'DESC']]
    });
    res.render('admin/manage_tools', { tools });
  } catch (error) {
    console.error('Manage tools error:', error);
    res.render('error', { message: 'Failed to load tools' });
  }
});

// Moderate tools
router.get('/moderate-tools', requireModerator, async (req, res) => {
  try {
    const tools = await Tool.findAll({
      where: { is_approved: false },
      include: [
        {
          model: User,
          as: 'author',
          attributes: ['username']
        },
        {
          model: Category,
          as: 'categories',
          through: { attributes: [] }
        }
      ],
      order: [['createdAt', 'DESC']]
    });
    res.render('admin/moderate_tools', { tools });
  } catch (error) {
    console.error('Moderate tools error:', error);
    res.render('error', { message: 'Failed to load tools for moderation' });
  }
});

// Approve tool
router.post('/approve-tool/:id', requireModerator, async (req, res) => {
  try {
    const tool = await Tool.findByPk(req.params.id);
    if (!tool) {
      req.session.flash = { type: 'danger', message: 'Tool not found' };
      return res.redirect('/admin/moderate-tools');
    }
    
    tool.is_approved = true;
    await tool.save();
    
    req.session.flash = { type: 'success', message: 'Tool approved successfully!' };
    res.redirect('/admin/moderate-tools');
  } catch (error) {
    console.error('Approve tool error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to approve tool' };
    res.redirect('/admin/moderate-tools');
  }
});

// Reject tool
router.post('/reject-tool/:id', requireModerator, async (req, res) => {
  try {
    const tool = await Tool.findByPk(req.params.id);
    if (!tool) {
      req.session.flash = { type: 'danger', message: 'Tool not found' };
      return res.redirect('/admin/moderate-tools');
    }
    
    await tool.destroy();
    
    req.session.flash = { type: 'success', message: 'Tool rejected and removed successfully!' };
    res.redirect('/admin/moderate-tools');
  } catch (error) {
    console.error('Reject tool error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to reject tool' };
    res.redirect('/admin/moderate-tools');
  }
});

// Manage categories
router.get('/categories', requireAdmin, async (req, res) => {
  try {
    const categories = await Category.findAll({
      order: [['name', 'ASC']]
    });
    res.render('admin/categories', { categories });
  } catch (error) {
    console.error('Manage categories error:', error);
    res.render('error', { message: 'Failed to load categories' });
  }
});

// Add category
router.post('/categories', requireAdmin, async (req, res) => {
  try {
    const { name, description } = req.body;
    
    if (!name) {
      req.session.flash = { type: 'danger', message: 'Category name is required' };
      return res.redirect('/admin/categories');
    }
    
    await Category.create({ name, description });
    
    req.session.flash = { type: 'success', message: 'Category added successfully!' };
    res.redirect('/admin/categories');
  } catch (error) {
    console.error('Add category error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to add category' };
    res.redirect('/admin/categories');
  }
});

// Delete category
router.post('/delete-category/:id', requireAdmin, async (req, res) => {
  try {
    const category = await Category.findByPk(req.params.id);
    if (!category) {
      req.session.flash = { type: 'danger', message: 'Category not found' };
      return res.redirect('/admin/categories');
    }
    
    await category.destroy();
    
    req.session.flash = { type: 'success', message: 'Category deleted successfully!' };
    res.redirect('/admin/categories');
  } catch (error) {
    console.error('Delete category error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to delete category' };
    res.redirect('/admin/categories');
  }
});

// Appearance settings
router.get('/appearance', requireAdmin, async (req, res) => {
  try {
    const settings = await AppearanceSettings.getSettings();
    res.render('admin/appearance', { settings });
  } catch (error) {
    console.error('Appearance settings error:', error);
    res.render('error', { message: 'Failed to load appearance settings' });
  }
});

// Update appearance settings
router.post('/appearance', requireAdmin, async (req, res) => {
  try {
    const settings = await AppearanceSettings.getSettings();
    
    // Update all settings from request body
    Object.keys(req.body).forEach(key => {
      if (settings.hasOwnProperty(key)) {
        settings[key] = req.body[key];
      }
    });
    
    await settings.save();
    
    req.session.flash = { type: 'success', message: 'Appearance settings updated successfully!' };
    res.redirect('/admin/appearance');
  } catch (error) {
    console.error('Update appearance settings error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to update appearance settings' };
    res.redirect('/admin/appearance');
  }
});

module.exports = router; 