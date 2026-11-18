import streamlit as st
from typing import Dict, Any, List, Optional

def render_product_card(
    item_or_prod: Dict[str, Any],
    api_client,
    user_id: str = "default_user",
    show_score: bool = True,
    key_prefix: str = "card"
):
    """Render a structured, interactive product card."""
    # Check if item is wrapped in SearchResultItem
    is_search_result = "product" in item_or_prod
    prod = item_or_prod["product"] if is_search_result else item_or_prod
    score = item_or_prod.get("score") if is_search_result else None
    breakdown = item_or_prod.get("score_breakdown", {}) if is_search_result else {}
    reasons = item_or_prod.get("match_reasons", []) if is_search_result else []
    limitations = item_or_prod.get("limitations", []) if is_search_result else []

    pid = prod["id"]
    name = prod["name"]
    brand = prod["brand"]
    category = prod["category"]
    price = prod["price"]
    orig_price = prod.get("original_price")
    rating = prod.get("rating", 4.0)
    reviews = prod.get("review_count", 0)
    specs = prod.get("specifications", {})
    image_url = prod.get("image_url")

    with st.container():
        st.markdown(
            f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 16px; margin-bottom: 16px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="background-color: #e3f2fd; color: #1565c0; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">{category}</span>
                        <span style="background-color: #f5f5f5; color: #424242; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px; margin-left: 6px;">{brand}</span>
                        <h4 style="margin: 8px 0 4px 0; color: #1a202c; font-size: 16px;">{name}</h4>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 18px; font-weight: 700; color: #2e7d32;">₹{price:,.0f}</div>
                        {"<div style='font-size: 12px; color: #888; text-decoration: line-through;'>₹" + f"{orig_price:,.0f}</div>" if orig_price else ""}
                    </div>
                </div>
                <div style="margin-top: 6px; font-size: 13px; color: #616161;">
                    ⭐ <b>{rating}</b> ({reviews:,} verified ratings) &nbsp;•&nbsp; <span>{prod.get('availability_status', 'In Stock')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_left, col_right = st.columns([3, 2])

        with col_left:
            # Key Specs Pills
            specs_summary = []
            for k, v in list(specs.items())[:5]:
                clean_k = k.replace("_", " ").title()
                specs_summary.append(f"**{clean_k}**: {v}")
            st.markdown(" • ".join(specs_summary))

            # Match reasons
            if reasons:
                st.markdown("**Why it matches your requirements:**")
                for r in reasons[:3]:
                    st.markdown(f"✅ <span style='font-size: 13px;'>{r}</span>", unsafe_allow_html=True)

            # Limitations
            if limitations:
                st.markdown("**Trade-offs & Considerations:**")
                for lim in limitations[:2]:
                    st.markdown(f"⚠️ <span style='font-size: 13px; color: #b78103;'>{lim}</span>", unsafe_allow_html=True)

        with col_right:
            if show_score and score is not None:
                st.metric(label="Match Quality Score", value=f"{int(score * 100)}%", delta=f"{category} Match")
                if breakdown:
                    with st.expander("Score Breakdown"):
                        st.caption(f"Semantic Relevance: {int(breakdown.get('semantic_score', 0)*100)}%")
                        st.caption(f"Keyword BM25: {int(breakdown.get('keyword_score', 0)*100)}%")
                        st.caption(f"Hardware Specs: {int(breakdown.get('specification_score', 0)*100)}%")
                        st.caption(f"Budget Fit: {int(breakdown.get('budget_score', 0)*100)}%")
                        st.caption(f"Rating Score: {int(breakdown.get('rating_score', 0)*100)}%")

            # Action Buttons: Save & Add to Comparison
            act_col1, act_col2 = st.columns(2)
            with act_col1:
                if st.button("💾 Bookmark", key=f"{key_prefix}_save_{pid}"):
                    ok = api_client.save_product(user_id, pid)
                    if ok:
                        st.toast(f"Saved {name} to your profile!", icon="✅")
                    else:
                        st.toast("Already saved or error.", icon="ℹ️")

            with act_col2:
                if "compare_list" not in st.session_state:
                    st.session_state["compare_list"] = []
                is_in_compare = pid in st.session_state["compare_list"]
                btn_label = "Remove Compare" if is_in_compare else "⚖️ Compare"
                if st.button(btn_label, key=f"{key_prefix}_comp_{pid}"):
                    if is_in_compare:
                        st.session_state["compare_list"].remove(pid)
                        st.toast(f"Removed from comparison list.")
                    else:
                        if len(st.session_state["compare_list"]) >= 4:
                            st.warning("Maximum 4 products can be compared at once.")
                        else:
                            st.session_state["compare_list"].append(pid)
                            st.toast(f"Added {name} to comparison list ({len(st.session_state['compare_list'])}/4).")
                    st.rerun()

            # Feedback buttons
            with st.expander("Provide Feedback"):
                fb_col1, fb_col2, fb_col3 = st.columns(3)
                with fb_col1:
                    if st.button("👍 Useful", key=f"{key_prefix}_fb_pos_{pid}"):
                        api_client.submit_feedback(user_id, pid, "useful")
                        st.success("Feedback recorded!")
                with fb_col2:
                    if st.button("💰 Too Costly", key=f"{key_prefix}_fb_cost_{pid}"):
                        api_client.submit_feedback(user_id, pid, "too_expensive")
                        st.info("Marked as too expensive; future recommendations will favor lower price points.")
                with fb_col3:
                    if st.button("❌ Not Interested", key=f"{key_prefix}_fb_not_{pid}"):
                        api_client.submit_feedback(user_id, pid, "not_interested")
                        st.warning("Removed from future recommendations.")

        st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #f0f0f0;'>", unsafe_allow_html=True)
