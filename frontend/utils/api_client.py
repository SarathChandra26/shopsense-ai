import requests
from typing import Dict, Any, List, Optional

BACKEND_URL = "http://127.0.0.1:8000"

class ShopSenseAPIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=10.0)
            return r.json() if r.status_code == 200 else {"status": "error"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def list_products(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        page: int = 1,
        page_size: int = 12
    ) -> Dict[str, Any]:
        params = {"page": page, "page_size": page_size}
        if category and category != "All Categories":
            params["category"] = category
        if brand and brand != "All Brands":
            params["brand"] = brand
        if min_price:
            params["min_price"] = min_price
        if max_price:
            params["max_price"] = max_price
        if min_rating:
            params["min_rating"] = min_rating
            
        r = requests.get(f"{self.base_url}/api/products", params=params, timeout=5.0)
        return r.json() if r.status_code == 200 else {"total": 0, "items": []}

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        r = requests.get(f"{self.base_url}/api/products/{product_id}", timeout=10.0)
        return r.json() if r.status_code == 200 else None

    def search(
        self,
        query: str,
        search_type: str = "hybrid_rerank",
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 10,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        filters = {}
        if category and category != "All Categories":
            filters["category"] = category
        if brand and brand != "All Brands":
            filters["brand"] = brand
        if min_price:
            filters["min_price"] = min_price
        if max_price:
            filters["max_price"] = max_price

        payload = {
            "query": query,
            "search_type": search_type,
            "filters": filters if filters else None,
            "limit": limit,
            "user_id": user_id
        }
        endpoint = "/api/search/hybrid"
        if search_type == "semantic":
            endpoint = "/api/search/semantic"
        elif search_type == "keyword":
            endpoint = "/api/search/keyword"

        r = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=20.0)
        return r.json() if r.status_code == 200 else {"total_found": 0, "results": [], "latency_ms": 0}

    def get_recommendations(
        self,
        user_id: str = "default_user",
        rec_type: str = "best_overall",
        context_product_id: Optional[str] = None,
        limit: int = 6
    ) -> Dict[str, Any]:
        payload = {
            "user_id": user_id,
            "rec_type": rec_type,
            "context_product_id": context_product_id,
            "limit": limit
        }
        r = requests.post(f"{self.base_url}/api/recommendations", json=payload, timeout=15.0)
        return r.json() if r.status_code == 200 else {"items": [], "rationale": ""}

    def compare_products(self, product_ids: List[str]) -> Dict[str, Any]:
        payload = {"product_ids": product_ids}
        r = requests.post(f"{self.base_url}/api/compare", json=payload, timeout=10.0)
        return r.json() if r.status_code == 200 else {"specs_table": [], "tradeoffs": []}

    def chat_assistant(self, message: str, user_id: str = "default_user") -> Dict[str, Any]:
        payload = {"message": message, "user_id": user_id}
        r = requests.post(f"{self.base_url}/api/assistant/chat", json=payload, timeout=25.0)
        return r.json() if r.status_code == 200 else {"reply": "Service temporarily unavailable.", "retrieved_products": []}

    def get_preferences(self, user_id: str = "default_user") -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}/api/preferences/{user_id}", timeout=10.0)
        return r.json() if r.status_code == 200 else {}

    def update_preferences(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.put(f"{self.base_url}/api/preferences/{user_id}", json=updates, timeout=10.0)
        return r.json() if r.status_code == 200 else {}

    def save_product(self, user_id: str, product_id: str) -> bool:
        r = requests.post(f"{self.base_url}/api/saved-products", json={"user_id": user_id, "product_id": product_id}, timeout=10.0)
        return r.status_code in [200, 201]

    def list_saved_products(self, user_id: str = "default_user") -> List[Dict[str, Any]]:
        r = requests.get(f"{self.base_url}/api/saved-products/{user_id}", timeout=10.0)
        return r.json() if r.status_code == 200 else []

    def remove_saved_product(self, user_id: str, product_id: str) -> bool:
        r = requests.delete(f"{self.base_url}/api/saved-products/{user_id}/{product_id}", timeout=10.0)
        return r.status_code in [200, 204]

    def submit_feedback(self, user_id: str, product_id: str, feedback_type: str, comment: Optional[str] = None) -> bool:
        payload = {"user_id": user_id, "product_id": product_id, "feedback_type": feedback_type, "comment": comment}
        r = requests.post(f"{self.base_url}/api/feedback", json=payload, timeout=10.0)
        return r.status_code in [200, 201]

    def get_search_history(self, user_id: str = "default_user") -> List[Dict[str, Any]]:
        r = requests.get(f"{self.base_url}/api/history/{user_id}", timeout=10.0)
        return r.json() if r.status_code == 200 else []

    def get_analytics(self) -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}/api/analytics/summary", timeout=10.0)
        return r.json() if r.status_code == 200 else {}

    def run_evaluation(self, search_type: str = "all", k: int = 5) -> Dict[str, Any]:
        payload = {"search_type": search_type, "k": k}
        r = requests.post(f"{self.base_url}/api/evaluation/run", json=payload, timeout=60.0)
        return r.json() if r.status_code == 200 else {"metrics": []}

    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        r = requests.get(f"{self.base_url}/api/evaluation/results", timeout=10.0)
        return r.json() if r.status_code == 200 else []
