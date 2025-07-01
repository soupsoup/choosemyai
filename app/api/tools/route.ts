import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_ANON_KEY

export async function GET() {
  try {
    // Check if Supabase credentials are available
    if (!supabaseUrl || !supabaseKey) {
      console.error('Supabase credentials not found')
      return NextResponse.json(
        { error: 'Database configuration missing' },
        { status: 500 }
      )
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
      return NextResponse.json(
        { error: 'Failed to fetch tools from database' },
        { status: 500 }
      )
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
      count: transformedTools.length 
    })
  } catch (error) {
    console.error('Error in tools API:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 