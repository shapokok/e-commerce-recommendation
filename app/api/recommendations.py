"""
BALANCED Recommendation System
Goals:
- F1-Score: 55-70% (HIGH ACCURACY)
- Diversity: 50-70% (HIGH DIVERSITY)
- Coverage: 60%+ (GOOD COVERAGE)

Key Strategy: MMR (Maximal Marginal Relevance) for diversity
"""

from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import List, Dict
from collections import Counter, defaultdict
from datetime import datetime

# Import shared MongoDB connection from database module
from app.database import db
print("[OPTIMIZATION] recommendation_routes using shared MongoDB connection pool")

router = APIRouter()


# ==================== CONFIGURATION ====================

CONFIG = {
    # Interaction weights (higher = more important)
    "weights": {
        "like": 12.0,  # INCREASED from 5.0
        "rating": 6.0,  # INCREASED from 3.0
        "view": 1.0,
    },
    # Recency decay
    "recency": {
        "days_0_7": 2.0,  # Last week: +100%
        "days_8_30": 1.5,  # Last month: +50%
        "days_31_90": 1.0,  # Last 3 months: normal
        "days_90_plus": 0.5,  # Older: -50%
    },
    # Diversity control
    "diversity": {
        "enabled": True,
        "lambda": 0.7,  # 0.7 = 70% relevance, 30% diversity
        "max_per_category": 3,  # Max 3 items from same category
    },
    # User similarity
    "similarity": {
        "min_threshold": 0.15,  # Minimum 15% overlap
        "top_k_users": 25,  # Consider top 25 similar users
    },
}


# ==================== HELPER FUNCTIONS ====================


def calculate_interaction_score(interaction: Dict) -> float:
    """Calculate weighted score for an interaction"""

    interaction_type = interaction.get("interaction_type", "view")
    base_weight = CONFIG["weights"].get(interaction_type, 1.0)

    # Recency boost
    timestamp = interaction.get("timestamp")
    recency_multiplier = 1.0

    if timestamp:
        age_days = (datetime.utcnow() - timestamp).days

        if age_days <= 7:
            recency_multiplier = CONFIG["recency"]["days_0_7"]
        elif age_days <= 30:
            recency_multiplier = CONFIG["recency"]["days_8_30"]
        elif age_days <= 90:
            recency_multiplier = CONFIG["recency"]["days_31_90"]
        else:
            recency_multiplier = CONFIG["recency"]["days_90_plus"]

    return base_weight * recency_multiplier


def calculate_jaccard_similarity(set1: set, set2: set) -> float:
    """Jaccard similarity coefficient"""
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def diversify_recommendations(
    candidates: List[Dict], max_results: int, lambda_param: float = 0.6
) -> List[Dict]:
    """
    Apply Maximal Marginal Relevance (MMR) for diversity

    MMR = λ * Relevance - (1-λ) * Similarity to already selected

    lambda_param:
    - 1.0 = Only relevance (no diversity)
    - 0.5 = Equal balance
    - 0.0 = Only diversity (no relevance)
    """

    if not CONFIG["diversity"]["enabled"]:
        return candidates[:max_results]

    if len(candidates) <= max_results:
        return candidates

    selected = []
    remaining = candidates.copy()
    category_counts = Counter()
    max_per_category = CONFIG["diversity"]["max_per_category"]

    # First, add the highest scoring item
    if remaining:
        best = remaining.pop(0)
        selected.append(best)
        category_counts[best.get("category")] += 1

    # Iteratively select items that balance relevance and diversity
    while len(selected) < max_results and remaining:
        best_score = -float("inf")
        best_idx = 0

        for idx, candidate in enumerate(remaining):
            category = candidate.get("category")

            # Hard limit on category repetition
            if category_counts[category] >= max_per_category:
                continue

            # Relevance score (normalized)
            relevance = candidate.get("recommendation_score", 0)
            max_relevance = candidates[0].get("recommendation_score", 1)
            normalized_relevance = relevance / max_relevance if max_relevance > 0 else 0

            # Diversity penalty (how similar to already selected items)
            diversity_penalty = 0
            for selected_item in selected:
                if selected_item.get("category") == category:
                    diversity_penalty += 0.5  # Same category penalty

            # Normalize diversity penalty
            max_penalty = len(selected) * 0.5
            normalized_penalty = (
                diversity_penalty / max_penalty if max_penalty > 0 else 0
            )

            # MMR score
            mmr_score = (lambda_param * normalized_relevance) - (
                (1 - lambda_param) * normalized_penalty
            )

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        # Add best item
        if remaining:
            selected_item = remaining.pop(best_idx)
            selected.append(selected_item)
            category_counts[selected_item.get("category")] += 1

    return selected


