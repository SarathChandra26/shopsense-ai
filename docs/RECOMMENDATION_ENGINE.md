# ShopSense AI — Personalized Recommendation Engine

## 1. Core Philosophy: Why Content-Based First?
Many e-commerce systems claim "collaborative filtering" on tiny or zero-user datasets. Collaborative filtering requires millions of user-item interaction pairs (matrix factorization or two-tower neural networks) and suffers from severe **cold-start** problems for new users and new products.

ShopSense AI intentionally builds an industrial-grade **Content-Based Recommendation Engine** that operates reliably on product attributes, user search history, saved products, and explicit preference memory.

---

## 2. Seven Specialized Recommendation Strategies

| Strategy | Description | Algorithm |
|---|---|---|
| **Best Overall** | Personalized recommendations matching user's top categories, preferred brands, and target budget. | Hybrid vector search against user profile + multi-factor reranker. |
| **Within Budget** | Strict budget enforcement ensuring zero overspending. | Reranker with hard price limit $\le \text{budget\_max}$. |
| **Best Specs** | Maximum hardware performance regardless of price in category. | Sort by numeric specification metrics (RAM, GPU tier, CPU). |
| **Budget Alternatives** | Recommends products that offer comparable capability to a target product but cost **20% to 40% less**. | Vector nearest neighbor search in target category with price constraint $\le 0.80 \times P_{\text{target}}$. |
| **Similar Products** | Finds products geometrically closest to a context product. | ChromaDB cosine vector search using context product's embedding, excluding the product itself. |
| **Alternative Brands** | High-performing alternatives from competing manufacturers. | Vector similarity in same category filtering for $\text{brand} \neq \text{target.brand}$. |
| **Best Value** | Delivers highest performance and customer satisfaction per rupee. | Ranks by $\frac{\text{Rating} \times 10,000}{\text{Price}}$. |

---

## 3. Negative Feedback Loop & Rejection Memory
When users interact with recommendation cards, they can provide granular feedback:
- 👍 Useful
- 💰 Too Costly
- ❌ Wrong Specifications / Not Interested

**Action**: Products marked with negative feedback are recorded in `product_feedback` and automatically excluded from all future recommendation candidate pools for that user ID.
