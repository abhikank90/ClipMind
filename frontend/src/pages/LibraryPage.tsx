import { Play } from 'lucide-react';

export default function LibraryPage() {
  const videos = [
    { id: '1', title: 'Project Demo', duration: '5:23', thumbnail: 'https://via.placeholder.com/640x360/4F46E5/FFFFFF?text=Demo' },
    { id: '2', title: 'Team Meeting', duration: '45:12', thumbnail: 'https://via.placeholder.com/640x360/7C3AED/FFFFFF?text=Meeting' },
    { id: '3', title: 'Product Launch', duration: '12:45', thumbnail: 'https://via.placeholder.com/640x360/2563EB/FFFFFF?text=Launch' },
    { id: '4', title: 'Tutorial', duration: '8:30', thumbnail: 'https://via.placeholder.com/640x360/059669/FFFFFF?text=Tutorial' },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Video Library</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video) => (
          <div key={video.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow group">
            <div className="relative aspect-video cursor-pointer">
              <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center">
                <Play className="h-12 w-12 text-white opacity-0 group-hover:opacity-100" />
              </div>
              <span className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                {video.duration}
              </span>
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-gray-900">{video.title}</h3>
              <p className="text-sm text-gray-600 mt-1">Uploaded 2 days ago</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}