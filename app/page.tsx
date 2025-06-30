export default function Home() {
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
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* AI Tools Grid */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-blue-500 rounded-lg mb-4 flex items-center justify-center">
              <span className="text-white text-xl">🤖</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">ChatGPT</h3>
            <p className="text-gray-600 mb-4">
              Conversational AI assistant for various tasks
            </p>
            <div className="flex items-center justify-between">
              <span className="text-sm text-green-600 font-medium">Free</span>
              <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                Try Now
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-purple-500 rounded-lg mb-4 flex items-center justify-center">
              <span className="text-white text-xl">🎨</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">Midjourney</h3>
            <p className="text-gray-600 mb-4">
              AI-powered image generation from text
            </p>
            <div className="flex items-center justify-between">
              <span className="text-sm text-orange-600 font-medium">Paid</span>
              <button className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
                Try Now
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-green-500 rounded-lg mb-4 flex items-center justify-center">
              <span className="text-white text-xl">💻</span>
            </div>
            <h3 className="text-xl font-semibold mb-2">GitHub Copilot</h3>
            <p className="text-gray-600 mb-4">
              AI pair programmer for code completion
            </p>
            <div className="flex items-center justify-between">
              <span className="text-sm text-orange-600 font-medium">Paid</span>
              <button className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors">
                Try Now
              </button>
            </div>
          </div>
        </div>

        <footer className="text-center mt-16 text-gray-500">
          <p>Built with Next.js and Tailwind CSS</p>
        </footer>
      </div>
    </main>
  )
} 