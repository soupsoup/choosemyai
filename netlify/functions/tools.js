const { createClient } = require('@supabase/supabase-js')

exports.handler = async (event, context) => {
  // Handle CORS
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
      },
      body: ''
    }
  }

  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ error: 'Method not allowed' })
    }
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL
    const supabaseKey = process.env.SUPABASE_ANON_KEY

    // Check if Supabase credentials are available
    if (!supabaseUrl || !supabaseKey) {
      console.error('Supabase credentials not found')
      return {
        statusCode: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          error: 'Database configuration missing. Please contact the administrator.',
          details: 'Supabase environment variables are not configured.',
          debug: {
            supabaseUrl: supabaseUrl ? 'Set' : 'Not set',
            supabaseKey: supabaseKey ? 'Set' : 'Not set'
          }
        })
      }
    }

    // Create Supabase client
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Fetch tools with their categories
    const { data: tools, error: toolsError } = await supabase
      .from('tools')
      .select(`
        id,
        name,
        description,
        url,
        image_url,
        youtube_url,
        resources,
        is_approved,
        created_at,
        tool_categories (
          categories (
            id,
            name
          )
        )
      `)
      .eq('is_approved', true)
      .order('created_at', { ascending: false })

    if (toolsError) {
      console.error('Error fetching tools:', toolsError)
      return {
        statusCode: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          error: 'Failed to fetch AI tools from database. Please try again later.',
          details: toolsError.message
        })
      }
    }

    // Transform the data
    const transformedTools = tools?.map(tool => ({
      id: tool.id,
      name: tool.name,
      description: tool.description,
      url: tool.url,
      image_url: tool.image_url || `https://via.placeholder.com/300x200?text=${encodeURIComponent(tool.name)}`,
      youtube_url: tool.youtube_url,
      resources: tool.resources,
      categories: tool.tool_categories?.map(tc => tc.categories.name) || [],
      pricing: 'Free',
      is_approved: tool.is_approved,
      created_at: tool.created_at
    })) || []

    // Fetch categories
    const { data: categories, error: categoriesError } = await supabase
      .from('categories')
      .select('id, name, description')
      .order('name')

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tools: transformedTools,
        categories: categories || [],
        count: transformedTools.length,
        message: transformedTools.length > 0 ? 'Data loaded successfully from database' : 'No approved tools found'
      })
    }

  } catch (error) {
    console.error('Error in tools function:', error)
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        error: 'Internal server error. Please try again later.',
        details: error.message
      })
    }
  }
} 