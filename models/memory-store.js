// Simple in-memory data store for serverless environments
class MemoryStore {
  constructor() {
    this.users = new Map();
    this.categories = new Map();
    this.tools = new Map();
    this.comments = new Map();
    this.blogPosts = new Map();
    this.toolVotes = new Map();
    this.commentVotes = new Map();
    this.appearanceSettings = new Map();
    this.nextId = {
      users: 1,
      categories: 1,
      tools: 1,
      comments: 1,
      blogPosts: 1,
      toolVotes: 1,
      commentVotes: 1,
      appearanceSettings: 1
    };
    
    this.seedData();
  }

  seedData() {
    // Create admin user
    const adminUser = this.createUser({
      username: 'admin',
      email: 'admin@choosemyai.com',
      password_hash: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // admin123
      is_admin: true,
      is_moderator: true
    });

    // Create categories
    const categories = [
      { name: 'AI Writing', description: 'AI-powered writing and content creation tools' },
      { name: 'AI Image Generation', description: 'Tools for creating images with AI' },
      { name: 'AI Video', description: 'AI video creation and editing tools' },
      { name: 'AI Chatbots', description: 'Chatbot and conversational AI tools' },
      { name: 'AI Research', description: 'Research and analysis AI tools' },
      { name: 'AI Productivity', description: 'Productivity and workflow AI tools' },
      { name: 'AI Development', description: 'AI tools for developers' },
      { name: 'AI Business', description: 'Business and marketing AI tools' }
    ].map(cat => this.createCategory(cat));

    // Create sample tools
    const sampleTools = [
      {
        name: 'ChatGPT',
        description: 'Advanced language model for conversation and text generation',
        url: 'https://chat.openai.com',
        image_url: 'https://via.placeholder.com/300x200?text=ChatGPT',
        user_id: adminUser.id,
        is_approved: true,
        category_ids: [categories[0].id, categories[4].id] // AI Writing, AI Research
      },
      {
        name: 'Midjourney',
        description: 'AI art generation tool for creating stunning images',
        url: 'https://midjourney.com',
        image_url: 'https://via.placeholder.com/300x200?text=Midjourney',
        user_id: adminUser.id,
        is_approved: true,
        category_ids: [categories[1].id] // AI Image Generation
      },
      {
        name: 'GitHub Copilot',
        description: 'AI-powered code completion and generation tool',
        url: 'https://github.com/features/copilot',
        image_url: 'https://via.placeholder.com/300x200?text=GitHub+Copilot',
        user_id: adminUser.id,
        is_approved: true,
        category_ids: [categories[6].id] // AI Development
      }
    ].map(tool => this.createTool(tool));

    // Create sample blog post
    this.createBlogPost({
      title: 'Welcome to ChooseMyAI',
      slug: 'welcome-to-choosemyai',
      content: `
        <h1>Welcome to ChooseMyAI!</h1>
        <p>This is your comprehensive directory of AI tools and resources. Here you can discover, rate, and review the best AI tools available today.</p>
        <h2>Getting Started</h2>
        <ul>
          <li>Browse tools by category</li>
          <li>Search for specific tools</li>
          <li>Submit your own AI tools</li>
          <li>Rate and comment on tools</li>
        </ul>
        <p>Happy exploring!</p>
      `,
      published: true,
      user_id: adminUser.id,
      excerpt: 'Welcome to your comprehensive directory of AI tools and resources.'
    });

    // Create default appearance settings
    this.createAppearanceSettings({
      primary_color: '#0d6efd',
      secondary_color: '#6c757d',
      background_color: '#212529',
      font_color: '#ffffff',
      font_family: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif',
      header_background: '#0d6efd',
      footer_background: '#6c757d'
    });
  }

