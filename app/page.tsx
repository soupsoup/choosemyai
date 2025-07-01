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

export default function Home() {
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTools()
  }, [])

  const fetchTools = async () => {
    try {
      const response = await fetch('/api/tools')
      if (!response.ok) {
        throw new Error('Failed to fetch tools')
      }
      const data = await response.json()
      setTools(data.tools)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const getPricingColor = (pricing: string) => {
    return pricing.toLowerCase() === 'free' ? 'text-green-600' : 'text-orange-600'
  }

  const getCategoryIcon = (categories: string[]) => {
    if (categories.includes('AI Image Generation')) return '🎨'
    if (categories.includes('AI Development')) return '💻'
    if (categories.includes('AI Writing') || categories.includes('AI Chatbots')) return '🤖'
    return '🔧'
  }

  const getCategoryColor = (categories: string[]) => {
    if (categories.includes('AI Image Generation')) return 'bg-purple-500 hover:bg-purple-600'
    if (categories.includes('AI Development')) return 'bg-green-500 hover:bg-green-600'
    if (categories.includes('AI Writing') || categories.includes('AI Chatbots')) return 'bg-blue-500 hover:bg-blue-600'
    return 'bg-gray-500 hover:bg-gray-600'
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
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
      <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              Error: {error}
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            ChooseMyAI
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Discover the perfect AI tools for your needs
          </p>
          <p className="text-sm text-gray-500">
            {tools.length} AI tools available
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {tools.map((tool) => (
            <div key={tool.id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className={`w-12 h-12 ${getCategoryColor(tool.categories).split(' ')[0]} rounded-lg mb-4 flex items-center justify-center`}>
                <span className="text-white text-xl">{getCategoryIcon(tool.categories)}</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">{tool.name}</h3>
              <p className="text-gray-600 mb-4 text-sm">
                {tool.description}
              </p>
              <div className="mb-3">
                <div className="flex flex-wrap gap-1">
                  {tool.categories.map((category, index) => (
                    <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {category}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className={`text-sm font-medium ${getPricingColor(tool.pricing)}`}>
                  {tool.pricing}
                </span>
                <a 
                  href={tool.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`px-4 py-2 text-white rounded-lg transition-colors ${getCategoryColor(tool.categories)}`}
                >
                  Try Now
                </a>
              </div>
            </div>
          ))}
        </div>

        {tools.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No AI tools found.</p>
          </div>
        )}

        <footer className="text-center mt-16 text-gray-500">
          <p>Built with Next.js and Tailwind CSS</p>
        </footer>
      </div>
    </main>
  )
} 