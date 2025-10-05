import { Plus, Film } from 'lucide-react';

export default function CompilationPage() {
  const compilations = [
    { id: '1', title: 'Best Moments', clips: 12, duration: '8:45' },
    { id: '2', title: 'Product Highlights', clips: 8, duration: '5:20' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">Compilations</h2>
        <button className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
          <Plus size={20} />
          <span>New Compilation</span>
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {compilations.map((comp) => (
          <div key={comp.id} className="bg-white rounded-lg shadow p-6">
            <Film className="h-10 w-10 text-indigo-600 mb-3" />
            <h3 className="text-lg font-semibold mb-2">{comp.title}</h3>
            <p className="text-sm text-gray-600">{comp.clips} clips • {comp.duration}</p>
            <button className="mt-4 w-full border border-indigo-600 text-indigo-600 py-2 rounded-lg hover:bg-indigo-50">
              Edit
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}