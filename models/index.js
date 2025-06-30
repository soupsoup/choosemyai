const { Sequelize, DataTypes } = require('sequelize');
const bcrypt = require('bcryptjs');
const path = require('path');
const fs = require('fs');

// Import memory store for serverless environments
const memoryStore = require('./memory-store');

// Database configuration for serverless compatibility
let sequelize;
let useMemoryStore = false;

if (process.env.NODE_ENV === 'production' || process.env.NETLIFY) {
  // For serverless environments, use memory store
  useMemoryStore = true;
  // Create a dummy sequelize instance for compatibility
  sequelize = {
    sync: async () => Promise.resolve(),
    close: async () => Promise.resolve()
  };
} else {
  // For development, use file-based database
  const dbPath = path.join(__dirname, '../database.sqlite');
  sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: dbPath,
    logging: false,
    dialectOptions: {
      timeout: 30000
    }
  });
}

// User model
class User {
  static async findOne(where) {
    if (useMemoryStore) {
      return memoryStore.findUser(where);
    }
    return sequelize.models.User.findOne({ where });
  }

  static async findByPk(id) {
    if (useMemoryStore) {
      return memoryStore.findUser({ id });
    }
    return sequelize.models.User.findByPk(id);
  }

  static async create(userData) {
    if (useMemoryStore) {
      if (userData.password_hash) {
        userData.password_hash = await bcrypt.hash(userData.password_hash, 10);
      }
      return memoryStore.createUser(userData);
    }
    return sequelize.models.User.create(userData);
  }

  static async count() {
    if (useMemoryStore) {
      return memoryStore.countUsers();
    }
    return sequelize.models.User.count();
  }

  async checkPassword(password) {
    if (useMemoryStore) {
      return bcrypt.compare(password, this.password_hash);
    }
    return bcrypt.compare(password, this.password_hash);
  }

  async setPassword(password) {
    this.password_hash = await bcrypt.hash(password, 10);
    if (!useMemoryStore) {
      await this.save();
    }
  }

  async save() {
    if (!useMemoryStore) {
      return sequelize.models.User.prototype.save.call(this);
    }
    // For memory store, data is already saved
    return this;
  }
}

// Create Sequelize model for development
if (!useMemoryStore) {
  sequelize.define('User', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    username: {
      type: DataTypes.STRING(80),
      unique: true,
      allowNull: false
    },
    email: {
      type: DataTypes.STRING(120),
      unique: true,
      allowNull: false
    },
    password_hash: {
      type: DataTypes.STRING(256),
      allowNull: false
    },
    is_moderator: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    },
    is_admin: {
      type: DataTypes.BOOLEAN,
      defaultValue: false
    }
  }, {
    hooks: {
      beforeCreate: async (user) => {
        if (user.password_hash) {
          user.password_hash = await bcrypt.hash(user.password_hash, 10);
        }
      }
    }
  });
}

// Category model
const Category = sequelize.define('Category', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING(100),
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT
  }
});

// Tool model
const Tool = sequelize.define('Tool', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING(200),
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: false
  },
  url: {
    type: DataTypes.STRING(500),
    allowNull: false
  },
  image_url: {
    type: DataTypes.STRING(500)
  },
  youtube_url: {
    type: DataTypes.STRING(500)
  },
  is_approved: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  resources: {
    type: DataTypes.TEXT // Store as JSON string
  }
});

// Comment model
const Comment = sequelize.define('Comment', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  content: {
    type: DataTypes.TEXT,
    allowNull: false
  }
});

// BlogPost model
const BlogPost = sequelize.define('BlogPost', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  title: {
    type: DataTypes.STRING(200),
    allowNull: false
  },
  slug: {
    type: DataTypes.STRING(200),
    unique: true,
    allowNull: false
  },
  content: {
    type: DataTypes.TEXT,
    allowNull: false
  },
  published: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  featured_image: {
    type: DataTypes.STRING(500)
  },
  excerpt: {
    type: DataTypes.TEXT
  }
});

