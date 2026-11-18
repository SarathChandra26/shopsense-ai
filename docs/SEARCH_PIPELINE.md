# ShopSense AI — Search Pipeline & Retrieval Mechanics

## 1. What is Semantic Search?
Traditional keyword search matches exact tokens (e.g. `laptop`, `Python`). If a user queries:
> *"Lightweight developer workstation for coding and university classes"*
A traditional search engine fails if the product description says *"Ultra-portable programming ultrabook for computer science students"*.
**Semantic search** uses machine-learned dense vector representations where sentences with similar meanings map close together in vector space, allowing conceptual retrieval regardless of exact vocabulary.

---

## 2. What is Hybrid Search?
Neither semantic search nor keyword search is sufficient on its own:
- **Semantic search excels at**: Synonyms, conceptual queries, intent extraction, conversational phrasing.
- **Keyword search excels at**: Exact model numbers (`RTX 4050`, `WH-1000XM5`), unique acronyms (`OLED`, `NVMe`, `144Hz`), and specific brand codes.

**Hybrid search** runs both sparse BM25 keyword matching and dense vector similarity retrieval in parallel, and merges their candidate lists.

---

## 3. Reciprocal Rank Fusion (RRF)
Raw BM25 scores (negative logarithms) and cosine similarity scores ($[0, 1]$) have completely different scales and distributions. Adding raw scores produces distorted results.

ShopSense AI implements **Reciprocal Rank Fusion (RRF)**:
$$RRF(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where:
- $M = \{\text{semantic}, \text{keyword}\}$
- $k = 60$ (the standard Cormack et al. smoothing constant to avoid over-weighting outlier top-1 hits)
- $r_m(d)$ is the 1-based ordinal rank of document $d$ in system $m$.

### Why RRF is Superior:
1. Scale-invariant: relies solely on rank ordering, not raw scores.
2. Highly resilient to outlier score skews.
3. Proven in academic IR benchmarks (TREC) to outperform individual rankers.

---

## 4. End-to-End Query Execution Flow
```
User Natural Language Query
          |
          v
[ Query Parser ]  ---> Extracts: Category, Brand, Budget Max, RAM GB, Intended Usage
          |
          +-----------------------------------+
          |                                   |
          v                                   v
[ Dense Vector Query ]              [ Sparse BM25 Query ]
Embed text via all-MiniLM-L6-v2     Query SQLite FTS5 table
ChromaDB Cosine Space               Exact model tokens & specs
Top-50 candidates                   Top-50 candidates
          |                                   |
          +-----------------+-----------------+
                            |
                            v
               [ Reciprocal Rank Fusion ]
               Fuses ranks with k=60
                            |
                            v
               [ Multi-Factor Reranker ]
               - Hard budget/category filters
               - Hardware spec compatibility
               - Preference profile boosts
               - Customer rating normalization
                            |
                            v
               [ Grounded Explanations ]
               - Transparent score breakdown
               - Match reasons & limitations
```
