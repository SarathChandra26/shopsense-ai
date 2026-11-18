# ShopSense AI — Embedding Pipeline & Vector Database

## 1. What are Text Embeddings?
An **embedding** is a mapping from discrete human language tokens into a continuous multi-dimensional geometric vector space:
$$\vec{v} = f(\text{text}) \in \mathbb{R}^{384}$$

In this space, semantic similarity correlates directly with geometric proximity (angle between vectors).

---

## 2. Sentence Transformers (`all-MiniLM-L6-v2`)
ShopSense AI uses `sentence-transformers/all-MiniLM-L6-v2`:
- **Architecture**: 6-layer MiniLM transformer fine-tuned on over 1 billion sentence pairs using contrastive learning.
- **Output Dimension**: 384 dimensions.
- **Inference Speed**: ~14,200 sentences/second on GPU, ~700 sentences/second on consumer CPU.
- **Memory Footprint**: ~80 MB RAM. Perfect for 16 GB laptop constraints.
- **Normalization**: Vectors are $L_2$-normalized such that $||\vec{v}||_2 = 1.0$.

---

## 3. Searchable Text Formulation
Dense embeddings perform best when text contains natural syntactic context rather than isolated keywords. For every product, ShopSense constructs:

```python
searchable_text = (
    f"Product: {name}. Brand: {brand}. Category: {category}. "
    f"Key Specs: {specs_text}. "
    f"Overview: {description}"
)
```
Example:
> *"Product: Lenovo IdeaPad Gaming 3 (AMD Ryzen 5 7535HS, 16 GB RAM, 512 GB SSD, NVIDIA RTX 4050). Brand: Lenovo. Category: Laptops. Key Specs: Processor: AMD Ryzen 5; Ram Gb: 16; Storage Gb: 512; Gpu: NVIDIA RTX 4050; Battery Hours: 7.2; Weight Kg: 2.2. Overview: High performance gaming and developer laptop designed for programming, machine learning basics, casual 1080p gaming, and college multitasking."*

---

## 4. Vector Database: ChromaDB
ChromaDB is used as the local, embedded vector database:
- **Index Type**: Hierarchical Navigable Small World (HNSW) graph index.
- **Metric Space**: Cosine distance ($d_{\text{cosine}} = 1 - \cos(\theta)$).
- **Persistent Directory**: `storage/chroma`.
- **Metadata Filters**: Filters by category, price, and availability at query time.
- **Incremental Indexing**: Products are inserted, updated, and deleted individually without rebuilding the entire collection.
