const { pgTable, serial, text, timestamp, boolean, integer } = require('drizzle-orm/pg-core');

// Users table
const users = pgTable('user', {
    id: serial('id').primaryKey(),
    username: text('username').notNull().unique(),
    email: text('email').notNull().unique(),
    passwordHash: text('password_hash').notNull(),
    isAdmin: boolean('is_admin').default(false),
    isModerator: boolean('is_moderator').default(false),
    createdAt: timestamp('created_at').defaultNow()
});

// Categories table
const categories = pgTable('category', {
    id: serial('id').primaryKey(),
    name: text('name').notNull().unique(),
    description: text('description')
});

// Tools table
const tools = pgTable('tool', {
    id: serial('id').primaryKey(),
    name: text('name').notNull(),
    description: text('description').notNull(),
    url: text('url').notNull(),
    imageUrl: text('image_url'),
    youtubeUrl: text('youtube_url'),
    userId: integer('user_id').references(() => users.id),
    isApproved: boolean('is_approved').default(false),
    createdAt: timestamp('created_at').defaultNow(),
    resources: text('resources') // JSON string
});

module.exports = {
    users,
    categories,
    tools
};
