"""
Locust Load Testing Configuration for E-Commerce API
Tests system performance under concurrent user load
"""

from locust import HttpUser, task, between, events
import random
import json
import time

# Global variables to store test data
user_ids = []
product_ids = []
admin_user_id = None


@events.init_command_line_parser.add_listener
def init_parser(parser):
    """Add custom command line arguments"""
    parser.add_argument("--base-url", type=str, default="http://localhost:8000",
                       help="Base URL of the API")


class ECommerceUser(HttpUser):
    """Simulates a typical e-commerce user behavior"""

    # Wait between 1-3 seconds between tasks (realistic user behavior)
    wait_time = between(1, 3)

    def on_start(self):
        """Setup: Register and login user"""
        # Register a new user
        timestamp = int(time.time() * 1000)
        self.username = f"loadtest_user_{timestamp}_{random.randint(1000, 9999)}"
        self.email = f"{self.username}@test.com"
        self.password = "test123"

        # Register
        response = self.client.post("/api/register", json={
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "preferences": random.sample(["Electronics", "Books", "Clothing", "Home"], 2)
        })

        if response.status_code == 200:
            data = response.json()
            self.user_id = data.get("user_id")
            user_ids.append(self.user_id)
        else:
            # If registration fails, try to login
            self.user_id = None

    @task(3)
    def browse_products(self):
        """Browse products (most common action - weight 3)"""
        categories = ["Electronics", "Books", "Clothing", "Home", "Sports"]
        category = random.choice(categories)

        self.client.get(f"/api/products?category={category}",
                       name="/api/products (by category)")

    @task(2)
    def search_products(self):
        """Search for products (weight 2)"""
        search_terms = ["laptop", "phone", "book", "shirt", "shoes"]
        term = random.choice(search_terms)

        self.client.get(f"/api/products?search={term}",
                       name="/api/products (search)")

    @task(2)
    def view_product_details(self):
        """View individual product details (weight 2)"""
        if not product_ids:
            # Get products first if we don't have any
            response = self.client.get("/api/products")
            if response.status_code == 200:
                products = response.json().get("products", [])
                product_ids.extend([p["_id"] for p in products[:20]])

        if product_ids:
            product_id = random.choice(product_ids)
            self.client.get(f"/api/products/{product_id}",
                           name="/api/products/{id}")

    @task(1)
    def add_to_cart(self):
        """Add product to cart (weight 1)"""
        if not self.user_id:
            return

        if not product_ids:
            response = self.client.get("/api/products")
            if response.status_code == 200:
                products = response.json().get("products", [])
                product_ids.extend([p["_id"] for p in products[:20]])

        if product_ids:
            product_id = random.choice(product_ids)
            self.client.post(f"/api/cart/{self.user_id}/items", json={
                "product_id": product_id,
                "quantity": random.randint(1, 3)
            }, name="/api/cart/{user_id}/items (add)")

    @task(1)
    def view_cart(self):
        """View shopping cart (weight 1)"""
        if not self.user_id:
            return

        self.client.get(f"/api/cart/{self.user_id}",
                       name="/api/cart/{user_id}")

    @task(1)
    def get_recommendations(self):
        """Get product recommendations (weight 1)"""
        if not self.user_id:
            return

        algorithms = ["collaborative", "content", "hybrid"]
        algorithm = random.choice(algorithms)

        self.client.get(f"/api/recommendations/{self.user_id}?algorithm={algorithm}",
                       name=f"/api/recommendations ({algorithm})")

    @task(1)
    def track_interaction(self):
        """Track user interaction with products (weight 1)"""
        if not self.user_id or not product_ids:
            return

        product_id = random.choice(product_ids)
        interaction_type = random.choice(["view", "like", "rating"])

        payload = {
            "user_id": self.user_id,
            "product_id": product_id,
            "interaction_type": interaction_type
        }

        if interaction_type == "rating":
            payload["rating"] = random.randint(1, 5)

        self.client.post("/api/interactions", json=payload,
                        name="/api/interactions")

    @task(1)
    def view_profile(self):
        """View user profile (weight 1)"""
        if not self.user_id:
            return

        self.client.get(f"/api/users/{self.user_id}",
                       name="/api/users/{user_id}")

    @task(1)
    def view_history(self):
        """View user interaction history (weight 1)"""
        if not self.user_id:
            return

        self.client.get(f"/api/users/{self.user_id}/history",
                       name="/api/users/{user_id}/history")