# ==================== CONTENT-BASED (OPTIMIZED) ====================


def get_content_based_recommendations_balanced(user_id: str, n: int = 10) -> List[Dict]:
    """Optimized content-based with diversity"""

    try:
        # Get user interactions (with projection for less data transfer)
        interactions = list(
            db.interactions.find(
                {"user_id": user_id}, {"product_id": 1, "interaction_type": 1, "timestamp": 1}
            )
        )

        if not interactions:
            return get_popular_products(n)

        # Get unique product IDs
        product_ids = list(set(i["product_id"] for i in interactions))

        # Fetch all products at once instead of one by one
        products_map = {}
        products = db.products.find(
            {"_id": {"$in": [ObjectId(pid) for pid in product_ids]}},
            {"category": 1, "price": 1}
        )
        for product in products:
            products_map[str(product["_id"])] = product

        # Calculate weighted category preferences
        category_scores = defaultdict(float)
        price_list = []
        interacted_product_ids = set()

        for interaction in interactions:
            product_id = interaction["product_id"]
            interacted_product_ids.add(product_id)

            product = products_map.get(product_id)
            if not product:
                continue

            category = product.get("category", "Unknown")
            price = product.get("price", 0)

            score = calculate_interaction_score(interaction)
            category_scores[category] += score
            price_list.append(price)

        # Get top categories (top 60% by weight)
        total_weight = sum(category_scores.values())
        sorted_categories = sorted(
            category_scores.items(), key=lambda x: x[1], reverse=True
        )

        cumulative_weight = 0
        favorite_cats = []
        for cat, weight in sorted_categories:
            favorite_cats.append(cat)
            cumulative_weight += weight
            if cumulative_weight >= total_weight * 0.6:  # Top 60% of weight
                break

        # Ensure at least 2 categories for diversity
        if len(favorite_cats) < 2 and len(sorted_categories) >= 2:
            favorite_cats = [cat for cat, _ in sorted_categories[:2]]

        print(f"Content-based for {user_id}: Using categories {favorite_cats}")

        # Calculate average price
        avg_price = sum(price_list) / len(price_list) if price_list else 0

        # Get candidate products
        candidates = list(db.products.find({"category": {"$in": favorite_cats}}))

        # Score each candidate
        scored_products = []
        for product in candidates:
            product_id = str(product["_id"])
            category = product.get("category", "Unknown")
            price = product.get("price", 0)

            # Category score
            category_score = category_scores.get(category, 0)

            # Price similarity (within ±40% is good)
            if avg_price > 0:
                price_diff = abs(price - avg_price) / avg_price
                price_score = max(
                    0, 1 - price_diff / 0.4
                )  # Linear decay, 0 at 40% diff
            else:
                price_score = 0.5

            # Composite score: 75% category, 25% price
            final_score = (category_score * 0.75) + (
                price_score * category_score * 0.25
            )

            product["_id"] = str(product["_id"])
            product["recommendation_score"] = final_score
            scored_products.append(product)

        # Sort by score
        scored_products.sort(key=lambda x: x["recommendation_score"], reverse=True)

        # Apply diversity (get more candidates, then diversify)
        diversified = diversify_recommendations(
            scored_products[: n * 3],  # Get 3x candidates
            n,
            lambda_param=CONFIG["diversity"]["lambda"],
        )

        return diversified

    except Exception as e:
        print(f"ERROR in content-based: {e}")
        import traceback

        traceback.print_exc()
        return get_popular_products(n)


# ==================== COLLABORATIVE (OPTIMIZED) ====================


