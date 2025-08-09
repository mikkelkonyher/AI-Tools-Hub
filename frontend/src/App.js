import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import { Search, Filter, Star, ExternalLink, Sparkles, Zap, Brain, Music, Image, Video, Code2, Database, Gamepad2, User, LogOut, LogIn, MessageCircle, Plus, Edit, Trash2, MoreVertical } from 'lucide-react';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from './components/ui/dialog';
import { Textarea } from './components/ui/textarea';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Separator } from './components/ui/separator';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './components/ui/dropdown-menu';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from './components/ui/alert-dialog';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Authentication Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      logout();
    }
  };

  const login = async (credentials) => {
    try {
      const response = await axios.post(`${API}/login`, credentials);
      const { access_token } = response.data;
      
      setToken(access_token);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchCurrentUser();
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      await axios.post(`${API}/register`, userData);
      return await login({ username: userData.username, password: userData.password });
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Category icons and colors
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

// Auth Modal Component
const AuthModal = ({ isOpen, onClose }) => {
  const { login, register } = useAuth();
  const [activeTab, setActiveTab] = useState('login');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login({
      username: formData.username,
      password: formData.password
    });

    if (result.success) {
      onClose();
      setFormData({ username: '', email: '', password: '', confirmPassword: '' });
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const result = await register({
      username: formData.username,
      email: formData.email,
      password: formData.password
    });

    if (result.success) {
      onClose();
      setFormData({ username: '', email: '', password: '', confirmPassword: '' });
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-gray-900 border-gray-700 text-white">
        <DialogHeader>
          <DialogTitle>Join AI Tools Hub</DialogTitle>
          <DialogDescription className="text-gray-400">
            Sign in to write reviews and join the community
          </DialogDescription>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 bg-gray-800">
            <TabsTrigger value="login" className="text-white">Login</TabsTrigger>
            <TabsTrigger value="register" className="text-white">Register</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              {error && <p className="text-red-400 text-sm">{error}</p>}
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="register">
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <Label htmlFor="reg-username">Username</Label>
                <Input
                  id="reg-username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="reg-password">Password</Label>
                <Input
                  id="reg-password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="confirm-password">Confirm Password</Label>
                <Input
                  id="confirm-password"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="bg-gray-800 border-gray-600 text-white"
                  required
                />
              </div>
              {error && <p className="text-red-400 text-sm">{error}</p>}
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

// Review Modal Component
const ReviewModal = ({ isOpen, onClose, tool }) => {
  const { isAuthenticated } = useAuth();
  const [reviewData, setReviewData] = useState({
    rating: 5,
    title: '',
    content: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) return;

    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/reviews`, {
        tool_id: tool.id,
        ...reviewData
      });
      
      onClose();
      setReviewData({ rating: 5, title: '', content: '' });
      // Refresh page to show new review
      window.location.reload();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit review');
    }
    setLoading(false);
  };

  const handleRatingClick = (rating) => {
    setReviewData(prev => ({ ...prev, rating }));
  };

  if (!tool) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-gray-900 border-gray-700 text-white max-w-md">
        <DialogHeader>
          <DialogTitle>Write a Review for {tool.name}</DialogTitle>
          <DialogDescription className="text-gray-400">
            Share your experience with this AI tool
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label>Rating</Label>
            <div className="flex gap-1 mt-2">
              {[1, 2, 3, 4, 5].map((rating) => (
                <Star
                  key={rating}
                  className={`w-6 h-6 cursor-pointer ${
                    rating <= reviewData.rating
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-600 hover:text-yellow-400'
                  }`}
                  onClick={() => handleRatingClick(rating)}
                />
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="review-title">Title</Label>
            <Input
              id="review-title"
              value={reviewData.title}
              onChange={(e) => setReviewData(prev => ({ ...prev, title: e.target.value }))}
              className="bg-gray-800 border-gray-600 text-white"
              placeholder="Summarize your experience"
              required
            />
          </div>

          <div>
            <Label htmlFor="review-content">Review</Label>
            <Textarea
              id="review-content"
              value={reviewData.content}
              onChange={(e) => setReviewData(prev => ({ ...prev, content: e.target.value }))}
              className="bg-gray-800 border-gray-600 text-white min-h-24"
              placeholder="Tell us about your experience with this tool..."
              required
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Submitting...' : 'Submit Review'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Tool Detail Modal Component
const ToolDetailModal = ({ isOpen, onClose, tool }) => {
  const { isAuthenticated } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [loadingReviews, setLoadingReviews] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);

  useEffect(() => {
    if (isOpen && tool) {
      fetchReviews();
    }
  }, [isOpen, tool]);

  const fetchReviews = async () => {
    if (!tool) return;
    
    setLoadingReviews(true);
    try {
      const response = await axios.get(`${API}/reviews/${tool.id}`);
      setReviews(response.data.reviews);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    }
    setLoadingReviews(false);
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

  if (!tool) return null;

  const IconComponent = categoryIcons[tool.category] || Sparkles;

  return (
    <>
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="bg-gray-900 border-gray-700 text-white max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${categoryColors[tool.category]}`}>
                <IconComponent className="w-6 h-6" />
              </div>
              <div>
                <DialogTitle className="text-2xl">{tool.name}</DialogTitle>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex items-center gap-1">
                    {renderStars(tool.rating)}
                  </div>
                  <span className="text-sm text-gray-400">
                    {tool.rating}/5 ({tool.review_count.toLocaleString()} reviews)
                  </span>
                </div>
              </div>
            </div>
          </DialogHeader>

          <div className="space-y-6">
            <div>
              <p className="text-gray-300 text-lg">{tool.description}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge className={categoryColors[tool.category]}>
                {tool.category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Badge>
              <Badge className={`${priceModelColors[tool.price_model]} border`}>
                {tool.price_model.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Badge>
              <Badge variant="outline" className="text-gray-400 border-gray-600">
                {tool.platform.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Badge>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-lg font-medium text-blue-400">
                {tool.price_details}
              </span>
              <div className="flex gap-2">
                <Button asChild variant="outline">
                  <a href={tool.website_url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Visit Website
                  </a>
                </Button>
                {isAuthenticated && (
                  <Button onClick={() => setShowReviewModal(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Write Review
                  </Button>
                )}
              </div>
            </div>

            <Separator className="bg-gray-700" />

            <div>
              <h3 className="text-xl font-semibold mb-4">Reviews</h3>
              
              {loadingReviews ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
                  <p className="text-gray-400 mt-2">Loading reviews...</p>
                </div>
              ) : reviews.length === 0 ? (
                <div className="text-center py-8">
                  <MessageCircle className="w-12 h-12 text-gray-600 mx-auto mb-2" />
                  <p className="text-gray-400">No reviews yet. Be the first to review!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <Card key={review.id} className="bg-gray-800/50 border-gray-700">
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="font-medium text-white">{review.title}</h4>
                            <p className="text-sm text-gray-400">by {review.username}</p>
                          </div>
                          <div className="flex items-center gap-1">
                            {renderStars(review.rating)}
                          </div>
                        </div>
                        <p className="text-gray-300 mt-2">{review.content}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(review.created_at).toLocaleDateString()}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <ReviewModal
        isOpen={showReviewModal}
        onClose={() => setShowReviewModal(false)}
        tool={tool}
      />
    </>
  );
};

// Main App Component
function App() {
  const { user, logout, isAuthenticated } = useAuth();
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
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);
  const [showToolDetail, setShowToolDetail] = useState(false);

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

  const handleToolClick = (tool) => {
    setSelectedTool(tool);
    setShowToolDetail(true);
  };

  const ToolCard = ({ tool }) => {
    const IconComponent = categoryIcons[tool.category] || Sparkles;
    
    return (
      <Card 
        className="group bg-gray-900/50 border-gray-800 hover:border-gray-700 transition-all duration-300 hover:transform hover:scale-[1.02] backdrop-blur-sm cursor-pointer"
        onClick={() => handleToolClick(tool)}
      >
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
            <button
              onClick={(e) => {
                e.stopPropagation();
                window.open(tool.website_url, '_blank');
              }}
              className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
            >
              <ExternalLink className="w-4 h-4 text-gray-400" />
            </button>
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
          <div className="flex items-center justify-between mb-6">
            <div className="text-center flex-1">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                AI Tools Hub
              </h1>
              <p className="text-gray-400 text-lg">
                Discover the best agentic AI tools and platforms for your needs
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-400">Welcome, {user?.username}</span>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={logout}
                    className="border-gray-700 text-gray-300 hover:bg-gray-800"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </Button>
                </div>
              ) : (
                <Button 
                  variant="outline"
                  onClick={() => setShowAuthModal(true)}
                  className="border-gray-700 text-gray-300 hover:bg-gray-800"
                >
                  <LogIn className="w-4 h-4 mr-2" />
                  Sign In
                </Button>
              )}
            </div>
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
              <Select value={selectedCategory || undefined} onValueChange={(value) => setSelectedCategory(value === 'all' ? '' : value)}>
                <SelectTrigger className="w-40 bg-gray-800/50 border-gray-700 text-white">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  <SelectItem value="all" className="text-white hover:bg-gray-700">All Categories</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value} className="text-white hover:bg-gray-700">
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedPriceModel || undefined} onValueChange={(value) => setSelectedPriceModel(value === 'all' ? '' : value)}>
                <SelectTrigger className="w-40 bg-gray-800/50 border-gray-700 text-white">
                  <SelectValue placeholder="Price Model" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  <SelectItem value="all" className="text-white hover:bg-gray-700">All Price Models</SelectItem>
                  {priceModels.map((pm) => (
                    <SelectItem key={pm.value} value={pm.value} className="text-white hover:bg-gray-700">
                      {pm.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={selectedPlatform || undefined} onValueChange={(value) => setSelectedPlatform(value === 'all' ? '' : value)}>
                <SelectTrigger className="w-40 bg-gray-800/50 border-gray-700 text-white">
                  <SelectValue placeholder="Platform" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  <SelectItem value="all" className="text-white hover:bg-gray-700">All Platforms</SelectItem>
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
          {!isAuthenticated && (
            <p className="text-sm text-gray-500">
              <Button variant="link" className="p-0 h-auto text-blue-400" onClick={() => setShowAuthModal(true)}>
                Sign in
              </Button>
              {' '}to write reviews and join discussions
            </p>
          )}
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

      {/* Modals */}
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
      <ToolDetailModal 
        isOpen={showToolDetail} 
        onClose={() => {
          setShowToolDetail(false);
          setSelectedTool(null);
        }} 
        tool={selectedTool} 
      />
    </div>
  );
}

// Main App with Auth Provider
function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}

export default AppWithAuth;