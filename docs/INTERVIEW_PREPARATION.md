# ShopSense AI — Technical Interview Preparation & Architecture Deep-Dive

This document provides clear, technically sound answers to the core questions commonly asked in Senior AI Search Engineer, Recommendation Systems Engineer, and Machine Learning Backend interviews.

---

### 1. What are Embeddings?
An **embedding** is a learned mapping that converts high-dimensional, discrete categorical or textual data (like sentences or product descriptions) into a continuous low-dimensional geometric vector space ($\mathbb{R}^d$). In this vector space, geometric distance directly corresponds to semantic relatedness: phrases with similar meanings have vectors that point in almost identical directions.

---

### 2. How does Sentence Transformers work?
Standard BERT models are designed for cross-encoders ($A + B \to \text{score}$), which require $O(n^2)$ model passes to search $n$ products. **Sentence Transformers (SBERT)** uses a siamese/triplet neural network architecture with mean pooling to compute a fixed-size vector (e.g. 384 dimensions) for each sentence independently. This reduces search complexity from $O(n)$ neural passes at query time down to an initial offline vector encoding followed by sub-millisecond dot-product/cosine vector search ($O(1)$ with HNSW indexing).

---

### 3. Why use ChromaDB instead of a traditional relational database?
Traditional relational databases (B-Trees) index scalar values on 1D ordered lines ($<, =, >$). High-dimensional vectors (e.g. 384 dimensions) suffer from the *Curse of Dimensionality*, making B-Tree searches degrade to full sequential scans ($O(N)$). ChromaDB uses **Hierarchical Navigable Small World (HNSW)** graph indexing, which organizes vectors in multi-layered graphs allowing approximate nearest neighbor (ANN) retrieval in $O(\log N)$ logarithmic time.

---

### 4. How does Cosine Similarity work?
Cosine similarity measures the cosine of the angle $\theta$ between two non-zero vectors in an inner product space:
$$\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
Because SentenceTransformers outputs $L_2$-normalized vectors ($\|\mathbf{u}\|_2 = 1.0$), the formula simplifies to the simple dot product:
$$\cos(\theta) = \mathbf{u} \cdot \mathbf{v}$$
It ranges from $-1.0$ (opposite) to $1.0$ (identical direction), unaffected by the length of the original text.

---

### 5. What is Semantic Search?
Semantic search retrieves documents based on the **meaning and intent** of a query rather than literal keyword matches. For example, a query for *"laptop for university coding classes"* will retrieve products described as *"programming ultrabook for computer science students"* because their vector representations reside in the same geometric neighborhood.

---

### 6. What is Hybrid Search?
Hybrid search combines:
1. **Dense Semantic Retrieval**: High recall on synonyms, paraphrases, and intent.
2. **Sparse Keyword Retrieval (BM25)**: Exact precision on specific model numbers (`RTX 4050`), brand names, and technical acronyms (`OLED`, `NVMe`).
Merging both ensures that neither conceptual queries nor exact serial numbers fail.

---

### 7. What is Reciprocal Rank Fusion (RRF)?
Adding raw BM25 scores (unbounded negative logarithms) and raw cosine similarity ($[0, 1]$) is mathematically invalid because their score distributions are completely different. **Reciprocal Rank Fusion** is a rank-based fusion algorithm:
$$\text{RRF Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
Where $r_m(d)$ is the 1-based rank of item $d$ in retrieval method $m$, and $k=60$ is a smoothing constant. RRF is scale-invariant and guarantees that an item performing well across both retrieval systems outranks items appearing in only one.

---

### 8. What is Reranking and why is it two-stage?
In a multi-stage search architecture:
- **Stage 1 (Retrieval)**: Fast, coarse-grained candidate generation filtering 1,000,000 items down to the top 40 candidates in $<20$ ms using vector and inverted index lookups.
- **Stage 2 (Reranking)**: A computationally detailed, deterministic ranker that computes heavy features: exact hardware spec matching, hard budget constraint filtering, customer rating normalization, user brand preferences, and trade-off generation on just the top 40 candidates.

---

### 9. How does a Content-Based Recommendation Engine work?
A content-based recommender profiles items based on structured descriptors (category, brand, price, specs) and dense semantic representations. It profiles users by aggregating their interaction history (searches, saved products, preferences). It calculates candidate scores by matching the user's vector and preference constraints against item attributes, avoiding collaborative filtering's cold-start flaw.

---

### 10. How are ranking weights selected?
Weights ($w_{\text{sem}}=0.35, w_{\text{key}}=0.20, w_{\text{spec}}=0.20, w_{\text{bud}}=0.15, w_{\text{rat}}=0.10$) were tuned to balance conceptual relevance with strict hardware requirements:
1. Hard constraints (budget and category) act as binary gates ($S_{\text{bud}} = 0$).
2. Soft weights order the remaining eligible candidates according to user priorities.

---

### 11. What are Precision@K and Recall@K?
- **Precision@K**: The percentage of items in the top-$K$ results that are relevant ($\frac{\text{Hits}}{K}$). Measures how clean the top results are.
- **Recall@K**: The fraction of all relevant items in the entire catalogue that appear in the top-$K$ ($\frac{\text{Hits}}{|\text{Relevant}|}$). Measures search completeness.

---

### 12. What is MRR (Mean Reciprocal Rank)?
MRR evaluates where the **first relevant result** appears in the ranked list:
$$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}_q}$$
If the top result is relevant, rank is 1 ($\text{RR}=1.0$); if the first relevant result is at position 2, $\text{RR}=0.5$.

---

### 13. What is NDCG (Normalized Discounted Cumulative Gain)?
NDCG measures ranking quality for graded relevance (e.g. 2 = highly relevant, 1 = partially relevant, 0 = irrelevant). It penalizes putting relevant items lower down the list using logarithmic discount:
$$\text{DCG@K} = \sum_{i=1}^K \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}$$
Dividing by the Ideal DCG ($\text{IDCG}$) normalizes the score to $[0.0, 1.0]$.

---

### 14. How is product memory stored?
ShopSense AI stores user preferences in SQLite:
- Preferred categories and brands (comma-separated strings).
- Budget limits (`budget_min`, `budget_max`).
- Intended primary usage (e.g. *"Python development, machine learning"*).
- Structured preferred hardware specs (JSON dictionary).
- Interaction history and negative feedback (`product_feedback`).

---

### 15. How does the LLM avoid inventing product specifications?
ShopSense enforces strict **Retrieval-Augmented Generation (RAG) Grounding**:
1. The LLM does NOT search or invent products; the backend Python search engine executes the retrieval and deterministic reranking first.
2. The LLM is fed only the exact retrieved database records as verified context.
3. System prompt explicitly commands: *"Never invent specifications, prices, or ratings. If missing, state 'Not available in catalogue'"*.
4. If Ollama is offline, a deterministic Python template engine produces the response with verified facts.