// ToolVote model
const ToolVote = sequelize.define('ToolVote', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  value: {
    type: DataTypes.INTEGER,
    allowNull: false // 1 for upvote, -1 for downvote
  }
});

// CommentVote model
const CommentVote = sequelize.define('CommentVote', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  value: {
    type: DataTypes.INTEGER,
    allowNull: false // 1 for upvote, -1 for downvote
  }
});

// AppearanceSettings model
const AppearanceSettings = sequelize.define('AppearanceSettings', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  primary_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#0d6efd'
  },
  secondary_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#6c757d'
  },
  background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#212529'
  },
  font_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  font_family: {
    type: DataTypes.TEXT,
    defaultValue: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif'
  },
  header_background: {
    type: DataTypes.STRING(7),
    defaultValue: '#212529'
  },
  secondary_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#6c757d'
  },
  button_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#0d6efd'
  },
  button_hover_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#0b5ed7'
  },
  button_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  button_hover_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  link_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#0d6efd'
  },
  link_hover_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#0a58ca'
  },
  nav_link_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  nav_link_hover_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#e9ecef'
  },
  container_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#2c3034'
  },
  container_border_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#373b3e'
  },
  container_header_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  search_box_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#2c3034'
  },
  search_box_border_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#373b3e'
  },
  category_item_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#2c3034'
  },
  category_item_hover_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#373b3e'
  },
  category_item_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  category_item_hover_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  comment_box_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#2c3034'
  },
  comment_box_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  main_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  card_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  footer_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#6c757d'
  },
  blog_meta_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#6c757d'
  },
  list_item_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#2c3034'
  },
  list_item_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  },
  list_item_hover_background_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#373b3e'
  },
  list_item_hover_text_color: {
    type: DataTypes.STRING(7),
    defaultValue: '#ffffff'
  }
});

// Define associations
User.hasMany(Tool, { foreignKey: 'user_id', as: 'tools' });
Tool.belongsTo(User, { foreignKey: 'user_id', as: 'author' });

User.hasMany(Comment, { foreignKey: 'user_id', as: 'comments' });
Comment.belongsTo(User, { foreignKey: 'user_id', as: 'author' });

User.hasMany(BlogPost, { foreignKey: 'user_id', as: 'blog_posts' });
BlogPost.belongsTo(User, { foreignKey: 'user_id', as: 'author' });

Tool.hasMany(Comment, { foreignKey: 'tool_id', as: 'comments' });
Comment.belongsTo(Tool, { foreignKey: 'tool_id', as: 'tool' });

Tool.hasMany(ToolVote, { foreignKey: 'tool_id', as: 'votes' });
ToolVote.belongsTo(Tool, { foreignKey: 'tool_id', as: 'tool' });

Comment.hasMany(CommentVote, { foreignKey: 'comment_id', as: 'votes' });
CommentVote.belongsTo(Comment, { foreignKey: 'comment_id', as: 'comment' });

User.hasMany(ToolVote, { foreignKey: 'user_id', as: 'tool_votes' });
ToolVote.belongsTo(User, { foreignKey: 'user_id', as: 'user' });

User.hasMany(CommentVote, { foreignKey: 'user_id', as: 'comment_votes' });
CommentVote.belongsTo(User, { foreignKey: 'user_id', as: 'user' });

// Many-to-many relationship between Tool and Category
Tool.belongsToMany(Category, { through: 'tool_categories', as: 'categories' });
Category.belongsToMany(Tool, { through: 'tool_categories', as: 'tools' });

// Instance methods
User.prototype.checkPassword = async function(password) {
  return bcrypt.compare(password, this.password_hash);
};

User.prototype.setPassword = async function(password) {
  this.password_hash = await bcrypt.hash(password, 10);
};

// Static methods
AppearanceSettings.getSettings = async function() {
  let settings = await this.findOne();
  if (!settings) {
    settings = await this.create({});
  }
  return settings;
};

module.exports = {
  sequelize,
  User,
  Category,
  Tool,
  Comment,
  BlogPost,
  ToolVote,
  CommentVote,
  AppearanceSettings
}; 