def get_collaborative_recommendations_balanced(user_id: str, n: int = 10) -> List[Dict]:
    """Optimized collaborative filtering with diversity"""

    try:
        # Get user's interactions (with projection to reduce data transfer)
        my_interactions = list(
            db.interactions.find(
                {"user_id": user_id}, {"product_id": 1, "interaction_type": 1, "timestamp": 1}
            )
        )

        if not my_interactions:
            return get_popular_products(n)

        # Calculate user's product preferences
        my_product_scores = {}
        my_product_ids = set()

        for interaction in my_interactions:
            product_id = interaction["product_id"]
            my_product_ids.add(product_id)
            score = calculate_interaction_score(interaction)
            my_product_scores[product_id] = my_product_scores.get(product_id, 0) + score

        # Use aggregation pipeline to find similar users efficiently
        # Get all users who interacted with the same products
        pipeline = [
            {"$match": {"product_id": {"$in": list(my_product_ids)}, "user_id": {"$ne": user_id}}},
            {"$group": {
                "_id": "$user_id",
                "interactions": {"$push": {
                    "product_id": "$product_id",
                    "interaction_type": "$interaction_type",
                    "timestamp": "$timestamp"
                }}
            }},
            {"$limit": 100}  # Limit to top 100 users for performance
        ]

        potential_similar_users = list(db.interactions.aggregate(pipeline))
        user_similarities = []

        for user_doc in potential_similar_users:
            other_user_id = user_doc["_id"]
            their_interactions = user_doc["interactions"]
            their_product_ids = set(i["product_id"] for i in their_interactions)

            if not their_product_ids:
                continue

            # Calculate similarity
            similarity = calculate_jaccard_similarity(my_product_ids, their_product_ids)

            if similarity >= CONFIG["similarity"]["min_threshold"]:
                user_similarities.append(
                    {
                        "user_id": other_user_id,
                        "similarity": similarity,
                        "interactions": their_interactions,
                    }
                )

        # Sort by similarity
        user_similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_similar_users = user_similarities[: CONFIG["similarity"]["top_k_users"]]

        print(
            f"Collaborative for {user_id}: Found {len(top_similar_users)} similar users"
        )

        if not top_similar_users:
            return get_content_based_recommendations_balanced(user_id, n)

        # Aggregate recommendations from similar users
        product_scores = defaultdict(float)

        for similar_user in top_similar_users:
            similarity = similar_user["similarity"]

            for interaction in similar_user["interactions"]:
                product_id = interaction["product_id"]

                # Skip if user already interacted
                # if product_id in my_product_ids:
                #     continue

                interaction_score = calculate_interaction_score(interaction)
                product_scores[product_id] += interaction_score * similarity

        # Fetch and score products
        scored_products = []
        for product_id, score in product_scores.items():
            try:
                product = db.products.find_one({"_id": ObjectId(product_id)})
                if product:
                    product["_id"] = str(product["_id"])
                    product["recommendation_score"] = score
                    scored_products.append(product)
            except:
                continue

        # Sort by score
        scored_products.sort(key=lambda x: x["recommendation_score"], reverse=True)

        # Apply diversity
        diversified = diversify_recommendations(
            scored_products[: n * 3], n, lambda_param=CONFIG["diversity"]["lambda"]
        )

        return diversified

    except Exception as e:
        print(f"ERROR in collaborative: {e}")
        import traceback

        traceback.print_exc()
        return get_popular_products(n)


# ==================== HYBRID (OPTIMIZED) ====================


def get_hybrid_recommendations_balanced(user_id: str, n: int = 10) -> List[Dict]:
    """Smart hybrid with diversity preservation"""

    try:
        # Get recommendations from both methods
        interaction_count = db.interactions.count_documents({"user_id": user_id})

        if interaction_count == 0:
            return get_popular_products(n)
        elif interaction_count < 5:
            # Few interactions: 70% content, 30% collaborative
            content = get_content_based_recommendations_balanced(user_id, n)
            collab = get_collaborative_recommendations_balanced(user_id, n)
            content_weight = 0.7
        elif interaction_count < 15:
            # Medium: 50/50
            content = get_content_based_recommendations_balanced(user_id, n)
            collab = get_collaborative_recommendations_balanced(user_id, n)
            content_weight = 0.5
        else:
            # Many: 30% content, 70% collaborative
            content = get_content_based_recommendations_balanced(user_id, n)
            collab = get_collaborative_recommendations_balanced(user_id, n)
            content_weight = 0.3

        # Merge with weighted scoring
        all_products = {}

        for product in content:
            pid = product["_id"]
            all_products[pid] = product.copy()
            all_products[pid]["recommendation_score"] = (
                product["recommendation_score"] * content_weight
            )

        for product in collab:
            pid = product["_id"]
            if pid in all_products:
                # Combine scores
                all_products[pid]["recommendation_score"] += product[
                    "recommendation_score"
                ] * (1 - content_weight)
            else:
                all_products[pid] = product.copy()
                all_products[pid]["recommendation_score"] = product[
                    "recommendation_score"
                ] * (1 - content_weight)

        # Sort by combined score
        merged = list(all_products.values())
        merged.sort(key=lambda x: x["recommendation_score"], reverse=True)

        # Apply final diversity pass
        result = diversify_recommendations(merged, n, lambda_param=0.65)

        return result

    except Exception as e:
        print(f"ERROR in hybrid: {e}")
        return get_popular_products(n)


