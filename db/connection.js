const { Pool } = require('pg');
const { drizzle } = require('drizzle-orm/node-postgres');

// Create a new pool using the DATABASE_URL environment variable
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: false
});

// Create a drizzle instance
const db = drizzle(pool);

module.exports = {
    pool,
    db
};
