const express = require('express');
const session = require('express-session');
const path = require('path');
const pgSession = require('connect-pg-simple')(session);
const expressLayouts = require('express-ejs-layouts');
const cookieParser = require('cookie-parser');
const { pool } = require('./db/connection');
const { router: authRouter } = require('./routes/auth');

const app = express();

// View engine setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(expressLayouts);
app.set('layout', 'layout'); // This tells Express to use views/layout.ejs as the default layout

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(cookieParser());

// Session configuration
app.use(session({
    store: new pgSession({
        pool,
        tableName: 'session'
    }),
    secret: process.env.SESSION_SECRET || 'your_session_secret',
    resave: false,
    saveUninitialized: false,
    cookie: {
        maxAge: 30 * 24 * 60 * 60 * 1000 // 30 days
    }
}));

// Flash messages middleware
app.use((req, res, next) => {
    res.locals.messages = req.session.messages || [];
    res.locals.user = req.user || null;
    delete req.session.messages;
    next();
});

// Routes
app.use(authRouter); //This line is added from edited code.

app.get('/', (req, res) => {
    res.render('index', {
        title: 'AI Tools Directory',
        tools: [] // We'll populate this later
    });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on port ${PORT}`);
});