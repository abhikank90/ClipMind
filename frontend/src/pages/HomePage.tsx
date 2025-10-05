import { Video, Clock, TrendingUp, Film } from 'lucide-react';

export default function HomePage() {
  const stats = [
    { label: 'Total Videos', value: '1,234', icon: Video, color: 'bg-blue-500' },
    { label: 'Total Hours', value: '456', icon: Clock, color: 'bg-green-500' },
    { label: 'Searches Today', value: '89', icon: TrendingUp, color: 'bg-purple-500' },
    { label: 'Compilations', value: '23', icon: Film, color: 'bg-orange-500' },
  ];

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <h2 className="text-3xl font-bold mb-2">Welcome to ClipMind</h2>
        <p className="text-indigo-100 text-lg">AI-powered video memory and semantic search</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
            <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Start</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border rounded-lg hover:border-indigo-500">
            <Video className="h-8 w-8 text-indigo-600 mb-2" />
            <h4 className="font-semibold mb-1">Upload Videos</h4>
            <p className="text-sm text-gray-600">Add your video content</p>
          </div>
          <div className="p-4 border rounded-lg hover:border-indigo-500">
            <TrendingUp className="h-8 w-8 text-indigo-600 mb-2" />
            <h4 className="font-semibold mb-1">Smart Search</h4>
            <p className="text-sm text-gray-600">Find clips instantly</p>
          </div>
          <div className="p-4 border rounded-lg hover:border-indigo-500">
            <Film className="h-8 w-8 text-indigo-600 mb-2" />
            <h4 className="font-semibold mb-1">Create Compilations</h4>
            <p className="text-sm text-gray-600">Build highlight reels</p>
          </div>
        </div>
      </div>
    </div>
  );
}