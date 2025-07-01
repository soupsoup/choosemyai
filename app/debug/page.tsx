'use client'

import { useState } from 'react'

export default function DebugPage() {
  const [results, setResults] = useState<any[]>([])

  const testEndpoint = async (url: string, name: string) => {
    try {
      console.log(`Testing ${name}:`, url)
      const response = await fetch(url)
      const data = await response.json()
      
      setResults(prev => [...prev, {
        name,
        url,
        status: response.status,
        success: response.ok,
        data: data,
        timestamp: new Date().toISOString()
      }])
    } catch (error) {
      setResults(prev => [...prev, {
        name,
        url,
        status: 'ERROR',
        success: false,
        data: { error: error instanceof Error ? error.message : 'Unknown error' },
        timestamp: new Date().toISOString()
      }])
    }
  }

  const clearResults = () => setResults([])

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API Debug Page</h1>
        
        <div className="space-y-4 mb-8">
          <button
            onClick={() => testEndpoint('/.netlify/functions/tools', 'Netlify Function')}
            className="bg-blue-500 text-white px-4 py-2 rounded mr-4"
          >
            Test Netlify Function
          </button>
          
          <button
            onClick={() => testEndpoint('/api/tools', 'Next.js API Route')}
            className="bg-green-500 text-white px-4 py-2 rounded mr-4"
          >
            Test Next.js API
          </button>
          
          <button
            onClick={() => testEndpoint('/api/test', 'Next.js Test API')}
            className="bg-purple-500 text-white px-4 py-2 rounded mr-4"
          >
            Test Next.js Test API
          </button>
          
          <button
            onClick={clearResults}
            className="bg-red-500 text-white px-4 py-2 rounded"
          >
            Clear Results
          </button>
        </div>

        <div className="space-y-4">
          {results.map((result, index) => (
            <div key={index} className={`p-4 rounded-lg border ${
              result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold">{result.name}</h3>
                <span className={`px-2 py-1 rounded text-sm ${
                  result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {result.status}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{result.url}</p>
              <p className="text-xs text-gray-500 mb-2">{result.timestamp}</p>
              <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto max-h-40">
                {JSON.stringify(result.data, null, 2)}
              </pre>
            </div>
          ))}
        </div>

        {results.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Click the buttons above to test different API endpoints
          </div>
        )}
      </div>
    </div>
  )
} 