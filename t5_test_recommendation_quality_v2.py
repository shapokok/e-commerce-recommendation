"""
Recommendation Quality Testing V2
Tests ALL users from database (not just hardcoded ones)
Provides comprehensive quality metrics
"""

import requests
import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import statistics
from pymongo import MongoClient
import sys
import io

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API_URL = "http://127.0.0.1:8000"

# MongoDB connection to get all users
MONGO_URI = (
    "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"
)
client = MongoClient(MONGO_URI)
db = client.ecommerce_db


class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    END = "\033[0m"
    BOLD = "\033[1m"


class RecommendationQualityTesterV2:
    """Test recommendation quality using ALL users"""

    def __init__(self, sample_size: int = 15):
        self.sample_size = sample_size  # Number of users to test
        self.users = []
        self.all_products = []
        self.results = {}

    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}  {title}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}\n")

    def load_test_data(self):
        """Load ALL users from database (OPTIMIZED - direct MongoDB access)"""
        self.print_header("LOADING TEST DATA FROM DATABASE")

        # Get all products directly from MongoDB (faster)
        all_products_cursor = db.products.find({})
        self.all_products = []
        for p in all_products_cursor:
            p["_id"] = str(p["_id"])
            self.all_products.append(p)
        print(f"✓ Loaded {len(self.all_products)} products")

        # Get ALL users directly from MongoDB
        all_users = list(db.users.find({}))
        print(f"✓ Found {len(all_users)} total users in database")

        # Get ALL interactions at once (MUCH faster than per-user API calls)
        print(f"✓ Loading interactions from database...")
        all_interactions = list(db.interactions.find({}))
        print(f"✓ Loaded {len(all_interactions)} total interactions")

        # Group interactions by user
        from collections import defaultdict

        user_interactions = defaultdict(list)
        for interaction in all_interactions:
            user_interactions[interaction["user_id"]].append(interaction)

        # Filter users with interactions
        users_with_interactions = []

        for user in all_users:
            user_id = str(user["_id"])
            username = user.get("username", "unknown")

            # Get interactions for this user
            interactions = user_interactions.get(user_id, [])

            if len(interactions) > 0:  # Only users with interactions
                # Extract liked and viewed products
                liked_products = set()
                viewed_products = set()

                for interaction in interactions:
                    product_id = interaction["product_id"]
                    if interaction["interaction_type"] == "like":
                        liked_products.add(product_id)
                    elif interaction["interaction_type"] in ["view", "rating"]:
                        viewed_products.add(product_id)

                users_with_interactions.append(
                    {
                        "user_id": user_id,
                        "username": username,
                        "persona": user.get("persona", "unknown"),
                        "liked_products": liked_products,
                        "viewed_products": viewed_products,
                        "all_interacted": liked_products.union(viewed_products),
                        "interaction_count": len(interactions),
                    }
                )

        print(f"✓ Found {len(users_with_interactions)} users with interactions")

        # Sample users if there are too many
        if len(users_with_interactions) > self.sample_size:
            import random

            # Stratified sampling: get users from each persona
            personas = defaultdict(list)
            for user in users_with_interactions:
                personas[user["persona"]].append(user)

            sampled_users = []
            users_per_persona = max(1, self.sample_size // len(personas))

            for persona, persona_users in personas.items():
                sample_count = min(users_per_persona, len(persona_users))
                sampled_users.extend(random.sample(persona_users, sample_count))

            # If we still need more, add randomly
            if len(sampled_users) < self.sample_size:
                remaining = [
                    u for u in users_with_interactions if u not in sampled_users
                ]
                additional = min(self.sample_size - len(sampled_users), len(remaining))
                sampled_users.extend(random.sample(remaining, additional))

            self.users = sampled_users[: self.sample_size]
            print(
                f"✓ Sampled {len(self.users)} users for testing (stratified by persona)"
            )
        else:
            self.users = users_with_interactions
            print(f"✓ Testing all {len(self.users)} users")

        # Print sample breakdown
        persona_counts = defaultdict(int)
        for user in self.users:
            persona_counts[user["persona"]] += 1

        print(f"\nTest sample breakdown by persona:")
        for persona, count in sorted(persona_counts.items()):
            print(f"  - {persona}: {count}")

        print(
            f"\nAverage interactions per test user: {statistics.mean(u['interaction_count'] for u in self.users):.1f}"
        )

    def calculate_precision_recall(
        self, recommended: Set[str], relevant: Set[str]
    ) -> Tuple[float, float, float]:
        """Calculate Precision, Recall, and F1-Score"""
        if not recommended or not relevant:
            return 0.0, 0.0, 0.0

        true_positives = len(recommended.intersection(relevant))

        precision = true_positives / len(recommended) if recommended else 0.0
        recall = true_positives / len(relevant) if relevant else 0.0

        if precision + recall > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0

        return precision, recall, f1_score

    def test_collaborative_filtering(self):
        """Test collaborative filtering recommendations"""
        self.print_header("COLLABORATIVE FILTERING QUALITY TEST")

        results = []

        for user in self.users:
            user_id = user["user_id"]
            username = user["username"]

            # Get recommendations
            rec_response = requests.get(
                f"{API_URL}/api/recommendations/{user_id}?n=10&method=collaborative"
            )

            if rec_response.status_code == 200:
                recommendations = rec_response.json()["recommendations"]
                recommended_ids = set(rec["_id"] for rec in recommendations)

                # Use ALL interacted products as ground truth
                relevant_ids = user["all_interacted"]
                liked_ids = user["liked_products"]

                # Calculate metrics
                precision, recall, f1 = self.calculate_precision_recall(
                    recommended_ids, relevant_ids
                )
                precision_liked, recall_liked, f1_liked = (
                    self.calculate_precision_recall(recommended_ids, liked_ids)
                )
                hit_rate = (
                    1.0 if len(recommended_ids.intersection(relevant_ids)) > 0 else 0.0
                )

                result = {
                    "user": username,
                    "user_id": user_id,
                    "persona": user["persona"],
                    "recommended_count": len(recommended_ids),
                    "relevant_count": len(relevant_ids),
                    "liked_count": len(liked_ids),
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "precision_liked_only": precision_liked,
                    "recall_liked_only": recall_liked,
                    "f1_score_liked_only": f1_liked,
                    "hit_rate": hit_rate,
                }

                results.append(result)

        # Calculate overall averages
        if results:
            avg_precision = statistics.mean(r["precision"] for r in results)
            avg_recall = statistics.mean(r["recall"] for r in results)
            avg_f1 = statistics.mean(r["f1_score"] for r in results)
            avg_hit_rate = statistics.mean(r["hit_rate"] for r in results)

            print(f"{Color.BOLD}COLLABORATIVE FILTERING - AVERAGE METRICS:{Color.END}")
            print(f"  Average Precision: {Color.GREEN}{avg_precision:.3f}{Color.END}")
            print(f"  Average Recall: {Color.GREEN}{avg_recall:.3f}{Color.END}")
            print(f"  Average F1-Score: {Color.GREEN}{avg_f1:.3f}{Color.END}")
            print(f"  Average Hit Rate: {Color.GREEN}{avg_hit_rate:.3f}{Color.END}")

            # Calculate by persona
            print(f"\n{Color.BOLD}Results by Persona:{Color.END}")
            persona_results = defaultdict(list)
            for r in results:
                persona_results[r["persona"]].append(r["f1_score"])

            for persona, f1_scores in sorted(persona_results.items()):
                avg_f1_persona = statistics.mean(f1_scores)
                print(f"  {persona}: {Color.CYAN}{avg_f1_persona:.3f}{Color.END}")

            self.results["collaborative_filtering"] = {
                "method": "collaborative",
                "average_precision": avg_precision,
                "average_recall": avg_recall,
                "average_f1_score": avg_f1,
                "average_hit_rate": avg_hit_rate,
                "individual_results": results,
                "persona_breakdown": {
                    persona: statistics.mean(scores)
                    for persona, scores in persona_results.items()
                },
            }

    def test_content_based(self):
        """Test content-based recommendations"""
        self.print_header("CONTENT-BASED FILTERING QUALITY TEST")

        results = []

        for user in self.users:
            user_id = user["user_id"]
            username = user["username"]

            # Get content-based recommendations
            rec_response = requests.get(
                f"{API_URL}/api/recommendations/{user_id}?n=10&method=content"
            )

            if rec_response.status_code == 200:
                recommendations = rec_response.json()["recommendations"]
                recommended_ids = set(rec["_id"] for rec in recommendations)

                relevant_ids = user["all_interacted"]
                liked_ids = user["liked_products"]

                precision, recall, f1 = self.calculate_precision_recall(
                    recommended_ids, relevant_ids
                )
                hit_rate = (
                    1.0 if len(recommended_ids.intersection(relevant_ids)) > 0 else 0.0
                )

                result = {
                    "user": username,
                    "user_id": user_id,
                    "persona": user["persona"],
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "hit_rate": hit_rate,
                }

                results.append(result)

        # Calculate averages
        if results:
            avg_precision = statistics.mean(r["precision"] for r in results)
            avg_recall = statistics.mean(r["recall"] for r in results)
            avg_f1 = statistics.mean(r["f1_score"] for r in results)
            avg_hit_rate = statistics.mean(r["hit_rate"] for r in results)

            print(f"{Color.BOLD}CONTENT-BASED - AVERAGE METRICS:{Color.END}")
            print(f"  Average Precision: {Color.GREEN}{avg_precision:.3f}{Color.END}")
            print(f"  Average Recall: {Color.GREEN}{avg_recall:.3f}{Color.END}")
            print(f"  Average F1-Score: {Color.GREEN}{avg_f1:.3f}{Color.END}")
            print(f"  Average Hit Rate: {Color.GREEN}{avg_hit_rate:.3f}{Color.END}")

            # By persona
            print(f"\n{Color.BOLD}Results by Persona:{Color.END}")
            persona_results = defaultdict(list)
            for r in results:
                persona_results[r["persona"]].append(r["f1_score"])

            for persona, f1_scores in sorted(persona_results.items()):
                avg_f1_persona = statistics.mean(f1_scores)
                print(f"  {persona}: {Color.CYAN}{avg_f1_persona:.3f}{Color.END}")

            self.results["content_based"] = {
                "method": "content",
                "average_precision": avg_precision,
                "average_recall": avg_recall,
                "average_f1_score": avg_f1,
                "average_hit_rate": avg_hit_rate,
                "individual_results": results,
            }

    def test_diversity(self):
        """Test recommendation diversity"""
        self.print_header("RECOMMENDATION DIVERSITY TEST")

        diversity_results = []

        for user in self.users:
            user_id = user["user_id"]
            username = user["username"]

            rec_response = requests.get(f"{API_URL}/api/recommendations/{user_id}?n=10")

            if rec_response.status_code == 200:
                recommendations = rec_response.json()["recommendations"]

                categories = set(rec["category"] for rec in recommendations)
                diversity_score = (
                    len(categories) / len(recommendations) if recommendations else 0
                )

                diversity_results.append(
                    {
                        "user": username,
                        "persona": user["persona"],
                        "total_recommendations": len(recommendations),
                        "unique_categories": len(categories),
                        "diversity_score": diversity_score,
                    }
                )

        if diversity_results:
            avg_diversity = statistics.mean(
                r["diversity_score"] for r in diversity_results
            )

            print(
                f"{Color.BOLD}AVERAGE DIVERSITY SCORE: {Color.GREEN}{avg_diversity:.3f}{Color.END}"
            )

            # By persona
            print(f"\n{Color.BOLD}Diversity by Persona:{Color.END}")
            persona_diversity = defaultdict(list)
            for r in diversity_results:
                persona_diversity[r["persona"]].append(r["diversity_score"])

            for persona, scores in sorted(persona_diversity.items()):
                avg_div = statistics.mean(scores)
                print(f"  {persona}: {Color.CYAN}{avg_div:.3f}{Color.END}")

            self.results["diversity"] = {
                "average_diversity": avg_diversity,
                "individual_results": diversity_results,
            }

    def test_coverage(self):
        """Test catalog coverage"""
        self.print_header("CATALOG COVERAGE TEST")

        all_recommended = set()

        for user in self.users:
            user_id = user["user_id"]

            rec_response = requests.get(f"{API_URL}/api/recommendations/{user_id}?n=10")

            if rec_response.status_code == 200:
                recommendations = rec_response.json()["recommendations"]
                all_recommended.update(rec["_id"] for rec in recommendations)

        coverage = (
            len(all_recommended) / len(self.all_products) if self.all_products else 0
        )

        print(f"Total products in catalog: {len(self.all_products)}")
        print(f"Products recommended to at least one user: {len(all_recommended)}")
        print(f"{Color.BOLD}Catalog Coverage: {Color.GREEN}{coverage:.1%}{Color.END}")

        self.results["coverage"] = {
            "total_products": len(self.all_products),
            "recommended_products": len(all_recommended),
            "coverage_percentage": coverage * 100,
        }

    def generate_report(self):
        """Generate comprehensive quality report"""
        self.print_header("RECOMMENDATION QUALITY SUMMARY")

        # Overall assessment
        if "collaborative_filtering" in self.results:
            cf_f1 = self.results["collaborative_filtering"]["average_f1_score"]
            print(
                f"Collaborative Filtering F1-Score: {Color.GREEN}{cf_f1:.3f}{Color.END}"
            )

        if "content_based" in self.results:
            cb_f1 = self.results["content_based"]["average_f1_score"]
            print(f"Content-Based F1-Score: {Color.GREEN}{cb_f1:.3f}{Color.END}")

        if "diversity" in self.results:
            diversity = self.results["diversity"]["average_diversity"]
            print(f"Average Diversity: {Color.GREEN}{diversity:.3f}{Color.END}")

        if "coverage" in self.results:
            coverage = self.results["coverage"]["coverage_percentage"]
            print(f"Catalog Coverage: {Color.GREEN}{coverage:.1f}%{Color.END}")

        # Recommendations
        print(f"\n{Color.BOLD}ASSESSMENT:{Color.END}")

        if "collaborative_filtering" in self.results:
            cf_f1 = self.results["collaborative_filtering"]["average_f1_score"]
            if cf_f1 >= 0.60:
                print(
                    f"  {Color.GREEN}✅ EXCELLENT F1-Score: {cf_f1:.3f} (Target: 0.60+){Color.END}"
                )
            elif cf_f1 >= 0.50:
                print(
                    f"  {Color.YELLOW}✓ Good F1-Score: {cf_f1:.3f} (Close to target){Color.END}"
                )
            else:
                print(
                    f"  {Color.YELLOW}• F1-Score: {cf_f1:.3f} (Target: 0.60+){Color.END}"
                )

        if "diversity" in self.results:
            diversity = self.results["diversity"]["average_diversity"]
            if diversity >= 0.60:
                print(
                    f"  {Color.GREEN}✅ EXCELLENT Diversity: {diversity:.3f}{Color.END}"
                )
            else:
                print(f"  {Color.YELLOW}• Diversity could be improved{Color.END}")

        if "coverage" in self.results:
            coverage = self.results["coverage"]["coverage_percentage"]
            if coverage >= 70:
                print(
                    f"  {Color.GREEN}✅ EXCELLENT Coverage: {coverage:.1f}%{Color.END}"
                )
            elif coverage >= 50:
                print(f"  {Color.YELLOW}✓ Good Coverage: {coverage:.1f}%{Color.END}")
            else:
                print(f"  {Color.YELLOW}• Coverage could be improved{Color.END}")

    def save_results(self, filename: str = "recommendation_quality_results_v2.json"):
        """Save detailed results to file"""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n{Color.GREEN}Results saved to {filename}{Color.END}")


def main():
    """Run recommendation quality tests"""
    print(f"{Color.BOLD}{Color.BLUE}")
    print("=" * 70)
    print("  RECOMMENDATION QUALITY TESTING V2")
    print("  (Testing ALL Users from Database)")
    print("=" * 70)
    print(f"{Color.END}")
    print(f"API Endpoint: {API_URL}\n")

    tester = RecommendationQualityTesterV2(sample_size=15)

    # Load data
    tester.load_test_data()

    # Run tests
    tester.test_collaborative_filtering()
    tester.test_content_based()
    tester.test_diversity()
    tester.test_coverage()

    # Generate report
    tester.generate_report()

    # Save results
    tester.save_results()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Testing interrupted by user{Color.END}")
    except Exception as e:
        print(f"\n{Color.RED}Error during testing: {e}{Color.END}")
        import traceback

        traceback.print_exc()
