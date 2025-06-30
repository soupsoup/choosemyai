const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const { User } = require('../models');

// Login page
router.get('/login', (req, res) => {
  res.render('auth/login');
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    const user = await User.findOne({ where: { username } });
    if (!user || !(await user.checkPassword(password))) {
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
    
    const returnTo = req.session.returnTo || '/';
    delete req.session.returnTo;
    res.redirect(returnTo);
  } catch (error) {
    console.error('Login error:', error);
    req.session.flash = { type: 'danger', message: 'Login failed' };
    res.redirect('/auth/login');
  }
});

// Register page
router.get('/register', (req, res) => {
  res.render('auth/register');
});

// Register
router.post('/register', async (req, res) => {
  try {
    const { username, email, password, confirm_password } = req.body;
    
    if (password !== confirm_password) {
      req.session.flash = { type: 'danger', message: 'Passwords do not match' };
      return res.redirect('/auth/register');
    }
    
    const existingUser = await User.findOne({
      where: {
        [require('sequelize').Op.or]: [{ username }, { email }]
      }
    });
    
    if (existingUser) {
      req.session.flash = { type: 'danger', message: 'Username or email already exists' };
      return res.redirect('/auth/register');
    }
    
    const user = await User.create({
      username,
      email,
      password_hash: password
    });
    
    req.session.flash = { type: 'success', message: 'Registration successful! Please log in.' };
    res.redirect('/auth/login');
  } catch (error) {
    console.error('Registration error:', error);
    req.session.flash = { type: 'danger', message: 'Registration failed' };
    res.redirect('/auth/register');
  }
});

// Logout
router.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

// Change password page
router.get('/change-password', (req, res) => {
  if (!req.session.user) {
    return res.redirect('/auth/login');
  }
  res.render('auth/change_password');
});

// Change password
router.post('/change-password', async (req, res) => {
  try {
    if (!req.session.user) {
      return res.redirect('/auth/login');
    }
    
    const { current_password, new_password, confirm_password } = req.body;
    
    if (new_password !== confirm_password) {
      req.session.flash = { type: 'danger', message: 'New passwords do not match' };
      return res.redirect('/auth/change-password');
    }
    
    const user = await User.findByPk(req.session.user.id);
    if (!user || !(await user.checkPassword(current_password))) {
      req.session.flash = { type: 'danger', message: 'Current password is incorrect' };
      return res.redirect('/auth/change-password');
    }
    
    await user.setPassword(new_password);
    await user.save();
    
    req.session.flash = { type: 'success', message: 'Password changed successfully!' };
    res.redirect('/');
  } catch (error) {
    console.error('Change password error:', error);
    req.session.flash = { type: 'danger', message: 'Failed to change password' };
    res.redirect('/auth/change-password');
  }
});

module.exports = router; 