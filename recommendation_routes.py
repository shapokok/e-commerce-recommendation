from fastapi import APIRouter, HTTPException
from recommendations import recommendation_engine

router = APIRouter()

@router.get("/api/recommendations/{user_id}")
def get_user_recommendations(user_id: str, n: int = 10, method: str = "collaborative"):
    """
    Get personalized recommendations for a user
    
    Parameters:
    - user_id: User ID
    - n: Number of recommendations (default: 10)
    - method: "collaborative" or "content" (default: collaborative)
    """
    try:
        if method == "collaborative":
            recommendations = recommendation_engine.get_recommendations(user_id, n)
        elif method == "content":
            recommendations = recommendation_engine.get_content_based_recommendations(user_id, n)
        else:
            raise HTTPException(status_code=400, detail="Invalid method. Use 'collaborative' or 'content'")
        
        return {
            "user_id": user_id,
            "method": method,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/recommendations/popular")
def get_popular_recommendations(n: int = 10):
    """
    Get popular products based on overall interactions
    """
    try:
        popular = recommendation_engine.get_popular_products(n)
        return {
            "recommendations": popular,
            "count": len(popular)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/recommendations/rebuild")
def rebuild_recommendation_model():
    """
    Rebuild the recommendation model (user-item matrix and similarities)
    This should be called periodically or after significant data changes
    """
    try:
        recommendation_engine.build_user_item_matrix()
        recommendation_engine.calculate_user_similarity()
        
        return {
            "message": "Recommendation model rebuilt successfully",
            "users": len(recommendation_engine.user_ids),
            "products": len(recommendation_engine.product_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))