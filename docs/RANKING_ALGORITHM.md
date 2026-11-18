# ShopSense AI — Ranking & Reranking Algorithm

## 1. Multi-Factor Deterministic Ranking Formula

Each retrieved candidate is scored using multiple normalized factors in $[0.0, 1.0]$:

$$\text{Final Score} = \min\left(1.0, \left(\sum_{f \in F} w_f \cdot S_f\right) \times (0.85 + 0.15 \cdot S_{\text{pref}})\right)$$

Where factors $F$ and default normalized weights are:

| Factor | Description | Weight ($w_f$) |
|---|---|---|
| **Semantic Relevance** ($S_{\text{sem}}$) | Cosine similarity from ChromaDB vector retrieval | 0.35 |
| **Keyword Relevance** ($S_{\text{key}}$) | Normalized BM25 score from SQLite FTS5 | 0.20 |
| **Specification Match** ($S_{\text{spec}}$) | Hardware spec satisfaction (RAM, GPU, Battery) | 0.20 |
| **Budget Compatibility** ($S_{\text{bud}}$) | Proximity to budget; 0 if hard limit violated | 0.15 |
| **Product Rating** ($S_{\text{rat}}$) | Customer satisfaction normalized from $[1.0, 5.0]$ | 0.10 |
| **Preference Match** ($S_{\text{pref}}$) | Alignment with user's saved brand & category memory | Bonus |

---

## 2. Hard Constraints vs. Soft Preferences

### Hard Constraints:
1. **Category Match**: If query asks for *"laptop"*, products from *"smartphones"* or *"monitors"* are strictly excluded.
2. **Budget Max (Strict Mode)**: If price exceeds the user's explicit budget limit:
   $$S_{\text{bud}} = 0.0$$
   The product is filtered out of eligible recommendations.

### Soft Preferences:
1. **Brand Affinity**: If user prefers *Lenovo*, products from Lenovo receive a preference boost, but high-performing *Dell* or *ASUS* options are still recommended.
2. **RAM Threshold**: If query requests 16 GB, an 8 GB model is not completely discarded unless strict filtering is on, but receives a partial score ($8/16 = 0.5$).

---

## 3. Second-Stage Reranking Mechanics
1. **Candidate Pool**: Hybrid retrieval extracts top-40 candidates.
2. **Feature Evaluation**: Reranker inspects raw relational specs against extracted query constraints.
3. **Score Breakdown Computation**: Each candidate receives individual score components.
4. **Honest Rationale Extraction**: Generates verified positive reasons and transparent trade-offs (e.g. heavy weight, integrated GPU, moderate battery).
5. **Deterministic Sorting**: Final candidates are sorted strictly by `Final Score` descending.
