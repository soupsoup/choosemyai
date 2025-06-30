const supabase = require('./supabase');
const bcrypt = require('bcryptjs');

// Database service class
class DatabaseService {
  constructor() {
    this.useSupabase = !!(process.env.SUPABASE_URL && process.env.SUPABASE_ANON_KEY);
    
    if (!this.useSupabase) {
      console.log('📝 Using in-memory database (no Supabase configuration)');
      this.initMemoryStore();
    } else {
      console.log('🗄️  Using Supabase database');
    }
  }

  // Initialize in-memory store as fallback
  initMemoryStore() {
    this.memoryStore = {
      users: new Map(),
      categories: new Map(),
      tools: new Map(),
      comments: new Map(),
      blogPosts: new Map(),
      nextId: { users: 1, categories: 1, tools: 1, comments: 1, blogPosts: 1 }
    };
    this.seedMemoryData();
  }

  // Seed memory data
  seedMemoryData() {
    // Create admin user
    const adminUser = {
      id: this.memoryStore.nextId.users++,
      username: 'admin',
      email: 'admin@choosemyai.com',
      password_hash: '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', // admin123
      is_admin: true,
      is_moderator: true,
      created_at: new Date().toISOString()
    };
    this.memoryStore.users.set(adminUser.id, adminUser);

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
    ].map(cat => {
      const category = { 
        id: this.memoryStore.nextId.categories++, 
        ...cat, 
        created_at: new Date().toISOString() 
      };
      this.memoryStore.categories.set(category.id, category);
      return category;
    });

    // Create sample tools
    const sampleTools = [
      {
        name: 'ChatGPT',
        description: 'Advanced language model for conversation and text generation',
        url: 'https://chat.openai.com',
        image_url: 'https://via.placeholder.com/300x200?text=ChatGPT',
        user_id: adminUser.id,
        is_approved: true,
        category_ids: [categories[0].id, categories[4].id]
      },
      {
        name: 'Midjourney',
        description: 'AI art generation tool for creating stunning images',
        url: 'https://midjourney.com',
        image_url: 'https://via.placeholder.com/300x200?text=Midjourney',
        user_id: adminUser.id,
        is_approved: true,
        category_ids: [categories[1].id]
      },
      {
        name: 'GitHub Copilot',
        description: 'AI-powered code completion and generation tool',
        url: 'https://github.com/features/copilot',
        image_url: 'https://via.placeholder.com/300x200?text=GitHub+Copilot',
        user_id: adminUser.id,
        is_approved: true,
        category_ids: [categories[6].id]
      }
    ].map(tool => {
      const toolObj = { 
        id: this.memoryStore.nextId.tools++, 
        ...tool, 
        created_at: new Date().toISOString() 
      };
      this.memoryStore.tools.set(toolObj.id, toolObj);
      return toolObj;
    });

