const { sequelize, User, Category, Tool, Comment, BlogPost, ToolVote, CommentVote, AppearanceSettings } = require('../models');

async function syncDatabase() {
  try {
    // Sync all models with database
    await sequelize.sync({ force: false });
    console.log('✅ Database synced successfully');
    
    // Check if we need to seed initial data
    const userCount = await User.count();
    if (userCount === 0) {
      await seedInitialData();
      console.log('✅ Initial data seeded successfully');
    }
  } catch (error) {
    console.error('❌ Database sync failed:', error);
    throw error;
  }
}

async function seedInitialData() {
  try {
    // Create admin user
    const adminUser = await User.create({
      username: 'admin',
      email: 'admin@choosemyai.com',
      password_hash: 'admin123', // Will be hashed by the hook
      is_admin: true,
      is_moderator: true
    });

    // Create some default categories
    const categories = await Category.bulkCreate([
      { name: 'AI Writing', description: 'AI-powered writing and content creation tools' },
      { name: 'AI Image Generation', description: 'Tools for creating images with AI' },
      { name: 'AI Video', description: 'AI video creation and editing tools' },
      { name: 'AI Chatbots', description: 'Chatbot and conversational AI tools' },
      { name: 'AI Research', description: 'Research and analysis AI tools' },
      { name: 'AI Productivity', description: 'Productivity and workflow AI tools' },
      { name: 'AI Development', description: 'AI tools for developers' },
      { name: 'AI Business', description: 'Business and marketing AI tools' }
    ]);

    // Create some sample tools
    const sampleTools = await Tool.bulkCreate([
      {
        name: 'ChatGPT',
        description: 'Advanced language model for conversation and text generation',
        url: 'https://chat.openai.com',
        image_url: 'https://via.placeholder.com/300x200?text=ChatGPT',
        user_id: adminUser.id,
        is_approved: true
      },
      {
        name: 'Midjourney',
        description: 'AI art generation tool for creating stunning images',
        url: 'https://midjourney.com',
        image_url: 'https://via.placeholder.com/300x200?text=Midjourney',
        user_id: adminUser.id,
        is_approved: true
      },
      {
        name: 'GitHub Copilot',
        description: 'AI-powered code completion and generation tool',
        url: 'https://github.com/features/copilot',
        image_url: 'https://via.placeholder.com/300x200?text=GitHub+Copilot',
        user_id: adminUser.id,
        is_approved: true
      }
    ]);

    // Associate tools with categories
    await sampleTools[0].addCategories([categories[0], categories[4]]); // ChatGPT - AI Writing, AI Research
    await sampleTools[1].addCategories([categories[1]]); // Midjourney - AI Image Generation
    await sampleTools[2].addCategories([categories[6]]); // GitHub Copilot - AI Development

    // Create a sample blog post
    await BlogPost.create({
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

    console.log('✅ Sample data created successfully');
  } catch (error) {
    console.error('❌ Error seeding initial data:', error);
    throw error;
  }
}

module.exports = {
  syncDatabase,
  seedInitialData
}; 