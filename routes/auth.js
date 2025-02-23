const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { db } = require('../db/connection');
const { users } = require('../db/schema');
const { eq } = require('drizzle-orm');

const router = express.Router();

// Middleware to check if user is authenticated
const isAuthenticated = (req, res, next) => {
  const token = req.cookies.token;
  if (!token) {
    return res.redirect('/login');
  }

  try {
    const decoded = jwt.verify(token, process.env.SESSION_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.clearCookie('token');
    return res.redirect('/login');
  }
};

// Login route
router.get('/login', (req, res) => {
  res.render('auth/login', { messages: [] });
});

router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  try {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    
    if (!user || !await bcrypt.compare(password, user.passwordHash)) {
      req.session.messages = [{ type: 'danger', text: 'Invalid username or password' }];
      return res.redirect('/login');
    }

    const token = jwt.sign(
      { id: user.id, username: user.username, isAdmin: user.isAdmin },
      process.env.SESSION_SECRET,
      { expiresIn: '30d' }
    );

    res.cookie('token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 30 * 24 * 60 * 60 * 1000 // 30 days
    });

    req.session.messages = [{ type: 'success', text: 'Successfully logged in!' }];
    res.redirect('/');
  } catch (err) {
    console.error('Login error:', err);
    req.session.messages = [{ type: 'danger', text: 'An error occurred during login' }];
    res.redirect('/login');
  }
});

// Register route
router.get('/register', (req, res) => {
  res.render('auth/register', { messages: [] });
});

router.post('/register', async (req, res) => {
  const { username, email, password } = req.body;

  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    
    await db.insert(users).values({
      username,
      email,
      passwordHash: hashedPassword,
      isAdmin: false,
      isModerator: false
    });

    req.session.messages = [{ type: 'success', text: 'Registration successful! Please login.' }];
    res.redirect('/login');
  } catch (err) {
    console.error('Registration error:', err);
    req.session.messages = [{ type: 'danger', text: 'Username or email already exists' }];
    res.redirect('/register');
  }
});

// Logout route
router.get('/logout', (req, res) => {
  res.clearCookie('token');
  req.session.destroy();
  res.redirect('/');
});

module.exports = { router, isAuthenticated };
