// import React, { useState, useEffect } from 'react';
// import { ShoppingCart, Heart, Eye, Star, Search, LogOut, User } from 'lucide-react';

// const API_URL = 'http://localhost:8000';

// function App() {
//   const [currentUser, setCurrentUser] = useState(null);
//   const [view, setView] = useState('login'); // login, register, products, recommendations
//   const [products, setProducts] = useState([]);
//   const [recommendations, setRecommendations] = useState([]);
//   const [searchTerm, setSearchTerm] = useState('');
//   const [selectedCategory, setSelectedCategory] = useState('');
//   const [categories, setCategories] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');

//   // Auth forms
//   const [loginForm, setLoginForm] = useState({ email: '', password: '' });
//   const [registerForm, setRegisterForm] = useState({ username: '', email: '', password: '', preferences: [] });

//   useEffect(() => {
//     const user = localStorage.getItem('currentUser');
//     if (user) {
//       setCurrentUser(JSON.parse(user));
//       setView('products');
//       loadProducts();
//       loadCategories();
//     }
//   }, []);

//   useEffect(() => {
//     if (currentUser) {
//       loadRecommendations();
//     }
//   }, [currentUser]);

//   const loadCategories = async () => {
//     try {
//       const response = await fetch(`${API_URL}/api/categories`);
//       const data = await response.json();
//       setCategories(data.categories);
//     } catch (err) {
//       console.error('Error loading categories:', err);
//     }
//   };

//   const loadProducts = async () => {
//     setLoading(true);
//     try {
//       let url = `${API_URL}/api/products`;
//       const params = new URLSearchParams();
//       if (searchTerm) params.append('search', searchTerm);
//       if (selectedCategory) params.append('category', selectedCategory);
//       if (params.toString()) url += `?${params.toString()}`;

//       const response = await fetch(url);
//       const data = await response.json();
//       setProducts(data.products);
//     } catch (err) {
//       setError('Error loading products');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const loadRecommendations = async () => {
//     if (!currentUser) return;
//     try {
//       const response = await fetch(`${API_URL}/api/recommendations/${currentUser.user_id}?n=8`);
//       const data = await response.json();
//       setRecommendations(data.recommendations);
//     } catch (err) {
//       console.error('Error loading recommendations:', err);
//     }
//   };

//   const handleLogin = async (e) => {
//     e.preventDefault();
//     setError('');
//     setLoading(true);
//     try {
//       const response = await fetch(`${API_URL}/api/login`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(loginForm)
//       });
//       const data = await response.json();
//       if (response.ok) {
//         setCurrentUser(data);
//         localStorage.setItem('currentUser', JSON.stringify(data));
//         setView('products');
//         loadProducts();
//         loadCategories();
//       } else {
//         setError(data.detail);
//       }
//     } catch (err) {
//       setError('Login failed');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleRegister = async (e) => {
//     e.preventDefault();
//     setError('');
//     setLoading(true);
//     try {
//       const response = await fetch(`${API_URL}/api/register`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(registerForm)
//       });
//       const data = await response.json();
//       if (response.ok) {
//         setError('Registration successful! Please login.');
//         setView('login');
//       } else {
//         setError(data.detail);
//       }
//     } catch (err) {
//       setError('Registration failed');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleLogout = () => {
//     setCurrentUser(null);
//     localStorage.removeItem('currentUser');
//     setView('login');
//     setProducts([]);
//     setRecommendations([]);
//   };

//   const trackInteraction = async (productId, type) => {
//     if (!currentUser) return;
//     try {
//       await fetch(`${API_URL}/api/interactions`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           user_id: currentUser.user_id,
//           product_id: productId,
//           interaction_type: type
//         })
//       });
//       if (type === 'like') {
//         loadRecommendations();
//       }
//     } catch (err) {
//       console.error('Error tracking interaction:', err);
//     }
//   };

//   const handleSearch = () => {
//     loadProducts();
//   };

//   // Login View
//   if (view === 'login') {
//     return (
//       <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
//         <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
//           <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">E-Shop</h1>
//           <form onSubmit={handleLogin} className="space-y-4">
//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
//               <input
//                 type="email"
//                 value={loginForm.email}
//                 onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
//                 placeholder="alice@example.com"
//                 required
//               />
//             </div>
//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
//               <input
//                 type="password"
//                 value={loginForm.password}
//                 onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
//                 placeholder="password123"
//                 required
//               />
//             </div>
//             {error && <p className="text-red-500 text-sm">{error}</p>}
//             <button
//               type="submit"
//               disabled={loading}
//               className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
//             >
//               {loading ? 'Loading...' : 'Login'}
//             </button>
//           </form>
//           <p className="text-center mt-4 text-sm text-gray-600">
//             Don't have an account?{' '}
//             <button onClick={() => setView('register')} className="text-blue-600 font-semibold hover:underline">
//               Register
//             </button>
//           </p>
//           <div className="mt-6 p-3 bg-gray-100 rounded-lg text-xs text-gray-600">
//             <p className="font-semibold mb-1">Test credentials:</p>
//             <p>alice@example.com / password123</p>
//             <p>bob@example.com / password123</p>
//           </div>
//         </div>
//       </div>
//     );
//   }