    // Create sample blog post
    const blogPost = {
      id: this.memoryStore.nextId.blogPosts++,
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
      excerpt: 'Welcome to your comprehensive directory of AI tools and resources.',
      created_at: new Date().toISOString()
    };
    this.memoryStore.blogPosts.set(blogPost.id, blogPost);
  }

  // User methods
  async findUser(where) {
    if (this.useSupabase) {
      let query = supabase.from('users').select('*');
      
      if (where.id) query = query.eq('id', where.id);
      if (where.username) query = query.eq('username', where.username);
      if (where.email) query = query.eq('email', where.email);
      
      const { data, error } = await query.single();
      if (error) return null;
      return data;
    } else {
      for (const user of this.memoryStore.users.values()) {
        if (where.id && user.id === where.id) return user;
        if (where.username && user.username === where.username) return user;
        if (where.email && user.email === where.email) return user;
      }
      return null;
    }
  }

  async createUser(userData) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('users')
        .insert([userData])
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } else {
      const user = {
        id: this.memoryStore.nextId.users++,
        ...userData,
        created_at: new Date().toISOString()
      };
      this.memoryStore.users.set(user.id, user);
      return user;
    }
  }

  async getAllUsers() {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      return data;
    } else {
      return Array.from(this.memoryStore.users.values());
    }
  }

  async countUsers() {
    if (this.useSupabase) {
      const { count, error } = await supabase
        .from('users')
        .select('*', { count: 'exact', head: true });
      
      if (error) throw error;
      return count;
    } else {
      return this.memoryStore.users.size;
    }
  }

  // Category methods
  async getAllCategories() {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('categories')
        .select('*')
        .order('name', { ascending: true });
      
      if (error) throw error;
      return data;
    } else {
      return Array.from(this.memoryStore.categories.values());
    }
  }

  async findCategory(id) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('categories')
        .select('*')
        .eq('id', id)
        .single();
      
      if (error) return null;
      return data;
    } else {
      return this.memoryStore.categories.get(id);
    }
  }

  async createCategory(categoryData) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('categories')
        .insert([categoryData])
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } else {
      const category = {
        id: this.memoryStore.nextId.categories++,
        ...categoryData,
        created_at: new Date().toISOString()
      };
      this.memoryStore.categories.set(category.id, category);
      return category;
    }
  }

  async deleteCategory(id) {
    if (this.useSupabase) {
      const { error } = await supabase
        .from('categories')
        .delete()
        .eq('id', id);
      
      if (error) throw error;
      return true;
    } else {
      return this.memoryStore.categories.delete(id);
    }
  }

  // Tool methods
  async getAllTools(where = {}) {
    if (this.useSupabase) {
      let query = supabase
        .from('tools')
        .select(`
          *,
          users!tools_user_id_fkey(username),
          tool_categories(
            categories(*)
          )
        `);
      
      if (where.is_approved !== undefined) {
        query = query.eq('is_approved', where.is_approved);
      }
      
      if (where.user_id) {
        query = query.eq('user_id', where.user_id);
      }
      
      const { data, error } = await query.order('created_at', { ascending: false });
      
      if (error) throw error;
      
      // Transform the data to match expected format
      return data.map(tool => ({
        ...tool,
        author: tool.users,
        categories: tool.tool_categories.map(tc => tc.categories)
      }));
    } else {
      let tools = Array.from(this.memoryStore.tools.values());
      
      if (where.is_approved !== undefined) {
        tools = tools.filter(tool => tool.is_approved === where.is_approved);
      }
      
      if (where.user_id) {
        tools = tools.filter(tool => tool.user_id === where.user_id);
      }
      
      return tools.map(tool => ({
        ...tool,
        author: this.memoryStore.users.get(tool.user_id),
        categories: Array.from(this.memoryStore.categories.values())
          .filter(c => tool.category_ids.includes(c.id))
      }));
    }
  }

  async findTool(id) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('tools')
        .select(`
          *,
          users!tools_user_id_fkey(username),
          tool_categories(
            categories(*)
          )
        `)
        .eq('id', id)
        .single();
      
      if (error) return null;
      
      return {
        ...data,
        author: data.users,
        categories: data.tool_categories.map(tc => tc.categories)
      };
    } else {
      const tool = this.memoryStore.tools.get(id);
      if (!tool) return null;
      
      return {
        ...tool,
        author: this.memoryStore.users.get(tool.user_id),
        categories: Array.from(this.memoryStore.categories.values())
          .filter(c => tool.category_ids.includes(c.id))
      };
    }
  }

  async createTool(toolData) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('tools')
        .insert([toolData])
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } else {
      const tool = {
        id: this.memoryStore.nextId.tools++,
        ...toolData,
        created_at: new Date().toISOString()
      };
      this.memoryStore.tools.set(tool.id, tool);
      return tool;
    }
  }

  async updateTool(id, updates) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('tools')
        .update(updates)
        .eq('id', id)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } else {
      const tool = this.memoryStore.tools.get(id);
      if (!tool) throw new Error('Tool not found');
      
      Object.assign(tool, updates);
      return tool;
    }
  }

  async deleteTool(id) {
    if (this.useSupabase) {
      const { error } = await supabase
        .from('tools')
        .delete()
        .eq('id', id);
      
      if (error) throw error;
      return true;
    } else {
      return this.memoryStore.tools.delete(id);
    }
  }

  // Blog post methods
  async getAllBlogPosts() {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('blog_posts')
        .select(`
          *,
          users!blog_posts_user_id_fkey(username)
        `)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      
      return data.map(post => ({
        ...post,
        author: post.users
      }));
    } else {
      return Array.from(this.memoryStore.blogPosts.values()).map(post => ({
        ...post,
        author: this.memoryStore.users.get(post.user_id)
      }));
    }
  }

  async findBlogPost(id) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('blog_posts')
        .select(`
          *,
          users!blog_posts_user_id_fkey(username)
        `)
        .eq('id', id)
        .single();
      
      if (error) return null;
      
      return {
        ...data,
        author: data.users
      };
    } else {
      const post = this.memoryStore.blogPosts.get(id);
      if (!post) return null;
      
      return {
        ...post,
        author: this.memoryStore.users.get(post.user_id)
      };
    }
  }

  async createBlogPost(postData) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('blog_posts')
        .insert([postData])
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } else {
      const post = {
        id: this.memoryStore.nextId.blogPosts++,
        ...postData,
        created_at: new Date().toISOString()
      };
      this.memoryStore.blogPosts.set(post.id, post);
      return post;
    }
  }

  async updateBlogPost(id, updates) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('blog_posts')
        .update(updates)
        .eq('id', id)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } else {
      const post = this.memoryStore.blogPosts.get(id);
      if (!post) throw new Error('Blog post not found');
      
      Object.assign(post, updates);
      return post;
    }
  }

  async deleteBlogPost(id) {
    if (this.useSupabase) {
      const { error } = await supabase
        .from('blog_posts')
        .delete()
        .eq('id', id);
      
      if (error) throw error;
      return true;
    } else {
      return this.memoryStore.blogPosts.delete(id);
    }
  }

  // Comment methods
  async getComments(where) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('comments')
        .select(`
          *,
          users!comments_user_id_fkey(username)
        `)
        .eq('tool_id', where.tool_id)
        .order('created_at', { ascending: false });
      
      if (error) throw error;
      
      return data.map(comment => ({
        ...comment,
        author: comment.users
      }));
    } else {
      return Array.from(this.memoryStore.comments.values())
        .filter(comment => comment.tool_id === where.tool_id)
        .map(comment => ({
          ...comment,
          author: this.memoryStore.users.get(comment.user_id)
        }));
    }
  }

  async createComment(commentData) {
    if (this.useSupabase) {
      const { data, error } = await supabase
        .from('comments')
        .insert([commentData])
        .select()
        .single();
      
      if (error) throw error;
      return data;
    } else {
      const comment = {
        id: this.memoryStore.nextId.comments++,
        ...commentData,
        created_at: new Date().toISOString()
      };
      this.memoryStore.comments.set(comment.id, comment);
      return comment;
    }
  }

  // Count methods
  async countTools() {
    if (this.useSupabase) {
      const { count, error } = await supabase
        .from('tools')
        .select('*', { count: 'exact', head: true });
      
      if (error) throw error;
      return count;
    } else {
      return this.memoryStore.tools.size;
    }
  }

  async countCategories() {
    if (this.useSupabase) {
      const { count, error } = await supabase
        .from('categories')
        .select('*', { count: 'exact', head: true });
      
      if (error) throw error;
      return count;
    } else {
      return this.memoryStore.categories.size;
    }
  }

  async countBlogPosts() {
    if (this.useSupabase) {
      const { count, error } = await supabase
        .from('blog_posts')
        .select('*', { count: 'exact', head: true });
      
      if (error) throw error;
      return count;
    } else {
      return this.memoryStore.blogPosts.size;
    }
  }
}

// Create singleton instance
const db = new DatabaseService();

module.exports = db; 