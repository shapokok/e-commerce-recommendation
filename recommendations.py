from pymongo import MongoClient
from bson import ObjectId
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

MONGO_URI = "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.ecommerce_db

users_collection = db.users
products_collection = db.products
interactions_collection = db.interactions

class RecommendationEngine:
    """
    User-based Collaborative Filtering Recommendation Engine
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity = None
        self.user_ids = []
        self.product_ids = []
    
    def build_user_item_matrix(self):
        """Build user-item interaction matrix"""
        # Get all interactions
        interactions = list(interactions_collection.find())
        
        if not interactions:
            return None
        
        # Create mapping of users and products to indices
        user_set = set()
        product_set = set()
        
        for interaction in interactions:
            user_set.add(interaction['user_id'])
            product_set.add(interaction['product_id'])
        
        self.user_ids = list(user_set)
        self.product_ids = list(product_set)
        
        user_to_idx = {user_id: idx for idx, user_id in enumerate(self.user_ids)}
        product_to_idx = {product_id: idx for idx, product_id in enumerate(self.product_ids)}
        
        # Initialize matrix with zeros
        matrix = np.zeros((len(self.user_ids), len(self.product_ids)))
        
        # Fill matrix with interaction scores
        for interaction in interactions:
            user_idx = user_to_idx[interaction['user_id']]
            product_idx = product_to_idx[interaction['product_id']]
            
            # Score based on interaction type
            if interaction['interaction_type'] == 'rating' and interaction['rating']:
                score = interaction['rating']
            elif interaction['interaction_type'] == 'like':
                score = 4
            elif interaction['interaction_type'] == 'view':
                score = 1
            else:
                score = 1
            
            # If multiple interactions, take max
            matrix[user_idx][product_idx] = max(matrix[user_idx][product_idx], score)
        
        self.user_item_matrix = matrix
        return matrix
    
    def calculate_user_similarity(self):
        """Calculate cosine similarity between users"""
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        
        if self.user_item_matrix is None:
            return None
        
        # Cosine similarity
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        return self.user_similarity
    
    def get_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Dict]:
        """
        Get product recommendations for a user using collaborative filtering
        """
        # Build matrix if not exists
        if self.user_item_matrix is None:
            self.build_user_item_matrix()
        
        if self.user_item_matrix is None:
            # No interactions yet, return popular products
            return self.get_popular_products(n_recommendations)
        
        # Check if user exists in matrix
        if user_id not in self.user_ids:
            # New user, return popular products
            return self.get_popular_products(n_recommendations)
        
        # Calculate similarity if not exists
        if self.user_similarity is None:
            self.calculate_user_similarity()
        
        user_idx = self.user_ids.index(user_id)
        
        # Get similar users
        user_similarities = self.user_similarity[user_idx]
        
        # Get products user has already interacted with
        user_interacted = set()
        user_interactions = interactions_collection.find({"user_id": user_id})
        for interaction in user_interactions:
            user_interacted.add(interaction['product_id'])
        
        # Calculate predicted ratings for each product
        product_scores = defaultdict(float)
        product_similarity_sums = defaultdict(float)
        
        for other_user_idx, similarity in enumerate(user_similarities):
            if other_user_idx == user_idx or similarity <= 0:
                continue
            
            other_user_id = self.user_ids[other_user_idx]
            
            # Get products the similar user interacted with
            for product_idx, rating in enumerate(self.user_item_matrix[other_user_idx]):
                if rating > 0:
                    product_id = self.product_ids[product_idx]
                    
                    # Skip if user already interacted
                    if product_id in user_interacted:
                        continue
                    
                    product_scores[product_id] += similarity * rating
                    product_similarity_sums[product_id] += similarity
        
        # Normalize scores
        recommendations = []
        for product_id, score_sum in product_scores.items():
            if product_similarity_sums[product_id] > 0:
                normalized_score = score_sum / product_similarity_sums[product_id]
                recommendations.append((product_id, normalized_score))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations
        top_recommendations = recommendations[:n_recommendations]
        
        # Get product details
        result = []
        for product_id, score in top_recommendations:
            try:
                product = products_collection.find_one({"_id": ObjectId(product_id)})
                if product:
                    product["_id"] = str(product["_id"])
                    product["recommendation_score"] = float(score)
                    result.append(product)
            except:
                continue
        
        # If not enough recommendations, fill with popular products
        if len(result) < n_recommendations:
            popular = self.get_popular_products(n_recommendations - len(result))
            result.extend([p for p in popular if p['_id'] not in [r['_id'] for r in result]])
        
        return result
    
    def get_popular_products(self, n: int = 10) -> List[Dict]:
        """Get most popular products based on interactions"""
        # Count interactions per product
        pipeline = [
            {
                "$group": {
                    "_id": "$product_id",
                    "interaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"interaction_count": -1}},
            {"$limit": n}
        ]
        
        popular_product_ids = list(interactions_collection.aggregate(pipeline))
        
        if not popular_product_ids:
            # No interactions, return random products
            products = list(products_collection.find().limit(n))
        else:
            # Get product details
            product_ids = [ObjectId(item["_id"]) for item in popular_product_ids]
            products = list(products_collection.find({"_id": {"$in": product_ids}}))
        
        for product in products:
            product["_id"] = str(product["_id"])
        
        return products
    
    def get_content_based_recommendations(self, user_id: str, n: int = 10) -> List[Dict]:
        """
        Get recommendations based on user's category preferences
        """
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user or not user.get('preferences'):
            return self.get_popular_products(n)
        
        # Get products from preferred categories
        products = list(products_collection.find({
            "category": {"$in": user['preferences']}
        }).limit(n))
        
        # Get user's interacted products
        user_interacted = set()
        user_interactions = interactions_collection.find({"user_id": user_id})
        for interaction in user_interactions:
            user_interacted.add(interaction['product_id'])
        
        # Filter out already interacted products
        result = []
        for product in products:
            if str(product["_id"]) not in user_interacted:
                product["_id"] = str(product["_id"])
                result.append(product)
        
        return result

# Global recommendation engine instance
recommendation_engine = RecommendationEngine()