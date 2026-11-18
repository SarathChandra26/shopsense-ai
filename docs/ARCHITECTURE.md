# ShopSense AI — System Architecture

## 1. Architectural Overview

ShopSense AI is built with a decoupled, modular, layered architecture designed for local, offline-capable, CPU-optimized execution on consumer laptops (16 GB RAM, Windows 10/11).

```
+-------------------------------------------------------------------------------------------------+
|                                         Streamlit Frontend                                      |
|  (Home, Discover, Search, Assistant, Comparison, Personalization, Saved, History, Analytics)    |
+-------------------------------------------------------------------------------------------------+
                                                |  HTTP / REST
                                                v
+-------------------------------------------------------------------------------------------------+
|                                       FastAPI Backend API                                       |
|     (/api/products, /api/search, /api/recommendations, /api/compare, /api/assistant, /health)    |
+-------------------------------------------------------------------------------------------------+
         |                                |                                   |
         v                                v                                   v
+------------------+            +-------------------+               +-------------------+
|  Search Engine   |            | Recommendation    |               |  Grounded AI      |
|  - Semantic (DB) |            |      Engine       |               |    Assistant      |
|  - Keyword (FTS) |            |  - Content-Based  |               |  - Intent Parsing |
|  - Hybrid (RRF)  |            |  - Negative Filter|               |  - Ollama 3.2 3B  |
|  - Reranker      |            |  - Alternatives   |               |  - Fallback Engine|
+------------------+            +-------------------+               +-------------------+
         |                                |                                   |
         +--------------------------------+-----------------------------------+
                                          |
                                          v
+-------------------------------------------------------------------------------------------------+
|                                        Data & Storage Layer                                     |
|                                                                                                 |
|   +------------------------------------+             +-------------------------------------+    |
|   |         SQLite 3 + FTS5            |             |               ChromaDB              |    |
|   |  - Products & Specifications       |             |  - 384-Dim Dense Vector Collection  |    |
|   |  - BM25 Full-Text Search Virtual   |             |  - HNSW Indexing (Cosine Space)     |    |
|   |  - User Preferences & Interactions |             |  - Incremental Vector Upsert/Delete |    |
|   +------------------------------------+             +-------------------------------------+    |
|                                                                                                 |
|   +------------------------------------+             +-------------------------------------+    |
|   |       SentenceTransformers         |             |       Local Ollama Daemon           |    |
|   |  - all-MiniLM-L6-v2 (CPU cached)   |             |  - Llama 3.2 3B Model               |    |
|   +------------------------------------+             +-------------------------------------+    |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. Core Subsystems

### A. Data Ingestion & Catalogue Layer
- **Demonstration Dataset**: 1,100 synthetic products across 10 hardware categories (Laptops, Smartphones, Headphones, Smartwatches, Monitors, Keyboards, Mice, Tablets, Gaming Accessories, Storage Devices).
- **Relational Representation**: `products`, `product_specifications`, `product_categories` in SQLite.
- **Full-Text Index**: SQLite FTS5 table `products_fts` with Porter stemming and unicode tokenization.

### B. Dense Embedding & Vector Store Layer
- **Model**: `all-MiniLM-L6-v2` produces normalized 384-dimensional dense vectors.
- **Vector DB**: ChromaDB persistent client storing HNSW cosine-space indices in `storage/chroma`.
- **Searchable Text Formulation**: Combines name, brand, category, description, and structured hardware specifications into a coherent semantic paragraph.

### C. Search & Retrieval Layer
- **Dense Vector Search**: ChromaDB nearest neighbor query (cosine similarity in $[0, 1]$).
- **Sparse Keyword Search**: SQLite FTS5 BM25 match query.
- **Hybrid Retrieval**: Reciprocal Rank Fusion (RRF) fuses sparse and dense candidate ranks with smoothing constant $k=60$.

### D. Ranking & Reranking Layer
- **Deterministic Multi-Factor Scoring**:
  $$\text{Final Score} = w_{\text{sem}} \cdot S_{\text{sem}} + w_{\text{key}} \cdot S_{\text{key}} + w_{\text{spec}} \cdot S_{\text{spec}} + w_{\text{bud}} \cdot S_{\text{bud}} + w_{\text{rat}} \cdot S_{\text{rat}}$$
- **Constraint Enforcement**: Hard budget constraints eliminate out-of-budget products; soft preferences penalize proportionally.
- **Explainability**: Outputs human-readable match reasons and trade-offs.

### E. AI Assistant & LLM Integration Layer
- **Ollama Llama 3.2 Integration**: Connects to `http://localhost:11434`.
- **Strict Grounding Protocol**: The system prompt prohibits hallucination. The LLM only receives real catalogue records from the retrieval layer.
- **Offline Fallback Engine**: If Ollama is offline or not installed, a deterministic rule-based grounded engine answers all queries without throwing errors.
