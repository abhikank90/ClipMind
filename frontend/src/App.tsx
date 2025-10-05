import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Home, Video, Search, Film, Upload } from 'lucide-react';
import HomePage from './pages/HomePage';
import LibraryPage from './pages/LibraryPage';
import SearchPage from './pages/SearchPage';
import CompilationPage from './pages/CompilationPage';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-8">
                <Link to="/" className="text-2xl font-bold text-indigo-600">ClipMind</Link>
                <nav className="hidden md:flex space-x-4">
                  <Link to="/" className="flex items-center space-x-2 px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
                    <Home size={20} />
                    <span>Home</span>
                  </Link>
                  <Link to="/library" className="flex items-center space-x-2 px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
                    <Video size={20} />
                    <span>Library</span>
                  </Link>
                  <Link to="/search" className="flex items-center space-x-2 px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
                    <Search size={20} />
                    <span>Search</span>
                  </Link>
                  <Link to="/compilations" className="flex items-center space-x-2 px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
                    <Film size={20} />
                    <span>Compilations</span>
                  </Link>
                </nav>
              </div>
              <button className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                <Upload size={20} />
                <span>Upload</span>
              </button>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/library" element={<LibraryPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/compilations" element={<CompilationPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;