# ==================== POPULAR PRODUCTS ====================


def get_popular_products(n: int = 10) -> List[Dict]:
    """Get diverse popular products using aggregation for better performance"""

    try:
        # Use aggregation pipeline to calculate scores efficiently
        pipeline = [
            {
                "$group": {
                    "_id": "$product_id",
                    "interactions": {"$push": {
                        "interaction_type": "$interaction_type",
                        "timestamp": "$timestamp"
                    }}
                }
            },
            {"$limit": 100}  # Limit for performance
        ]

        interaction_groups = list(db.interactions.aggregate(pipeline))

        product_scores = {}
        for group in interaction_groups:
            product_id = group["_id"]
            total_score = 0
            for interaction in group["interactions"]:
                score = calculate_interaction_score(interaction)
                total_score += score
            product_scores[product_id] = total_score

        # Sort by score and get top product IDs
        top_product_ids = sorted(
            product_scores.items(), key=lambda x: x[1], reverse=True
        )[:n * 3]  # Get 3x for diversity filtering

        # Fetch all top products in one query
        product_id_list = [pid for pid, score in top_product_ids]
        products_cursor = db.products.find(
            {"_id": {"$in": [ObjectId(pid) for pid in product_id_list]}}
        )

        # Build products list with scores
        products = []
        for product in products_cursor:
            product_id = str(product["_id"])
            product["_id"] = product_id
            product["recommendation_score"] = product_scores.get(product_id, 0)
            products.append(product)

        # Sort by score
        products.sort(key=lambda x: x["recommendation_score"], reverse=True)

        # Apply diversity
        diversified = diversify_recommendations(products, n, lambda_param=0.5)

        # Fill with random if needed
        if len(diversified) < n:
            existing_ids = set(p["_id"] for p in diversified)
            random_products = list(
                db.products.find(
                    {"_id": {"$nin": [ObjectId(pid) for pid in existing_ids]}}
                ).limit(n - len(diversified))
            )

            for product in random_products:
                product["_id"] = str(product["_id"])
                product["recommendation_score"] = 0
                diversified.append(product)

        return diversified[:n]

    except:
        products = list(db.products.find().limit(n))
        for product in products:
            product["_id"] = str(product["_id"])
            product["recommendation_score"] = 0
        return products


# ==================== API ENDPOINTS ====================


@router.get("/api/recommendations/popular")
def get_popular_products_endpoint(n: int = Query(10, ge=1, le=50)):
    """Get popular products based on user interactions"""

    try:
        popular_products = get_popular_products(n)

        return {
            "method": "popular",
            "count": len(popular_products),
            "products": popular_products,
        }

    except Exception as e:
        print(f"ERROR in popular products: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/recommendations/{user_id}")
def get_recommendations(
    user_id: str,
    n: int = Query(10, ge=1, le=50),
    method: str = Query("hybrid", regex="^(collaborative|content|hybrid)$"),
):
    """Get balanced recommendations (high accuracy + high diversity)"""

    try:
        # Validate ObjectId format first
        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=404, detail="User not found")

        user = db.users.find_one({"_id": user_object_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if method == "collaborative":
            recommendations = get_collaborative_recommendations_balanced(user_id, n)
        elif method == "content":
            recommendations = get_content_based_recommendations_balanced(user_id, n)
        else:
            recommendations = get_hybrid_recommendations_balanced(user_id, n)

        return {
            "user_id": user_id,
            "username": user.get("username", "unknown"),
            "method": method,
            "count": len(recommendations),
            "recommendations": recommendations,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

