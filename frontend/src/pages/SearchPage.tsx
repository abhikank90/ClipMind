import { useState } from 'react';
import { Search } from 'lucide-react';

export default function SearchPage() {
  const [query, setQuery] = useState('');

  const results = [
    { id: '1', title: 'Product Demo', timestamp: '2:45', score: 95 },
    { id: '2', title: 'Team Meeting', timestamp: '15:30', score: 89 },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Search Videos</h2>
      <div className="bg-white rounded-lg shadow p-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search using natural language..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <button className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700">
          Search
        </button>
      </div>
      {query && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-4">Results for "{query}"</h3>
          {results.map((r) => (
            <div key={r.id} className="p-4 border-b last:border-b-0">
              <div className="flex justify-between">
                <div>
                  <h4 className="font-medium">{r.title}</h4>
                  <p className="text-sm text-gray-600">{r.timestamp}</p>
                </div>
                <span className="text-green-600 font-semibold">{r.score}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}