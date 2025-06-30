const express = require('express');
const router = express.Router();
const { BlogPost, User } = require('../models');

// Blog index
router.get('/', async (req, res) => {
  try {
    const posts = await BlogPost.findAll({
      include: [
        {
          model: User,
          as: 'author',
          attributes: ['username']
        }
      ],
      order: [['createdAt', 'DESC']]
    });
    
    res.render('blog/index', { posts });
  } catch (error) {
    console.error('Blog index error:', error);
    res.render('error', { message: 'Failed to load blog posts' });
  }
});

// Blog post detail
router.get('/post/:id', async (req, res) => {
  try {
    const post = await BlogPost.findByPk(req.params.id, {
      include: [
        {
          model: User,
          as: 'author',
          attributes: ['username']
        }
      ]
    });
    
    if (!post) {
      return res.status(404).render('error', { message: 'Blog post not found' });
    }
    
    res.render('blog/post', { post });
  } catch (error) {
    console.error('Blog post error:', error);
    res.render('error', { message: 'Failed to load blog post' });
  }
});

// Admin blog posts list
router.get('/admin', requireAdmin, async (req, res) => {
  try {
    const posts = await BlogPost.findAll({
      include: [
        {
          model: User,
          as: 'author',
          attributes: ['username']
        }
      ],
      order: [['createdAt', 'DESC']]
    });
    
    res.render('admin/blog/blog_posts', { posts });
  } catch (error) {
    console.error('Admin blog posts error:', error);
    res.render('error', { message: 'Failed to load blog posts' });
  }
});

// Create blog post form
router.get('/admin/create', requireAdmin, (req, res) => {
  res.render('admin/blog_post_form');
});

// Create blog post
router.post('/admin/create', requireAdmin, async (req, res) => {
  try {
    const { title, content, excerpt } = req.body;
    
    if (!title || !content) {
      req.session.flash = { type: 'danger', message: 'Title and content are required' };
      return res.redirect('/blog/admin/create');
    }
    
    await BlogPost.create({
      title,
      content,
      excerpt: excerpt || content.substring(0, 200) + '...',
      user_id: req.session.user.id
    });
    
    req.session.flash = { type: 'success', message: 'Blog post created successfully!' };
    res.redirect('/blog/admin');
  } catch (error) {
    console.error('Create blog post error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to create blog post' };
    res.redirect('/blog/admin/create');
  }
});

// Edit blog post form
router.get('/admin/edit/:id', requireAdmin, async (req, res) => {
  try {
    const post = await BlogPost.findByPk(req.params.id);
    
    if (!post) {
      req.session.flash = { type: 'danger', message: 'Blog post not found' };
      return res.redirect('/blog/admin');
    }
    
    res.render('admin/blog_post_form', { post });
  } catch (error) {
    console.error('Edit blog post form error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to load blog post' };
    res.redirect('/blog/admin');
  }
});

// Update blog post
router.post('/admin/edit/:id', requireAdmin, async (req, res) => {
  try {
    const post = await BlogPost.findByPk(req.params.id);
    
    if (!post) {
      req.session.flash = { type: 'danger', message: 'Blog post not found' };
      return res.redirect('/blog/admin');
    }
    
    const { title, content, excerpt } = req.body;
    
    if (!title || !content) {
      req.session.flash = { type: 'danger', message: 'Title and content are required' };
      return res.redirect(`/blog/admin/edit/${req.params.id}`);
    }
    
    post.title = title;
    post.content = content;
    post.excerpt = excerpt || content.substring(0, 200) + '...';
    await post.save();
    
    req.session.flash = { type: 'success', message: 'Blog post updated successfully!' };
    res.redirect('/blog/admin');
  } catch (error) {
    console.error('Update blog post error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to update blog post' };
    res.redirect(`/blog/admin/edit/${req.params.id}`);
  }
});

// Delete blog post
router.post('/admin/delete/:id', requireAdmin, async (req, res) => {
  try {
    const post = await BlogPost.findByPk(req.params.id);
    
    if (!post) {
      req.session.flash = { type: 'danger', message: 'Blog post not found' };
      return res.redirect('/blog/admin');
    }
    
    await post.destroy();
    
    req.session.flash = { type: 'success', message: 'Blog post deleted successfully!' };
    res.redirect('/blog/admin');
  } catch (error) {
    console.error('Delete blog post error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to delete blog post' };
    res.redirect('/blog/admin');
  }
});

module.exports = router; 