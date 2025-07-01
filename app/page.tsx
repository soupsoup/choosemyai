'use client'

import { useState, useEffect } from 'react'

interface Tool {
  id: number
  name: string
  description: string
  url: string
  image_url?: string
  categories: string[]
  pricing: string
  is_approved: boolean
}

interface Category {
  id: number
  name: string
  description: string
}

export default function Home() {
  const [tools, setTools] = useState<Tool[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [filteredTools, setFilteredTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All Categories')
  const [sortBy, setSortBy] = useState('Most Popular')

  useEffect(() => {
    fetchTools()
  }, [])

  useEffect(() => {
    filterTools()
  }, [tools, searchTerm, selectedCategory, sortBy])

  const fetchTools = async () => {
    try {
      const response = await fetch('/.netlify/functions/tools')
      const data = await response.json()
      
      console.log('API Response:', data) // Debug log
      
      if (!response.ok) {
        // Handle API errors
        throw new Error(data.error || 'Failed to fetch tools')
      }
      
      setTools(data.tools || [])
      setCategories(data.categories || [])
      
      if (data.message) {
        console.log('API Message:', data.message)
      }
    } catch (err) {
      console.error('Fetch error:', err)
      setError(err instanceof Error ? err.message : 'An error occurred while loading AI tools')
    } finally {
      setLoading(false)
    }
  }

  const filterTools = () => {
    let filtered = [...tools]

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(tool => 
        tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by category
    if (selectedCategory !== 'All Categories') {
      filtered = filtered.filter(tool => 
        tool.categories.includes(selectedCategory)
      )
    }

    // Sort
    if (sortBy === 'Most Popular') {
      // Keep current order (could be enhanced with actual popularity data)
    } else if (sortBy === 'Newest') {
      filtered.sort((a, b) => b.id - a.id)
    } else if (sortBy === 'Name') {
      filtered.sort((a, b) => a.name.localeCompare(b.name))
    }

    setFilteredTools(filtered)
  }

  const getPricingColor = (pricing: string) => {
    return pricing.toLowerCase() === 'free' ? 'text-green-600' : 'text-orange-600'
  }

  const getCategoryIcon = (categories: string[]) => {
    if (categories.includes('AI Image Generation')) return '🎨'
    if (categories.includes('AI Development')) return '💻'
    if (categories.includes('AI Writing') || categories.includes('AI Chatbots')) return '🤖'
    if (categories.includes('AI Video')) return '🎬'
    if (categories.includes('AI Audio')) return '🎵'
    if (categories.includes('AI Business')) return '💼'
    if (categories.includes('AI Research')) return '🔬'
    if (categories.includes('AI Productivity')) return '⚡'
    return '🔧'
  }

  const getCategoryColor = (categories: string[]) => {
    if (categories.includes('AI Image Generation')) return 'bg-purple-500 hover:bg-purple-600'
    if (categories.includes('AI Development')) return 'bg-green-500 hover:bg-green-600'
    if (categories.includes('AI Writing') || categories.includes('AI Chatbots')) return 'bg-blue-500 hover:bg-blue-600'
    if (categories.includes('AI Video')) return 'bg-red-500 hover:bg-red-600'
    if (categories.includes('AI Audio')) return 'bg-yellow-500 hover:bg-yellow-600'
    if (categories.includes('AI Business')) return 'bg-indigo-500 hover:bg-indigo-600'
    if (categories.includes('AI Research')) return 'bg-pink-500 hover:bg-pink-600'
    if (categories.includes('AI Productivity')) return 'bg-teal-500 hover:bg-teal-600'
    return 'bg-gray-500 hover:bg-gray-600'
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading AI tools...</p>
          </div>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Choose My AI</h1>
              <div className="flex items-center space-x-4">
                <button className="text-gray-600 hover:text-gray-900">Home</button>
                <button className="text-gray-600 hover:text-gray-900">Blog</button>
                <button className="text-gray-600 hover:text-gray-900">🌙</button>
                <button className="text-gray-600 hover:text-gray-900">🔍</button>
                <button className="text-gray-600 hover:text-gray-900">Log in</button>
                <button className="bg-gray-900 text-white px-4 py-2 rounded-lg">Sign up</button>
              </div>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-16">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-red-50 border border-red-200 rounded-lg p-8">
              <div className="text-red-600 text-6xl mb-4">⚠️</div>
              <h2 className="text-2xl font-bold text-red-800 mb-4">Service Unavailable</h2>
              <p className="text-red-700 mb-6">{error}</p>
              <div className="space-y-4">
                <button 
                  onClick={fetchTools}
                  className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
                >
                  Try Again
                </button>
                <p className="text-sm text-red-600">
                  If this problem persists, please contact the administrator.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Choose My AI</h1>
            <div className="flex items-center space-x-4">
              <button className="text-gray-600 hover:text-gray-900">Home</button>
              <button className="text-gray-600 hover:text-gray-900">Blog</button>
              <button className="text-gray-600 hover:text-gray-900">🌙</button>
              <button className="text-gray-600 hover:text-gray-900">🔍</button>
              <button className="text-gray-600 hover:text-gray-900">Log in</button>
              <button className="bg-gray-900 text-white px-4 py-2 rounded-lg">Sign up</button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            Find the Perfect AI Tool
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Discover and compare hundreds of AI tools to enhance your workflow
          </p>
          <div className="max-w-2xl mx-auto flex">
            <input
              type="text"
              placeholder="Search AI tools..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button className="bg-gray-900 text-white px-6 py-3 rounded-r-lg hover:bg-gray-800 transition-colors">
              🔍 Search
            </button>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <aside className="lg:w-1/4">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Filters</h3>
              
              <div className="mb-6">
                <input
                  type="text"
                  placeholder="Search tools..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option>All Categories</option>
                  {categories.map(category => (
                    <option key={category.id} value={category.name}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option>Most Popular</option>
                  <option>Newest</option>
                  <option>Name</option>
                </select>
              </div>

              <button 
                onClick={filterTools}
                className="w-full bg-gray-900 text-white py-2 rounded-lg hover:bg-gray-800 transition-colors"
              >
                Apply Filters
              </button>
            </div>
          </aside>

          {/* Tools Grid */}
          <main className="lg:w-3/4">
            <div className="mb-6">
              <p className="text-gray-600">
                Showing {filteredTools.length} of {tools.length} tools
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTools.map((tool) => (
                <div key={tool.id} className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
                  <div className="w-full h-40 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                    {tool.image_url ? (
                      <img 
                        src={tool.image_url} 
                        alt={tool.name}
                        className="w-full h-full object-cover rounded-lg"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                          const nextElement = target.nextElementSibling as HTMLElement;
                          if (nextElement) nextElement.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div className="flex items-center justify-center w-full h-full text-gray-400">
                      <span className="text-4xl">{getCategoryIcon(tool.categories)}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold">{tool.name}</h3>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {tool.categories[0] || 'AI Tool'}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {tool.description}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-yellow-500">⭐</span>
                      <span className="text-sm text-gray-600">4.8</span>
                      <span className="text-gray-400">👍</span>
                      <span className="text-sm text-gray-600">1250</span>
                    </div>
                    <a
                      href={tool.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      View Details
                    </a>
                  </div>
                </div>
              ))}
            </div>

            {filteredTools.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">No AI tools found matching your criteria.</p>
              </div>
            )}
          </main>
        </div>
      </div>
    </main>
  )
} 