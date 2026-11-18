import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.schemas.assistant import ChatRequest, ChatResponse, ExtractedConstraints
from backend.app.schemas.search import SearchRequest, SearchResultItem
from backend.app.schemas.preference import UserPreferenceUpdate
from backend.app.search.query_parser import QueryParser
from backend.app.search.search_service import execute_search
from backend.app.repositories.preference_repository import PreferenceRepository
from backend.app.repositories.interaction_repository import InteractionRepository
from backend.app.assistant.ollama_client import OllamaClient
from backend.app.core.logging import logger

SYSTEM_PROMPT = """You are ShopSense AI, a helpful, precise, and completely grounded shopping assistant.
STRICT GROUNDING RULES:
1. You must ONLY answer using the real product catalogue records provided in the context.
2. NEVER fabricate, invent, or assume product specifications, prices, battery life, or features.
3. If a specification is not listed in the provided data, explicitly state "Not available in catalogue".
4. Always clearly specify prices in INR (₹).
5. For each recommended product, explain WHY it matches the user's requirements and honestly state its limitations or trade-offs.
6. Keep explanations concise, professional, and structured with bullet points.
"""

class GroundedShoppingAssistant:
    def __init__(self, db: Session):
        self.db = db
        self.pref_repo = PreferenceRepository(db)
        self.interaction_repo = InteractionRepository(db)
        self.ollama_client = OllamaClient()

    def process_chat(self, request: ChatRequest) -> ChatResponse:
        query = request.message.strip()
        user_id = request.user_id
        q_lower = query.lower()

        # 1. Parse constraints & intent
        constraints = QueryParser.parse(query)
        intent = self._classify_intent(query, constraints)

        # 2. Check for explicit memory / preference update
        # e.g., "Remember that I prefer Lenovo", "My budget is 70000"
        if intent == "preference_update":
            return self._handle_preference_update(query, constraints, user_id)

        # 3. Handle Ambiguous Queries (Needs Clarification)
        if intent == "clarification":
            reply = (
                "Could you specify what kind of product you are looking for? "
                "For example: 'Find a laptop under ₹70,000 for Python development', "
                "'Noise cancelling headphones for office calls', or 'Smartwatch with GPS for running'."
            )
            return ChatResponse(
                reply=reply,
                intent=intent,
                constraints=constraints,
                retrieved_products=[],
                tradeoffs=[],
                grounded_in_catalogue=True,
                llm_source="rule_grounded_engine"
            )

        # 4. Execute Retrieval & Multi-factor Reranking
        search_req = SearchRequest(
            query=query,
            search_type="hybrid_rerank",
            limit=4,
            user_id=user_id
        )
        search_res = execute_search(search_req, self.db)
        retrieved_products = search_res.results

        # 5. Extract Tradeoffs from retrieved products
        tradeoffs = []
        for p in retrieved_products:
            tradeoffs.extend(p.limitations)

        # 6. Try Ollama local generation if available
        llm_reply = None
        llm_source = "rule_grounded_engine"
        
        if self.ollama_client.is_available() and retrieved_products:
            context_block = self._build_context_block(retrieved_products)
            user_msg = f"User Request: {query}\n\nRetrieved Real Catalogue Records:\n{context_block}\n\nPlease recommend and compare the best matching products strictly using the above facts."
            llm_reply = self.ollama_client.generate_chat_response(
                messages=[{"role": "user", "content": user_msg}],
                system_prompt=SYSTEM_PROMPT
            )
            if llm_reply:
                llm_source = f"ollama ({self.ollama_client.model})"

        # 7. Fallback to Grounded Deterministic Response Synthesizer
        if not llm_reply:
            llm_reply = self._generate_deterministic_grounded_reply(query, constraints, retrieved_products)

        return ChatResponse(
            reply=llm_reply,
            intent=intent,
            constraints=constraints,
            retrieved_products=retrieved_products,
            tradeoffs=list(set(tradeoffs))[:4],
            grounded_in_catalogue=True,
            llm_source=llm_source
        )

    def _classify_intent(self, query: str, constraints: ExtractedConstraints) -> str:
        q_lower = query.lower()
        if any(w in q_lower for w in ["remember", "my preference", "prefer", "save my", "my budget is"]):
            return "preference_update"
        if any(w in q_lower for w in ["compare", "difference between", "versus", "vs"]):
            return "compare"
        # If no category was detected and query is short or vague
        if not constraints.category and (len(query.split()) <= 2 or not constraints.intended_usage):
            # Check if query mentions any known brand or specific spec
            if not constraints.brand and not constraints.budget_max and not constraints.ram_gb:
                return "clarification"
        if any(w in q_lower for w in ["recommend", "suggest", "which", "best", "find"]):
            return "recommend"
        return "search"

    def _handle_preference_update(
        self,
        query: str,
        constraints: ExtractedConstraints,
        user_id: str
    ) -> ChatResponse:
        """Persist explicit user preferences into SQLite."""
        pref_update = UserPreferenceUpdate(
            preferred_categories=[constraints.category] if constraints.category else None,
            preferred_brands=[constraints.brand] if constraints.brand else None,
            budget_max=constraints.budget_max,
            budget_min=constraints.budget_min,
            intended_usage=constraints.intended_usage
        )
        self.pref_repo.create_or_update(user_id, pref_update)

        acknowledged = []
        if constraints.brand:
            acknowledged.append(f"brand preference for **{constraints.brand}**")
        if constraints.budget_max:
            acknowledged.append(f"maximum budget of **₹{constraints.budget_max:,.0f}**")
        if constraints.category:
            acknowledged.append(f"category focus on **{constraints.category}**")
        if constraints.intended_usage:
            acknowledged.append(f"intended usage for **{constraints.intended_usage}**")

        summary_ack = ", ".join(acknowledged) if acknowledged else "your shopping preferences"
        reply = (
            f"✅ **Saved to your profile memory!** I have recorded {summary_ack}. "
            f"All future searches and personalized recommendations will automatically account for these preferences."
        )

        return ChatResponse(
            reply=reply,
            intent="preference_update",
            constraints=constraints,
            retrieved_products=[],
            tradeoffs=[],
            grounded_in_catalogue=True,
            llm_source="rule_grounded_engine"
        )

    @staticmethod
    def _build_context_block(results: List[SearchResultItem]) -> str:
        blocks = []
        for i, it in enumerate(results, 1):
            p = it.product
            specs_summary = "; ".join([f"{k}: {v}" for k, v in p.specifications.items()])
            block = (
                f"[{i}] {p.brand} {p.name}\n"
                f"   - Category: {p.category}\n"
                f"   - Price: ₹{p.price:,.0f}\n"
                f"   - Rating: {p.rating}★ ({p.review_count:,} reviews)\n"
                f"   - Specifications: {specs_summary}\n"
                f"   - Key Reasons: {'; '.join(it.match_reasons)}\n"
                f"   - Limitations: {'; '.join(it.limitations) if it.limitations else 'None noted'}"
            )
            blocks.append(block)
        return "\n\n".join(blocks)

    def _generate_deterministic_grounded_reply(
        self,
        query: str,
        constraints: ExtractedConstraints,
        results: List[SearchResultItem]
    ) -> str:
        """Deterministic grounded synthesis when Ollama is offline or unavailable."""
        if not results:
            cat_mention = f" in {constraints.category}" if constraints.category else ""
            budget_mention = f" under ₹{constraints.budget_max:,.0f}" if constraints.budget_max else ""
            return (
                f"No products found matching your exact criteria{cat_mention}{budget_mention}. "
                f"Try adjusting your budget or relaxing specific hardware requirements."
            )

        top_match = results[0]
        p = top_match.product
        
        lines = [
            f"Based on real catalogue records, here is the top recommendation for your request: **{p.brand} {p.name}**.",
            "",
            f"### Top Recommendation: [{p.name}]",
            f"- **Price**: ₹{p.price:,.0f} ({'Within your budget' if constraints.budget_max and p.price <= constraints.budget_max else 'Standard catalogue price'})",
            f"- **Rating**: {p.rating}★ ({p.review_count:,} verified customer ratings)",
            f"- **Key Match Strengths**:"
        ]
        
        for reason in top_match.match_reasons:
            lines.append(f"  • {reason}")
            
        if top_match.limitations:
            lines.append("- **Important Trade-offs / Limitations**:")
            for lim in top_match.limitations:
                lines.append(f"  ⚠️ {lim}")

        if len(results) > 1:
            lines.append("")
            lines.append("### Suitable Alternatives in Catalogue:")
            for alt in results[1:3]:
                alt_p = alt.product
                lines.append(f"- **{alt_p.brand} {alt_p.name}** at **₹{alt_p.price:,.0f}** ({alt_p.rating}★)")
                if alt.match_reasons:
                    lines.append(f"  ↳ {alt.match_reasons[0]}")

        lines.append("")
        lines.append("*All specifications and prices are verified facts retrieved directly from the ShopSense product catalogue.*")
        return "\n".join(lines)
