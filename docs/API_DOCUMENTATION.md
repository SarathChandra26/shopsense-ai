# ShopSense AI — Backend REST API Documentation

The ShopSense AI backend is implemented with **FastAPI** and auto-generates interactive Swagger documentation at `http://localhost:8000/docs` and Redoc at `http://localhost:8000/redoc`.

Base URL: `http://localhost:8000`

---

## 1. Health Endpoints
- **`GET /health`** or **`GET /api/health`**
  - Returns overall system health, total SQL products count, ChromaDB collection status, and Ollama connection state.

---

## 2. Product Catalogue Endpoints
- **`GET /api/products`**
  - Query params: `category`, `brand`, `min_price`, `max_price`, `min_rating`, `availability`, `page`, `page_size`.
  - Returns paginated `ProductListResponse`.
- **`GET /api/products/{product_id}`**
  - Returns detailed `ProductResponse` with category-specific structured specifications.
- **`POST /api/products`**
  - Inserts a new product into SQLite, SQLite FTS5, and ChromaDB vector index.
- **`PUT /api/products/{product_id}`**
  - Incrementally updates product fields, FTS5 index, and re-embeds vector in ChromaDB.
- **`DELETE /api/products/{product_id}`**
  - Removes product from SQLite, FTS5 table, and ChromaDB collection.
- **`POST /api/products/import`**
  - Accepts CSV file upload or triggers import from `data/products.csv`.

---

## 3. Search Endpoints
- **`POST /api/search/semantic`**: Pure dense vector similarity retrieval.
- **`POST /api/search/keyword`**: Pure SQLite FTS5 BM25 retrieval.
- **`POST /api/search/hybrid`**: Reciprocal Rank Fusion (RRF) with multi-factor reranking.
  - Body:
    ```json
    {
      "query": "laptop under 70000 for Python development with 16 GB RAM",
      "search_type": "hybrid_rerank",
      "filters": {
        "category": "Laptops",
        "max_price": 70000.0
      },
      "limit": 10,
      "user_id": "default_user"
    }
    ```

---

## 4. Recommendation & Comparison Endpoints
- **`POST /api/recommendations`** & **`GET /api/recommendations/{user_id}`**
  - Strategies: `best_overall`, `within_budget`, `best_specs`, `budget_alternatives`, `similar_products`, `alternative_brands`, `best_value`.
- **`POST /api/compare`**
  - Body: `{"product_ids": ["PROD-LAP-001", "PROD-LAP-002"]}`
  - Returns structured comparison matrix, dimension winners, trade-offs, and summary verdict.

---

## 5. AI Assistant & Preferences Endpoints
- **`POST /api/assistant/chat`**
  - Body: `{"message": "I want a laptop under ₹70,000 for Python programming", "user_id": "default_user"}`
  - Returns grounded response, extracted constraints, retrieved products, and trade-offs.
- **`GET /api/preferences/{user_id}`**: Retrieves stored preference memory.
- **`PUT /api/preferences/{user_id}`**: Updates budget, brands, categories, usage.
- **`POST /api/feedback`**: Records user feedback (useful, too_expensive, not_interested).
- **`GET /api/analytics/summary`**: Aggregated query volume and latency analytics.

---

## 6. Evaluation Endpoints
- **`POST /api/evaluation/run`**: Triggers real benchmark run (`search_type: "all"` or specific method).
- **`GET /api/evaluation/results`**: Retrieves historical benchmark runs.