  // User methods
  createUser(userData) {
    const user = {
      id: this.nextId.users++,
      ...userData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.users.set(user.id, user);
    return user;
  }

  findUser(where) {
    for (const user of this.users.values()) {
      if (where.id && user.id === where.id) return user;
      if (where.username && user.username === where.username) return user;
      if (where.email && user.email === where.email) return user;
    }
    return null;
  }

  findAllUsers() {
    return Array.from(this.users.values());
  }

  // Category methods
  createCategory(categoryData) {
    const category = {
      id: this.nextId.categories++,
      ...categoryData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.categories.set(category.id, category);
    return category;
  }

  findCategory(id) {
    return this.categories.get(id);
  }

  findAllCategories() {
    return Array.from(this.categories.values());
  }

  // Tool methods
  createTool(toolData) {
    const tool = {
      id: this.nextId.tools++,
      ...toolData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.tools.set(tool.id, tool);
    return tool;
  }

  findTool(id) {
    return this.tools.get(id);
  }

  findAllTools(where = {}) {
    let tools = Array.from(this.tools.values());
    
    if (where.is_approved !== undefined) {
      tools = tools.filter(tool => tool.is_approved === where.is_approved);
    }
    
    if (where.user_id) {
      tools = tools.filter(tool => tool.user_id === where.user_id);
    }
    
    return tools;
  }

  // Comment methods
  createComment(commentData) {
    const comment = {
      id: this.nextId.comments++,
      ...commentData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.comments.set(comment.id, comment);
    return comment;
  }

  findComments(where) {
    return Array.from(this.comments.values()).filter(comment => {
      if (where.tool_id) return comment.tool_id === where.tool_id;
      return true;
    });
  }

  // Blog post methods
  createBlogPost(postData) {
    const post = {
      id: this.nextId.blogPosts++,
      ...postData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.blogPosts.set(post.id, post);
    return post;
  }

  findBlogPost(id) {
    return this.blogPosts.get(id);
  }

  findAllBlogPosts() {
    return Array.from(this.blogPosts.values());
  }

  // Vote methods
  createToolVote(voteData) {
    const vote = {
      id: this.nextId.toolVotes++,
      ...voteData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.toolVotes.set(vote.id, vote);
    return vote;
  }

  findToolVote(where) {
    for (const vote of this.toolVotes.values()) {
      if (vote.tool_id === where.tool_id && vote.user_id === where.user_id) {
        return vote;
      }
    }
    return null;
  }

  createCommentVote(voteData) {
    const vote = {
      id: this.nextId.commentVotes++,
      ...voteData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.commentVotes.set(vote.id, vote);
    return vote;
  }

  findCommentVote(where) {
    for (const vote of this.commentVotes.values()) {
      if (vote.comment_id === where.comment_id && vote.user_id === where.user_id) {
        return vote;
      }
    }
    return null;
  }

  // Appearance settings methods
  createAppearanceSettings(settingsData) {
    const settings = {
      id: this.nextId.appearanceSettings++,
      ...settingsData,
      created_at: new Date(),
      updated_at: new Date()
    };
    this.appearanceSettings.set(settings.id, settings);
    return settings;
  }

  getAppearanceSettings() {
    const settings = Array.from(this.appearanceSettings.values())[0];
    if (!settings) {
      return this.createAppearanceSettings({
        primary_color: '#0d6efd',
        secondary_color: '#6c757d',
        background_color: '#212529',
        font_color: '#ffffff',
        font_family: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif',
        header_background: '#0d6efd',
        footer_background: '#6c757d'
      });
    }
    return settings;
  }

  updateAppearanceSettings(settingsData) {
    const settings = this.getAppearanceSettings();
    Object.assign(settings, settingsData, { updated_at: new Date() });
    return settings;
  }

  // Count methods
  countUsers() {
    return this.users.size;
  }

  countTools() {
    return this.tools.size;
  }

  countCategories() {
    return this.categories.size;
  }

  countBlogPosts() {
    return this.blogPosts.size;
  }
}

// Create singleton instance
const memoryStore = new MemoryStore();

module.exports = memoryStore; 