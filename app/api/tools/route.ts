import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_ANON_KEY

// Fallback data in case Supabase is not available
const fallbackTools = [
  {
    id: 1,
    name: 'ChatGPT',
    description: 'Advanced language model for natural conversations and content generation',
    url: 'https://chat.openai.com',
    image_url: 'https://via.placeholder.com/300x200?text=ChatGPT',
    categories: ['AI Chatbots', 'AI Writing'],
    pricing: 'Free',
    is_approved: true,
    created_at: '2024-01-01'
  },
  {
    id: 2,
    name: 'DALL-E',
    description: 'AI image generation from textual descriptions',
    url: 'https://openai.com/dall-e',
    image_url: 'https://via.placeholder.com/300x200?text=DALL-E',
    categories: ['AI Image Generation'],
    pricing: 'Free',
    is_approved: true,
    created_at: '2024-01-02'
  },
  {
    id: 3,
    name: 'Jasper',
    description: 'AI writing assistant for marketing and content creation',
    url: 'https://jasper.ai',
    image_url: 'https://via.placeholder.com/300x200?text=Jasper',
    categories: ['AI Writing'],
    pricing: 'Paid',
    is_approved: true,
    created_at: '2024-01-03'
  }
]

export async function GET() {
  try {
    // Check if Supabase credentials are available
    if (!supabaseUrl || !supabaseKey) {
      console.error('Supabase credentials not found, using fallback data')
      console.log('SUPABASE_URL:', supabaseUrl ? 'Set' : 'Not set')
      console.log('SUPABASE_ANON_KEY:', supabaseKey ? 'Set' : 'Not set')
      
      return NextResponse.json({ 
        tools: fallbackTools,
        categories: [
          { id: 1, name: 'AI Chatbots', description: 'Conversational AI tools' },
          { id: 2, name: 'AI Writing', description: 'Content generation tools' },
          { id: 3, name: 'AI Image Generation', description: 'Image creation tools' }
        ],
        count: fallbackTools.length,
        message: 'Using fallback data - Supabase not configured'
      })
    }

    // Create Supabase client
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Test the connection first
    const { data: testData, error: testError } = await supabase
      .from('tools')
      .select('count')
      .limit(1)

    if (testError) {
      console.error('Supabase connection test failed:', testError)
      return NextResponse.json({ 
        tools: fallbackTools,
        categories: [],
        count: fallbackTools.length,
        message: 'Supabase connection failed, using fallback data',
        error: testError.message
      })
    }

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
      return NextResponse.json({ 
        tools: fallbackTools,
        categories: [],
        count: fallbackTools.length,
        message: 'Database query failed, using fallback data',
        error: toolsError.message
      })
    }

    // Transform the data to match the expected format
    const transformedTools = tools?.map((tool: any) => ({
      id: tool.id,
      name: tool.name,
      description: tool.description,
      url: tool.url,
      image_url: tool.image_url || `https://via.placeholder.com/300x200?text=${encodeURIComponent(tool.name)}`,
      youtube_url: tool.youtube_url,
      resources: tool.resources,
      categories: tool.tool_categories?.map((tc: any) => tc.categories.name) || [],
      pricing: 'Free', // Default to Free since we don't have pricing data
      is_approved: tool.is_approved,
      created_at: tool.created_at
    })) || []

    // Also fetch categories for the filter
    const { data: categories, error: categoriesError } = await supabase
      .from('categories')
      .select('id, name, description')
      .order('name')

    if (categoriesError) {
      console.error('Error fetching categories:', categoriesError)
    }

    return NextResponse.json({ 
      tools: transformedTools,
      categories: categories || [],
      count: transformedTools.length,
      message: transformedTools.length > 3 ? 'Data loaded from Supabase' : 'Limited data available'
    })
  } catch (error) {
    console.error('Error in tools API:', error)
    return NextResponse.json({ 
      tools: fallbackTools,
      categories: [],
      count: fallbackTools.length,
      message: 'Server error, using fallback data',
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
} 