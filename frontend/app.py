import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from frontend.utils.api_client import ShopSenseAPIClient
from frontend.components.ui_elements import render_product_card

st.set_page_config(
    page_title="ShopSense AI — Discovery & Recommendation Engine",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API Client
api = ShopSenseAPIClient()
USER_ID = "default_user"

# Sidebar Navigation
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h2 style="margin: 0; color: #1e3a8a;">🛍️ ShopSense AI</h2>
        <span style="font-size: 12px; color: #64748b;">Intelligent Discovery & Retrieval Engine</span>
    </div>
    """,
    unsafe_allow_html=True
)

# System Health Pill in Sidebar
health = api.get_health()
if health.get("status") == "healthy":
    st.sidebar.success(f"Backend: Online • 1,100 Products Indexed")
elif health.get("status") == "offline":
    st.sidebar.error("Backend API is currently offline. Start FastAPI backend at http://localhost:8000.")
else:
    st.sidebar.warning(f"Backend: Degraded ({health.get('status')})")

PAGES = [
    "🏠 Home Dashboard",
    "🤖 AI Shopping Assistant",
    "⚡ Product Search",
    "🔍 Discover Products",
    "⚖️ Product Comparison",
    "🎯 Personalized Recommendations",
    "💾 Saved Products",
    "📜 Search History",
    "⚙️ My Preferences",
    "📊 Search Analytics",
    "🧪 Evaluation Dashboard",
    "🛠️ Settings"
]

selected_page = st.sidebar.radio("Navigation", PAGES, index=0)

# Sidebar Comparison Quick Drawer
if "compare_list" not in st.session_state:
    st.session_state["compare_list"] = []

if st.session_state["compare_list"]:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**⚖️ Comparison Queue ({len(st.session_state['compare_list'])}/4):**")
    for pid in st.session_state["compare_list"]:
        st.sidebar.caption(f"• `{pid}`")
    if st.sidebar.button("Clear Comparison Queue"):
        st.session_state["compare_list"] = []
        st.rerun()

# -------------------------------------------------------------
# PAGE 1: HOME DASHBOARD
# -------------------------------------------------------------
if selected_page == "🏠 Home Dashboard":
    st.title("🛍️ ShopSense AI Discovery & Recommendation Platform")
    st.markdown(
        "Welcome to **ShopSense AI** — an engineering demonstration of modern Information Retrieval (IR), "
        "Dense Vector Embeddings (`all-MiniLM-L6-v2`), SQLite FTS5 Keyword Search, Reciprocal Rank Fusion (RRF), "
        "Deterministic Multi-Factor Reranking, and Grounded Local LLM Shopping Assistance."
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Catalogue Products", value="1,100", delta="10 Categories")
    with col2:
        st.metric(label="Embedding Engine", value="all-MiniLM-L6-v2", delta="384-Dim Dense")
    with col3:
        st.metric(label="Vector Database", value="ChromaDB", delta="Cosine Space")
    with col4:
        st.metric(label="Ranking Method", value="Hybrid + RRF", delta="Multi-Factor Reranker")

    st.markdown("---")
    st.subheader("🚀 Quick Architecture Walkthrough")
    st.markdown(
        """
        - **Semantic Search**: Dense vector embeddings capture conceptual queries like *'laptop for machine learning'* or *'headphones for noisy office'* without needing exact keyword overlap.
        - **Hybrid Retrieval**: Combines SQLite FTS5 (BM25 sparse search) with ChromaDB (dense vector search) using **Reciprocal Rank Fusion (RRF)**. Exact model terms (e.g. `RTX 4050`, `Sony WH-1000XM5`, `144Hz`) match precisely.
        - **Multi-Factor Reranker**: Deterministically weights Semantic Match, Keyword Match, Hardware Specs, Budget Compliance, User Preferences, and Customer Rating.
        - **Zero-Hallucination Assistant**: Integrates with local Ollama (`llama3.2`) with strict grounding rules — answers only from retrieved catalogue facts, or falls back gracefully to a deterministic rule-based grounded engine.
        """
    )

    st.subheader("💡 Suggested Queries to Try")
    sample_queries = [
        "I want a laptop under ₹70,000 for Python development, machine learning basics, and casual gaming with 16 GB RAM.",
        "Wireless noise cancelling headphones with long battery life for remote calls.",
        "Ergonomic mechanical keyboard with wireless connectivity and tactile switches.",
        "144Hz high refresh rate IPS monitor for coding and gaming setup.",
        "Fast 1TB NVMe PCIe 4.0 SSD for PC build storage."
    ]
    for sq in sample_queries:
        if st.button(f"🔍 \"{sq}\"", key=f"sq_{hash(sq)}"):
            st.session_state["search_query_input"] = sq
            st.info("Query copied! Switch to '⚡ Product Search' or '🤖 AI Shopping Assistant' to run.")

# -------------------------------------------------------------
# PAGE 2: AI SHOPPING ASSISTANT
# -------------------------------------------------------------
elif selected_page == "🤖 AI Shopping Assistant":
    st.title("🤖 Grounded AI Shopping Assistant")
    st.caption("Powered by local LLM (Ollama / Llama 3.2) with strict factual grounding & zero hallucinations.")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {
                "role": "assistant",
                "content": "Hello! I am your ShopSense AI shopping assistant. How can I help you discover products today? Tell me your budget, intended use, or desired specifications!"
            }
        ]

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "retrieved_products" in msg and msg["retrieved_products"]:
                st.markdown("**Real Products Retrieved from Catalogue:**")
                for it in msg["retrieved_products"]:
                    render_product_card(it, api, USER_ID, show_score=True, key_prefix=f"chat_{it['product']['id']}")

    user_input = st.chat_input("Ask for recommendations (e.g., 'Find a laptop under ₹70,000 for Python development')...")
    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing request and retrieving catalogue records..."):
                chat_res = api.chat_assistant(user_input, USER_ID)
                reply = chat_res.get("reply", "No response received.")
                st.markdown(reply)
                
                # Show extracted constraints
                constraints = chat_res.get("constraints", {})
                if any(constraints.values()):
                    with st.expander("🛠️ Extracted Search Constraints", expanded=False):
                        st.json(constraints)

                # Show retrieved products
                retrieved = chat_res.get("retrieved_products", [])
                if retrieved:
                    st.markdown("---")
                    st.markdown("### 📦 Verified Matching Products in Catalogue:")
                    for it in retrieved:
                        render_product_card(it, api, USER_ID, show_score=True, key_prefix=f"chat_ret_{it['product']['id']}")

                st.session_state["chat_messages"].append({
                    "role": "assistant",
                    "content": reply,
                    "retrieved_products": retrieved
                })

# -------------------------------------------------------------
# PAGE 3: PRODUCT SEARCH
# -------------------------------------------------------------
elif selected_page == "⚡ Product Search":
    st.title("⚡ Multi-Stage Product Search Engine")
    st.caption("Compare Semantic, Keyword (BM25), Hybrid (RRF), and Multi-Factor Reranked Retrieval.")

    query_val = st.session_state.get("search_query_input", "laptop under 70000 for Python development with 16 GB RAM")
    
    col_q, col_type = st.columns([3, 1])
    with col_q:
        search_query = st.text_input("Natural Language Search Query:", value=query_val)
    with col_type:
        search_mode = st.selectbox(
            "Search Pipeline",
            ["hybrid_rerank", "hybrid", "semantic", "keyword"],
            format_func=lambda x: {
                "hybrid_rerank": "Hybrid + Multi-Factor Reranker",
                "hybrid": "Hybrid Search (RRF)",
                "semantic": "Semantic Search Only (Dense)",
                "keyword": "Keyword Search Only (BM25)"
            }[x]
        )

    # Search Filters Expander
    with st.expander("⚙️ Advanced Metadata Filters", expanded=False):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            cat_filter = st.selectbox("Category", ["All Categories", "Laptops", "Smartphones", "Headphones", "Smartwatches", "Monitors", "Keyboards", "Mice", "Tablets", "Gaming Accessories", "Storage Devices"])
        with f_col2:
            brand_filter = st.text_input("Brand (Optional)", "")
        with f_col3:
            min_p = st.number_input("Min Price (₹)", min_value=0, value=0, step=5000)
        with f_col4:
            max_p = st.number_input("Max Price (₹)", min_value=0, value=0, step=5000)

    if st.button("🚀 Execute Search", type="primary"):
        if not search_query.strip():
            st.warning("Please enter a search query.")
        else:
            with st.spinner(f"Executing {search_mode} search..."):
                res = api.search(
                    query=search_query,
                    search_type=search_mode,
                    category=cat_filter,
                    brand=brand_filter if brand_filter.strip() else None,
                    min_price=float(min_p) if min_p > 0 else None,
                    max_price=float(max_p) if max_p > 0 else None,
                    limit=10,
                    user_id=USER_ID
                )

                st.markdown(f"**Found {res.get('total_found', 0)} matching products** in `{res.get('latency_ms', 0):.1f} ms`")
                st.caption(res.get("explanation", ""))

                results = res.get("results", [])
                if not results:
                    st.info("No matching products found for this query and filter set. Try broadening your criteria.")
                else:
                    for i, it in enumerate(results, 1):
                        render_product_card(it, api, USER_ID, show_score=True, key_prefix=f"search_{i}")

# -------------------------------------------------------------
# PAGE 4: DISCOVER PRODUCTS (CATALOGUE BROWSER)
# -------------------------------------------------------------
elif selected_page == "🔍 Discover Products":
    st.title("🔍 Product Catalogue Browser")
    st.caption("Explore all 1,100 verified demonstration records across 10 hardware categories.")

    col1, col2, col3 = st.columns(3)
    with col1:
        cat = st.selectbox("Category Filter", ["All Categories", "Laptops", "Smartphones", "Headphones", "Smartwatches", "Monitors", "Keyboards", "Mice", "Tablets", "Gaming Accessories", "Storage Devices"])
    with col2:
        brand = st.text_input("Filter by Brand Name", "")
    with col3:
        page = st.number_input("Page Number", min_value=1, value=1, step=1)

    prods_data = api.list_products(
        category=cat,
        brand=brand if brand.strip() else None,
        page=page,
        page_size=12
    )
    total = prods_data.get("total", 0)
    items = prods_data.get("items", [])

    st.markdown(f"Showing **{len(items)}** of **{total}** products (Page {page})")
    
    for i, p in enumerate(items, 1):
        render_product_card(p, api, USER_ID, show_score=False, key_prefix=f"browse_{p['id']}_{i}")

# -------------------------------------------------------------
# PAGE 5: PRODUCT COMPARISON
# -------------------------------------------------------------
elif selected_page == "⚖️ Product Comparison":
    st.title("⚖️ Deterministic Product Comparison Engine")
    st.caption("Compare hardware specifications, identify winners across key dimensions, and understand critical trade-offs.")

    compare_pids = st.session_state.get("compare_list", [])
    
    # Allow manual ID entry
    st.markdown("Select 2 to 4 products to compare. Add them from search result cards or enter Product IDs directly:")
    col_add, col_btn = st.columns([3, 1])
    with col_add:
        extra_pid = st.text_input("Add Product ID (e.g. PROD-LAP-001):", "")
    with col_btn:
        if st.button("Add to Comparison"):
            if extra_pid.strip() and extra_pid.strip() not in compare_pids:
                compare_pids.append(extra_pid.strip())
                st.session_state["compare_list"] = compare_pids
                st.rerun()

    if len(compare_pids) < 2:
        st.info("Please select at least 2 products to compare. Use the '⚖️ Compare' button on any product card.")
    else:
        st.markdown(f"Comparing **{len(compare_pids)} products**: {', '.join(compare_pids)}")
        comp_res = api.compare_products(compare_pids)

        if comp_res and "specs_table" in comp_res:
            st.markdown("### 🏆 Dimension Leaders ('Best For'):")
            best_for = comp_res.get("best_for", {})
            b_cols = st.columns(len(best_for))
            for col, (dim, winner) in zip(b_cols, best_for.items()):
                with col:
                    st.success(f"**{dim}**\n\n{winner}")

            st.markdown("### 📋 Side-by-Side Specification Matrix:")
            table_data = []
            for row in comp_res.get("specs_table", []):
                entry = {"Specification": row["label"]}
                for pid, val in row["values"].items():
                    entry[pid] = val
                if row.get("winner_reason"):
                    entry["Highlight / Winner"] = f"⭐ {row['winner_product_id']} ({row['winner_reason']})"
                else:
                    entry["Highlight / Winner"] = "Tie / Similar" if row["is_different"] else "Identical"
                table_data.append(entry)

            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)

            st.markdown("### ⚖️ Critical Trade-offs:")
            for to in comp_res.get("tradeoffs", []):
                st.markdown(f"• {to}")

            st.markdown("### 📝 Summary Verdict:")
            st.info(comp_res.get("summary_verdict", ""))

# -------------------------------------------------------------
# PAGE 6: PERSONALIZED RECOMMENDATIONS
# -------------------------------------------------------------
elif selected_page == "🎯 Personalized Recommendations":
    st.title("🎯 Personalized Content-Based Recommendations")
    st.caption("Content-based recommendation strategies driven by search history, saved products, and negative feedback filtering.")

    rec_strategy = st.selectbox(
        "Recommendation Strategy",
        ["best_overall", "within_budget", "best_value", "budget_alternatives", "similar_products", "alternative_brands"],
        format_func=lambda x: {
            "best_overall": "Best Overall Match (Preferences + Profile)",
            "within_budget": "Best Within Budget (Strict Price Cap)",
            "best_value": "Best Value for Money (Rating-to-Price Ratio)",
            "budget_alternatives": "Budget Alternatives (Save 20%+ on comparable item)",
            "similar_products": "Similar Products (Vector Embedding Neighbors)",
            "alternative_brands": "Alternative Brands (Competing Brand Options)"
        }[x]
    )

    ctx_pid = None
    if rec_strategy in ["budget_alternatives", "similar_products", "alternative_brands"]:
        ctx_pid = st.text_input("Context Product ID to base alternatives on (e.g. PROD-LAP-001):", value="PROD-LAP-001")

    if st.button("Generate Recommendations", type="primary"):
        with st.spinner("Generating personalized recommendations..."):
            rec_res = api.get_recommendations(
                user_id=USER_ID,
                rec_type=rec_strategy,
                context_product_id=ctx_pid if ctx_pid else None,
                limit=6
            )
            st.info(rec_res.get("rationale", ""))
            items = rec_res.get("items", [])
            if not items:
                st.warning("No recommendations generated for this strategy. Check if the context product ID is valid.")
            else:
                for i, it in enumerate(items, 1):
                    render_product_card(it, api, USER_ID, show_score=True, key_prefix=f"rec_{i}")

# -------------------------------------------------------------
# PAGE 7: SAVED PRODUCTS
# -------------------------------------------------------------
elif selected_page == "💾 Saved Products":
    st.title("💾 Saved Products")
    st.caption("Bookmarked products saved to your local profile memory.")

    saved = api.list_saved_products(USER_ID)
    if not saved:
        st.info("You haven't saved any products yet. Click '💾 Bookmark' on any product card to save it here.")
    else:
        st.markdown(f"You have **{len(saved)}** saved product(s).")
        for p in saved:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{p['name']}** — ₹{p['price']:,.0f} ({p['category']})")
                specs_str = "; ".join([f"{k}: {v}" for k, v in list(p.get("specifications", {}).items())[:4]])
                st.caption(specs_str)
            with col2:
                if st.button("🗑️ Remove", key=f"del_saved_{p['id']}"):
                    api.remove_saved_product(USER_ID, p["id"])
                    st.rerun()
            st.markdown("---")

# -------------------------------------------------------------
# PAGE 8: SEARCH HISTORY
# -------------------------------------------------------------
elif selected_page == "📜 Search History":
    st.title("📜 Search History")
    st.caption("Your recent search queries, execution latencies, and retrieved result counts.")

    history = api.get_search_history(USER_ID)
    if not history:
        st.info("No search history recorded yet. Run a search to see it logged here.")
    else:
        df_hist = pd.DataFrame(history)
        st.dataframe(df_hist[["query", "search_type", "results_count", "latency_ms", "created_at"]], use_container_width=True)

# -------------------------------------------------------------
# PAGE 9: MY PREFERENCES
# -------------------------------------------------------------
elif selected_page == "⚙️ My Preferences":
    st.title("⚙️ Persistent User Preferences & Memory")
    st.caption("View and modify your persistent shopping memory stored in SQLite.")

    current_pref = api.get_preferences(USER_ID)

    with st.form("pref_form"):
        st.subheader("Profile Constraints")
        all_cats = ["Laptops", "Smartphones", "Headphones", "Smartwatches", "Monitors", "Keyboards", "Mice", "Tablets", "Gaming Accessories", "Storage Devices"]
        saved_cats = [c for c in current_pref.get("preferred_categories", []) if c in all_cats]
        pref_cats = st.multiselect("Preferred Categories", all_cats, default=saved_cats)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            b_min = st.number_input("Minimum Budget (₹)", value=float(current_pref.get("budget_min") or 0.0), step=5000.0)
        with col_b2:
            b_max = st.number_input("Maximum Budget (₹)", value=float(current_pref.get("budget_max") or 80000.0), step=5000.0)

        brands_str = st.text_input("Preferred Brands (comma-separated)", value=", ".join(current_pref.get("preferred_brands", ["Lenovo", "Dell"])))
        usage_str = st.text_input("Intended Primary Usage", value=current_pref.get("intended_usage", "coding, Python development, machine learning basics"))

        submitted = st.form_submit_button("💾 Save Preferences")
        if submitted:
            brands_list = [b.strip() for b in brands_str.split(",") if b.strip()]
            updates = {
                "preferred_categories": pref_cats,
                "budget_min": float(b_min) if b_min > 0 else None,
                "budget_max": float(b_max) if b_max > 0 else None,
                "preferred_brands": brands_list,
                "intended_usage": usage_str
            }
            api.update_preferences(USER_ID, updates)
            st.success("Preferences updated and persisted to SQLite!")
            st.rerun()

# -------------------------------------------------------------
# PAGE 10: SEARCH ANALYTICS
# -------------------------------------------------------------
elif selected_page == "📊 Search Analytics":
    st.title("📊 Search & Recommendation Analytics")
    st.caption("Aggregated analytics covering search volumes, latency distributions, and catalogue categories.")

    analytics = api.get_analytics()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Queries Recorded", value=analytics.get("total_searches", 0))
    with col2:
        st.metric(label="Average Search Latency", value=f"{analytics.get('average_latency_ms', 0):.1f} ms")

    st.markdown("---")
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Search Retrieval Types")
        st_dist = analytics.get("search_types_distribution", {})
        if st_dist:
            fig1 = px.pie(
                names=list(st_dist.keys()),
                values=list(st_dist.values()),
                title="Queries by Retrieval Method",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Execute searches to see retrieval distribution.")

    with col_chart2:
        st.subheader("Catalogue Distribution by Category")
        cat_dist = analytics.get("catalogue_category_distribution", {})
        if cat_dist:
            fig2 = px.bar(
                x=list(cat_dist.keys()),
                y=list(cat_dist.values()),
                labels={"x": "Category", "y": "Product Count"},
                title="Catalogue Distribution (1,100 Products)",
                color=list(cat_dist.values()),
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------------
# PAGE 11: EVALUATION DASHBOARD
# -------------------------------------------------------------
elif selected_page == "🧪 Evaluation Dashboard":
    st.title("🧪 Search & Retrieval Evaluation Benchmark")
    st.markdown(
        "Mathematically evaluate and compare **Precision@K**, **Recall@K**, **Mean Reciprocal Rank (MRR)**, "
        "**Normalized Discounted Cumulative Gain (NDCG@K)**, **Constraint Satisfaction Rate**, and **Execution Latency** "
        "against reproducible human-curated ground truth queries."
    )

    col_btn, col_k = st.columns([3, 1])
    with col_k:
        eval_k = st.slider("Evaluation K", min_value=1, max_value=10, value=5)
    with col_btn:
        if st.button("⚡ Run Full Benchmark (All 4 Methods)", type="primary"):
            with st.spinner("Benchmarking Keyword, Semantic, Hybrid, and Hybrid+Rerank..."):
                report = api.run_evaluation("all", k=eval_k)
                st.session_state["latest_eval_report"] = report
                st.success("Evaluation completed!")

    report = st.session_state.get("latest_eval_report")
    if not report:
        # Load historical runs
        history = api.get_evaluation_history()
        if history:
            st.subheader("Recent Evaluation Runs from Database:")
            df_runs = pd.DataFrame(history)
            st.dataframe(df_runs, use_container_width=True)
    else:
        st.markdown("### 📊 Benchmark Metrics Comparison Matrix:")
        metrics = report.get("metrics", [])
        if metrics:
            df_m = pd.DataFrame(metrics)
            st.dataframe(df_m, use_container_width=True)

            # Plot comparison bar chart
            st.subheader("MRR and NDCG Comparison")
            fig = go.Figure()
            fig.add_trace(go.Bar(name='MRR', x=df_m['search_type'], y=df_m['mrr'], marker_color='#3b82f6'))
            fig.add_trace(go.Bar(name=f'NDCG@{eval_k}', x=df_m['search_type'], y=df_m['ndcg'], marker_color='#10b981'))
            fig.add_trace(go.Bar(name='Constraint Satisfaction', x=df_m['search_type'], y=df_m['constraint_satisfaction_rate'], marker_color='#f59e0b'))
            fig.update_layout(barmode='group', title=f"IR Ranking Quality Metrics (k={eval_k})")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 📝 Engineering Assessment:")
            st.info(report.get("comparison_summary", ""))

# -------------------------------------------------------------
# PAGE 12: SETTINGS
# -------------------------------------------------------------
elif selected_page == "🛠️ Settings":
    st.title("🛠️ System Configuration & Infrastructure")
    st.caption("Inspect local runtime components, storage directories, and model configurations.")

    st.subheader("Local Infrastructure Status")
    st.json(health)

    st.subheader("Embedding & Vector Database")
    st.markdown(
        """
        - **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors)
        - **Vector Store**: ChromaDB Persistent Client (`storage/chroma`)
        - **Relational Store**: SQLite3 with FTS5 Full-Text Extension (`storage/sqlite/shopsense.db`)
        - **LLM Endpoint**: Ollama (`http://localhost:11434`), Model: `llama3.2` (Graceful fallback to deterministic grounded engine)
        """
    )