class BuyerUser(HttpUser):
    """Simulates a user who actually makes purchases"""

    wait_time = between(2, 5)
    weight = 2  # Less common than browsers

    def on_start(self):
        """Register and login"""
        timestamp = int(time.time() * 1000)
        self.username = f"buyer_{timestamp}_{random.randint(1000, 9999)}"
        self.email = f"{self.username}@test.com"

        response = self.client.post("/api/register", json={
            "username": self.username,
            "email": self.email,
            "password": "test123",
            "preferences": ["Electronics", "Books"]
        })

        if response.status_code == 200:
            self.user_id = response.json().get("user_id")
        else:
            self.user_id = None

    @task
    def complete_purchase_flow(self):
        """Complete full purchase workflow"""
        if not self.user_id:
            return

        # 1. Browse products
        response = self.client.get("/api/products?category=Electronics")
        if response.status_code != 200:
            return

        products = response.json().get("products", [])
        if not products:
            return

        # 2. Add 2-3 items to cart
        for _ in range(random.randint(2, 3)):
            product = random.choice(products)
            self.client.post(f"/api/cart/{self.user_id}/items", json={
                "product_id": product["_id"],
                "quantity": random.randint(1, 2)
            })
            time.sleep(0.5)

        # 3. View cart
        response = self.client.get(f"/api/cart/{self.user_id}")
        if response.status_code != 200:
            return

        cart = response.json()
        if not cart.get("items"):
            return

        # 4. Checkout (only if cart has items)
        self.client.post(f"/api/checkout/{self.user_id}", json={
            "shipping_address": "123 Test St, Test City, TC 12345",
            "payment_method": "credit_card"
        }, name="/api/checkout/{user_id}")

        # 5. View orders
        time.sleep(1)
        self.client.get(f"/api/orders/{self.user_id}",
                       name="/api/orders/{user_id}")


class AdminUser(HttpUser):
    """Simulates admin operations"""

    wait_time = between(5, 10)
    weight = 1  # Rare compared to regular users

    def on_start(self):
        """Get admin user ID"""
        # In real scenario, you'd login as admin
        # For testing, we'll use a pre-created admin user
        global admin_user_id

        # Try to get an admin user
        response = self.client.get("/api/users/test")
        if response.status_code == 200:
            admin_user_id = "your_admin_user_id_here"
        else:
            admin_user_id = None

    @task(3)
    def view_admin_stats(self):
        """View admin dashboard statistics"""
        if not admin_user_id:
            return

        self.client.get(f"/api/admin/stats?admin_user_id={admin_user_id}",
                       name="/api/admin/stats")

    @task(2)
    def view_all_orders(self):
        """View all orders"""
        if not admin_user_id:
            return

        self.client.get(f"/api/admin/orders?admin_user_id={admin_user_id}",
                       name="/api/admin/orders")

    @task(1)
    def update_product(self):
        """Update product information"""
        if not admin_user_id or not product_ids:
            return

        product_id = random.choice(product_ids)
        self.client.put(f"/api/admin/products/{product_id}?admin_user_id={admin_user_id}",
                       json={
                           "price": random.uniform(10, 500),
                           "stock_quantity": random.randint(10, 100)
                       },
                       name="/api/admin/products/{id} (update)")


# Events for better reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    print("\n" + "="*70)
    print("LOAD TEST STARTING")
    print("="*70)
    print(f"Target URL: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("="*70 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    print("\n" + "="*70)
    print("LOAD TEST COMPLETED")
    print("="*70)

    stats = environment.runner.stats

    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min Response Time: {stats.total.min_response_time}ms")
    print(f"Max Response Time: {stats.total.max_response_time}ms")
    print(f"Requests per Second: {stats.total.total_rps:.2f}")

    if stats.total.num_requests > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"Failure Rate: {failure_rate:.2f}%")

    print("="*70 + "\n")


"""
HOW TO RUN:

1. Basic run (web UI):
   locust -f locustfile.py --host http://localhost:8000
   Then open http://localhost:8089

2. Headless mode (50 users, 10/sec spawn rate, 60 seconds):
   locust -f locustfile.py --headless --users 50 --spawn-rate 10 --run-time 60s --host http://localhost:8000

3. Different user loads:
   # Light load (50 users)
   locust -f locustfile.py --headless --users 50 --spawn-rate 5 --run-time 60s --host http://localhost:8000

   # Medium load (100 users)
   locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 120s --host http://localhost:8000

   # Heavy load (500 users)
   locust -f locustfile.py --headless --users 500 --spawn-rate 20 --run-time 180s --host http://localhost:8000

4. Generate HTML report:
   locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 60s --host http://localhost:8000 --html load_test_report.html

5. Export CSV stats:
   locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 60s --host http://localhost:8000 --csv stats
"""
