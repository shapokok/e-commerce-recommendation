"""
Recommendation Quality Testing
Evaluates recommendation system using Precision, Recall, and F1-Score metrics
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


class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


class RecommendationQualityTester:
    """Test recommendation quality using standard metrics"""

    def __init__(self):
        self.users = []
        self.all_products = []
        self.user_interactions = {}
        self.results = {}
        self.client = MongoClient(
            "mongodb+srv://db:IpWdsbFWTop14L60@cluster0.zjhgztm.mongodb.net/?appName=Cluster0"
        )
        self.db = self.client["ecommerce_db"]

    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}  {title}{Color.END}")
        print(f"{Color.BOLD}{Color.BLUE}{'='*70}{Color.END}\n")

    def load_test_data(self):
        """Load users and their interaction history"""
        self.print_header("LOADING TEST DATA")

        # Get all products
        response = requests.get(f"{API_URL}/api/products")
        if response.status_code == 200:
            self.all_products = response.json()["products"]
            print(f"✓ Loaded {len(self.all_products)} products")

        # Login test users and get their history
        test_users = [
            {"email": "alice@example.com", "password": "password123"},
            {"email": "bob@example.com", "password": "password123"},
            {"email": "charlie@example.com", "password": "password123"},
            {"email": "diana@example.com", "password": "password123"},
        ]

        for credentials in test_users:
            login_response = requests.post(f"{API_URL}/api/login", json=credentials)
            if login_response.status_code == 200:
                user_data = login_response.json()
                user_id = user_data["user_id"]
                username = user_data["username"]

                # Get user history
                history_response = requests.get(
                    f"{API_URL}/api/users/{user_id}/history"
                )
                if history_response.status_code == 200:
                    history = history_response.json()["history"]

                    # Extract liked and viewed products
                    liked_products = set()
                    viewed_products = set()

                    for interaction in history:
                        product_id = interaction["product"]["_id"]
                        if interaction["interaction_type"] == "like":
                            liked_products.add(product_id)
                        elif interaction["interaction_type"] in ["view", "rating"]:
                            viewed_products.add(product_id)

                    self.users.append(
                        {
                            "user_id": user_id,
                            "username": username,
                            "liked_products": liked_products,
                            "viewed_products": viewed_products,
                            "all_interacted": liked_products.union(viewed_products),
                        }
                    )

                    print(
                        f"✓ Loaded user: {username} ({len(liked_products)} likes, {len(viewed_products)} views)"
                    )

        print(f"\nTotal users loaded: {len(self.users)}")

    def calculate_precision_recall(
        self, recommended: Set[str], relevant: Set[str]
    ) -> Tuple[float, float, float]:
        """
        Calculate Precision, Recall, and F1-Score

        Precision = True Positives / (True Positives + False Positives)
        Recall = True Positives / (True Positives + False Negatives)
        F1 = 2 * (Precision * Recall) / (Precision + Recall)
        """
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

                # Calculate metrics using all interactions as ground truth
                precision, recall, f1 = self.calculate_precision_recall(
                    recommended_ids, relevant_ids
                )

                # Also calculate based on liked products only (stricter metric)
                precision_liked, recall_liked, f1_liked = (
                    self.calculate_precision_recall(recommended_ids, liked_ids)
                )

                # Calculate "hit rate" - at least one relevant item in recommendations
                hit_rate = (
                    1.0 if len(recommended_ids.intersection(relevant_ids)) > 0 else 0.0
                )

                result = {
                    "user": username,
                    "user_id": user_id,
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

                # Print individual results
                print(f"\n{username}:")
                print(f"  Recommended: {len(recommended_ids)} products")
                print(f"  Relevant (all interactions): {len(relevant_ids)} products")
                print(f"  Liked products: {len(liked_ids)} products")
                print(f"  Precision: {precision:.3f}")
                print(f"  Recall: {recall:.3f}")
                print(f"  F1-Score: {f1:.3f}")
                print(f"  Precision (liked only): {precision_liked:.3f}")
                print(f"  Recall (liked only): {recall_liked:.3f}")
                print(f"  F1-Score (liked only): {f1_liked:.3f}")
                print(f"  Hit Rate: {hit_rate:.3f}")

        # Calculate averages
        if results:
            avg_precision = statistics.mean(r["precision"] for r in results)
            avg_recall = statistics.mean(r["recall"] for r in results)
            avg_f1 = statistics.mean(r["f1_score"] for r in results)
            avg_hit_rate = statistics.mean(r["hit_rate"] for r in results)
            avg_precision_liked = statistics.mean(
                r["precision_liked_only"] for r in results
            )
            avg_recall_liked = statistics.mean(r["recall_liked_only"] for r in results)
            avg_f1_liked = statistics.mean(r["f1_score_liked_only"] for r in results)

            print(
                f"\n{Color.BOLD}COLLABORATIVE FILTERING - AVERAGE METRICS:{Color.END}"
            )
            print(f"  Average Precision: {Color.GREEN}{avg_precision:.3f}{Color.END}")
            print(f"  Average Recall: {Color.GREEN}{avg_recall:.3f}{Color.END}")
            print(f"  Average F1-Score: {Color.GREEN}{avg_f1:.3f}{Color.END}")
            print(f"  Average Hit Rate: {Color.GREEN}{avg_hit_rate:.3f}{Color.END}")
            print(f"\n  (Based on liked products only):")
            print(
                f"  Average Precision (liked): {Color.YELLOW}{avg_precision_liked:.3f}{Color.END}"
            )
            print(
                f"  Average Recall (liked): {Color.YELLOW}{avg_recall_liked:.3f}{Color.END}"
            )
            print(
                f"  Average F1-Score (liked): {Color.YELLOW}{avg_f1_liked:.3f}{Color.END}"
            )

            self.results["collaborative_filtering"] = {
                "method": "collaborative",
                "average_precision": avg_precision,
                "average_recall": avg_recall,
                "average_f1_score": avg_f1,
                "average_hit_rate": avg_hit_rate,
                "average_precision_liked": avg_precision_liked,
                "average_recall_liked": avg_recall_liked,
                "average_f1_liked": avg_f1_liked,
                "individual_results": results,
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

                print(f"\n{username}:")
                print(f"  Recommended: {len(recommended_ids)} products")
                print(f"  Relevant (all interactions): {len(relevant_ids)} products")
                print(f"  Liked products: {len(liked_ids)} products")
                print(f"  Precision: {precision:.3f}")
                print(f"  Recall: {recall:.3f}")
                print(f"  F1-Score: {f1:.3f}")
                print(f"  Hit Rate: {hit_rate:.3f}")

        # Calculate averages
        if results:
            avg_precision = statistics.mean(r["precision"] for r in results)
            avg_recall = statistics.mean(r["recall"] for r in results)
            avg_f1 = statistics.mean(r["f1_score"] for r in results)
            avg_hit_rate = statistics.mean(r["hit_rate"] for r in results)

            print(f"\n{Color.BOLD}CONTENT-BASED - AVERAGE METRICS:{Color.END}")
            print(f"  Average Precision: {Color.GREEN}{avg_precision:.3f}{Color.END}")
            print(f"  Average Recall: {Color.GREEN}{avg_recall:.3f}{Color.END}")
            print(f"  Average F1-Score: {Color.GREEN}{avg_f1:.3f}{Color.END}")
            print(f"  Average Hit Rate: {Color.GREEN}{avg_hit_rate:.3f}{Color.END}")

            self.results["content_based"] = {
                "method": "content",
                "average_precision": avg_precision,
                "average_recall": avg_recall,
                "average_f1_score": avg_f1,
                "average_hit_rate": avg_hit_rate,
                "individual_results": results,
            }

    def test_diversity(self):
        """Test recommendation diversity (different categories)"""
        self.print_header("RECOMMENDATION DIVERSITY TEST")

        diversity_results = []

        for user in self.users:
            user_id = user["user_id"]
            username = user["username"]

            # Get recommendations
            rec_response = requests.get(f"{API_URL}/api/recommendations/{user_id}?n=10")

            if rec_response.status_code == 200:
                recommendations = rec_response.json()["recommendations"]

                # Count unique categories
                categories = set(rec["category"] for rec in recommendations)
                diversity_score = (
                    len(categories) / len(recommendations) if recommendations else 0
                )

                diversity_results.append(
                    {
                        "user": username,
                        "total_recommendations": len(recommendations),
                        "unique_categories": len(categories),
                        "diversity_score": diversity_score,
                    }
                )

                print(f"\n{username}:")
                print(f"  Total recommendations: {len(recommendations)}")
                print(f"  Unique categories: {len(categories)}")
                print(f"  Diversity score: {diversity_score:.3f}")

        if diversity_results:
            avg_diversity = statistics.mean(
                r["diversity_score"] for r in diversity_results
            )

            print(
                f"\n{Color.BOLD}AVERAGE DIVERSITY SCORE: {Color.GREEN}{avg_diversity:.3f}{Color.END}"
            )

            self.results["diversity"] = {
                "average_diversity": avg_diversity,
                "individual_results": diversity_results,
            }

    def test_coverage(self):
        """Test catalog coverage (% of products that can be recommended)"""
        self.print_header("CATALOG COVERAGE TEST")

        all_recommended = set()

        for user in self.users:
            user_id = user["user_id"]

            # Get recommendations
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
            cf_precision = self.results["collaborative_filtering"]["average_precision"]
            cf_recall = self.results["collaborative_filtering"]["average_recall"]
            cf_f1 = self.results["collaborative_filtering"]["average_f1_score"]
            print(f"{Color.BOLD}Collaborative Filtering:{Color.END}")
            print(f"  Precision: {Color.GREEN}{cf_precision:.3f}{Color.END}")
            print(f"  Recall: {Color.GREEN}{cf_recall:.3f}{Color.END}")
            print(f"  F1-Score: {Color.GREEN}{cf_f1:.3f}{Color.END}")

        if "content_based" in self.results:
            cb_precision = self.results["content_based"]["average_precision"]
            cb_recall = self.results["content_based"]["average_recall"]
            cb_f1 = self.results["content_based"]["average_f1_score"]
            print(f"\n{Color.BOLD}Content-Based Filtering:{Color.END}")
            print(f"  Precision: {Color.GREEN}{cb_precision:.3f}{Color.END}")
            print(f"  Recall: {Color.GREEN}{cb_recall:.3f}{Color.END}")
            print(f"  F1-Score: {Color.GREEN}{cb_f1:.3f}{Color.END}")

        if "diversity" in self.results:
            diversity = self.results["diversity"]["average_diversity"]
            print(f"\n{Color.BOLD}Diversity:{Color.END}")
            print(f"  Average Diversity: {Color.GREEN}{diversity:.3f}{Color.END}")

        if "coverage" in self.results:
            coverage = self.results["coverage"]["coverage_percentage"]
            print(f"\n{Color.BOLD}Coverage:{Color.END}")
            print(f"  Catalog Coverage: {Color.GREEN}{coverage:.1f}%{Color.END}")

        # Recommendations
        print(f"\n{Color.BOLD}RECOMMENDATIONS FOR IMPROVEMENT:{Color.END}")

        if "collaborative_filtering" in self.results:
            cf_f1 = self.results["collaborative_filtering"]["average_f1_score"]
            if cf_f1 < 0.3:
                print(
                    f"  {Color.YELLOW}• Low F1-Score: Consider using matrix factorization or deep learning{Color.END}"
                )
            elif cf_f1 < 0.5:
                print(
                    f"  {Color.YELLOW}• Moderate F1-Score: Fine-tune similarity thresholds{Color.END}"
                )
            else:
                print(
                    f"  {Color.GREEN}• Good F1-Score: System performing well{Color.END}"
                )

        if "diversity" in self.results:
            diversity = self.results["diversity"]["average_diversity"]
            if diversity < 0.4:
                print(
                    f"  {Color.YELLOW}• Low diversity: Add diversity penalty in ranking{Color.END}"
                )
            else:
                print(
                    f"  {Color.GREEN}• Good diversity: Recommendations cover multiple categories{Color.END}"
                )

        if "coverage" in self.results:
            coverage = self.results["coverage"]["coverage_percentage"]
            if coverage < 30:
                print(
                    f"  {Color.YELLOW}• Low coverage: Popular items dominate, consider popularity penalty{Color.END}"
                )
            else:
                print(
                    f"  {Color.GREEN}• Good coverage: Wide range of products recommended{Color.END}"
                )

    def save_results(self, filename: str = "recommendation_quality_results.json"):
        """Save detailed results to file"""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n{Color.GREEN}Results saved to {filename}{Color.END}")


def main():
    """Run recommendation quality tests"""
    print(f"{Color.BOLD}{Color.BLUE}")
    print("=" * 70)
    print("  RECOMMENDATION QUALITY TESTING")
    print("=" * 70)
    print(f"{Color.END}")
    print(f"API Endpoint: {API_URL}\n")

    tester = RecommendationQualityTester()

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