//   // Register View
//   if (view === 'register') {
//     return (
//       <div className="min-h-screen bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center p-4">
//         <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
//           <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">Create Account</h1>
//           <form onSubmit={handleRegister} className="space-y-4">
//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
//               <input
//                 type="text"
//                 value={registerForm.username}
//                 onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
//                 required
//               />
//             </div>
//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
//               <input
//                 type="email"
//                 value={registerForm.email}
//                 onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
//                 required
//               />
//             </div>
//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
//               <input
//                 type="password"
//                 value={registerForm.password}
//                 onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
//                 required
//               />
//             </div>
//             {error && <p className="text-red-500 text-sm">{error}</p>}
//             <button
//               type="submit"
//               disabled={loading}
//               className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition disabled:opacity-50"
//             >
//               {loading ? 'Creating...' : 'Register'}
//             </button>
//           </form>
//           <p className="text-center mt-4 text-sm text-gray-600">
//             Already have an account?{' '}
//             <button onClick={() => setView('login')} className="text-purple-600 font-semibold hover:underline">
//               Login
//             </button>
//           </p>
//         </div>
//       </div>
//     );
//   }

//   // Main App View
//   return (
//     <div className="min-h-screen bg-gray-50">
//       {/* Header */}
//       <header className="bg-white shadow-md sticky top-0 z-50">
//         <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
//           <h1 className="text-2xl font-bold text-blue-600">E-Shop</h1>
//           <div className="flex items-center gap-4">
//             <button
//               onClick={() => setView('recommendations')}
//               className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg font-medium hover:bg-purple-200 transition"
//             >
//               <Star className="inline w-4 h-4 mr-1" />
//               Recommendations
//             </button>
//             <button
//               onClick={() => setView('products')}
//               className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium hover:bg-blue-200 transition"
//             >
//               Products
//             </button>
//             <div className="flex items-center gap-2 text-gray-700">
//               <User className="w-5 h-5" />
//               <span className="font-medium">{currentUser?.username}</span>
//             </div>
//             <button onClick={handleLogout} className="text-red-500 hover:text-red-700">
//               <LogOut className="w-5 h-5" />
//             </button>
//           </div>
//         </div>
//       </header>

//       <div className="max-w-7xl mx-auto px-4 py-6">
//         {/* Search and Filters */}
//         {view === 'products' && (
//           <div className="mb-6 bg-white p-4 rounded-lg shadow">
//             <div className="flex gap-4">
//               <div className="flex-1">
//                 <input
//                   type="text"
//                   value={searchTerm}
//                   onChange={(e) => setSearchTerm(e.target.value)}
//                   onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
//                   placeholder="Search products..."
//                   className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
//                 />
//               </div>
//               <select
//                 value={selectedCategory}
//                 onChange={(e) => {
//                   setSelectedCategory(e.target.value);
//                   setTimeout(handleSearch, 100);
//                 }}
//                 className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
//               >
//                 <option value="">All Categories</option>
//                 {categories.map((cat) => (
//                   <option key={cat} value={cat}>{cat}</option>
//                 ))}
//               </select>
//               <button
//                 onClick={handleSearch}
//                 className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
//               >
//                 <Search className="w-5 h-5" />
//               </button>
//             </div>
//           </div>
//         )}

//         {/* Recommendations View */}
//         {view === 'recommendations' && (
//           <div>
//             <h2 className="text-2xl font-bold mb-6 text-gray-800">Recommended for You</h2>
//             {recommendations.length === 0 ? (
//               <p className="text-gray-500">No recommendations yet. Interact with products to get personalized suggestions!</p>
//             ) : (
//               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//                 {recommendations.map((product) => (
//                   <ProductCard key={product._id} product={product} onInteract={trackInteraction} />
//                 ))}
//               </div>
//             )}
//           </div>
//         )}

//         {/* Products View */}
//         {view === 'products' && (
//           <div>
//             <h2 className="text-2xl font-bold mb-6 text-gray-800">
//               {selectedCategory || 'All Products'}
//             </h2>
//             {loading ? (
//               <p className="text-gray-500">Loading...</p>
//             ) : products.length === 0 ? (
//               <p className="text-gray-500">No products found</p>
//             ) : (
//               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
//                 {products.map((product) => (
//                   <ProductCard key={product._id} product={product} onInteract={trackInteraction} />
//                 ))}
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// function ProductCard({ product, onInteract }) {
//   const [liked, setLiked] = useState(false);
//   const [viewed, setViewed] = useState(false);

//   useEffect(() => {
//     if (!viewed) {
//       onInteract(product._id, 'view');
//       setViewed(true);
//     }
//   }, []);

//   const handleLike = () => {
//     setLiked(!liked);
//     onInteract(product._id, 'like');
//   };

//   return (
//     <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition transform hover:-translate-y-1">
//       <div className="h-48 bg-gray-200 flex items-center justify-center">
//         <img
//           src={product.image_url}
//           alt={product.name}
//           className="w-full h-full object-cover"
//         />
//       </div>
//       <div className="p-4">
//         <div className="flex justify-between items-start mb-2">
//           <h3 className="font-semibold text-gray-800 text-lg line-clamp-2">{product.name}</h3>
//           <button
//             onClick={handleLike}
//             className={`${liked ? 'text-red-500' : 'text-gray-400'} hover:text-red-500 transition`}
//           >
//             <Heart className={`w-5 h-5 ${liked ? 'fill-current' : ''}`} />
//           </button>
//         </div>
//         <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>
//         <div className="flex justify-between items-center">
//           <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">{product.category}</span>
//           <span className="text-xl font-bold text-blue-600">${product.price}</span>
//         </div>
//         {product.recommendation_score && (
//           <div className="mt-2 flex items-center gap-1 text-sm text-purple-600">
//             <Star className="w-4 h-4 fill-current" />
//             <span>Match: {(product.recommendation_score * 20).toFixed(0)}%</span>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default App;