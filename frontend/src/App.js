import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Filter, Star, ExternalLink, Sparkles, Zap, Brain, Music, Image, Video, Code2, Database, Gamepad2 } from 'lucide-react';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const categoryIcons = {
  music_generation: Music,
  image_creation: Image,
  video_editing: Video,
  text_generation: Brain,
  automation: Zap,
  data_analysis: Database,
  gaming: Gamepad2,
  code_generation: Code2
};

const categoryColors = {
  music_generation: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  image_creation: 'bg-pink-500/10 text-pink-400 border-pink-500/20',
  video_editing: 'bg-red-500/10 text-red-400 border-red-500/20',
  text_generation: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  automation: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  data_analysis: 'bg-green-500/10 text-green-400 border-green-500/20',
  gaming: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  code_generation: 'bg-orange-500/10 text-orange-400 border-orange-500/20'
};

const priceModelColors = {
  free: 'bg-green-500/10 text-green-400',
  freemium: 'bg-blue-500/10 text-blue-400',
  subscription: 'bg-orange-500/10 text-orange-400',
  one_time: 'bg-purple-500/10 text-purple-400'
};

function App() {
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedPriceModel, setSelectedPriceModel] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [categories, setCategories] = useState([]);
  const [priceModels, setPriceModels] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  // Fetch filter options
  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        const [categoriesRes, priceModelsRes, platformsRes] = await Promise.all([
          axios.get(`${API}/categories`),
          axios.get(`${API}/price-models`),
          axios.get(`${API}/platforms`)
        ]);
        
        setCategories(categoriesRes.data);
        setPriceModels(priceModelsRes.data);
        setPlatforms(platformsRes.data);
      } catch (error) {
        console.error('Error fetching filter options:', error);
      }
    };

    fetchFilterOptions();
  }, []);

  // Seed data on first load
  useEffect(() => {
    const seedData = async () => {
      try {
        await axios.post(`${API}/seed-data`);
      } catch (error) {
        console.log('Seed data already exists or error seeding:', error.response?.data?.message);
      }
    };

    seedData();
  }, []);

  // Fetch tools with filters
  useEffect(() => {
    const fetchTools = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (searchTerm) params.append('search', searchTerm);
        if (selectedCategory) params.append('category', selectedCategory);
        if (selectedPriceModel) params.append('price_model', selectedPriceModel);
        if (selectedPlatform) params.append('platform', selectedPlatform);
        params.append('page', page.toString());
        params.append('per_page', '20');

        const response = await axios.get(`${API}/tools?${params.toString()}`);
        setTools(response.data.tools);
        setTotal(response.data.total);
      } catch (error) {
        console.error('Error fetching tools:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTools();
  }, [searchTerm, selectedCategory, selectedPriceModel, selectedPlatform, page]);

  const formatCategoryName = (category) => {
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatPriceModel = (priceModel) => {
    return priceModel.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatPlatform = (platform) => {
    return platform.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedCategory('');
    setSelectedPriceModel('');
    setSelectedPlatform('');
    setPage(1);
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating)
            ? 'fill-yellow-400 text-yellow-400'
            : i < rating
            ? 'fill-yellow-400/50 text-yellow-400'
            : 'text-gray-600'
        }`}
      />
    ));
  };

  const ToolCard = ({ tool }) => {
    const IconComponent = categoryIcons[tool.category] || Sparkles;
    
    return (
      <Card className="group bg-gray-900/50 border-gray-800 hover:border-gray-700 transition-all duration-300 hover:transform hover:scale-[1.02] backdrop-blur-sm">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${categoryColors[tool.category]}`}>
                <IconComponent className="w-5 h-5" />
              </div>
              <div>
                <CardTitle className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors">
                  {tool.name}
                </CardTitle>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex items-center gap-1">
                    {renderStars(tool.rating)}
                  </div>
                  <span className="text-sm text-gray-400">
                    {tool.rating}/5 ({tool.review_count.toLocaleString()})
                  </span>
                </div>
              </div>
            </div>
            <a
              href={tool.website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
            >
              <ExternalLink className="w-4 h-4 text-gray-400" />
            </a>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <p className="text-gray-300 text-sm mb-4 line-clamp-2">
            {tool.description}
          </p>
          
          <div className="flex flex-wrap gap-2 mb-4">
            <Badge className={categoryColors[tool.category]}>
              {formatCategoryName(tool.category)}
            </Badge>
            <Badge className={`${priceModelColors[tool.price_model]} border`}>
              {formatPriceModel(tool.price_model)}
            </Badge>
            <Badge variant="outline" className="text-gray-400 border-gray-600">
              {formatPlatform(tool.platform)}
            </Badge>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-blue-400">
              {tool.price_details}
            </span>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
              AI Tools Hub
            </h1>
            <p className="text-gray-400 text-lg">
              Discover the best agentic AI tools and platforms for your needs
            </p>
          </div>
          
          {/* Search and Filters */}
          <div className="space-y-4">
            <div className="relative max-w-2xl mx-auto">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Search AI tools..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-gray-800/50 border-gray-700 text-white placeholder-gray-400 focus:border-blue-500"
              />
            </div>
            
            <div className="flex flex-wrap gap-4 justify-center items-center">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-40 bg-gray-800/50 border-gray-700 text-white">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {categories.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value} className="text-white hover:bg-gray-700">
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedPriceModel} onValueChange={setSelectedPriceModel}>
                <SelectTrigger className="w-40 bg-gray-800/50 border-gray-700 text-white">
                  <SelectValue placeholder="Price Model" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {priceModels.map((pm) => (
                    <SelectItem key={pm.value} value={pm.value} className="text-white hover:bg-gray-700">
                      {pm.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <SelectTrigger className="w-40 bg-gray-800/50 border-gray-700 text-white">
                  <SelectValue placeholder="Platform" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {platforms.map((platform) => (
                    <SelectItem key={platform.value} value={platform.value} className="text-white hover:bg-gray-700">
                      {platform.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button
                onClick={clearFilters}
                variant="outline"
                className="border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                <Filter className="w-4 h-4 mr-2" />
                Clear Filters
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Results Info */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-gray-400">
            {loading ? 'Loading...' : `Found ${total} AI tools`}
          </p>
        </div>

        {/* Tools Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className="bg-gray-900/50 border-gray-800 animate-pulse">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-700 rounded-lg"></div>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-700 rounded w-24"></div>
                      <div className="h-3 bg-gray-700 rounded w-16"></div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="h-3 bg-gray-700 rounded w-full"></div>
                    <div className="h-3 bg-gray-700 rounded w-3/4"></div>
                    <div className="flex gap-2">
                      <div className="h-6 bg-gray-700 rounded w-16"></div>
                      <div className="h-6 bg-gray-700 rounded w-12"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : tools.length === 0 ? (
          <div className="text-center py-16">
            <Sparkles className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">No tools found</h3>
            <p className="text-gray-500">Try adjusting your search criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tools.map((tool) => (
              <ToolCard key={tool.id} tool={tool} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {tools.length > 0 && total > 20 && (
          <div className="flex justify-center mt-12">
            <div className="flex gap-2">
              <Button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                variant="outline"
                className="border-gray-700 text-gray-300 hover:bg-gray-800 disabled:opacity-50"
              >
                Previous
              </Button>
              <span className="flex items-center px-4 text-gray-400">
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <Button
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(total / 20)}
                variant="outline"
                className="border-gray-700 text-gray-300 hover:bg-gray-800 disabled:opacity-50"
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-gray-900/50 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-gray-400">
              © 2025 AI Tools Hub. Discover, explore, and leverage the power of AI.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;