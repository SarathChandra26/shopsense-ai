import pytest
from backend.app.schemas.assistant import ChatRequest
from backend.app.assistant.grounded_assistant import GroundedShoppingAssistant
from backend.app.repositories.preference_repository import PreferenceRepository

def test_shopping_assistant_preference_memory(db_session):
    assistant = GroundedShoppingAssistant(db_session)
    req = ChatRequest(
        message="Remember that I prefer Lenovo laptops and my budget is ₹70,000",
        user_id="user_assistant_test"
    )
    res = assistant.process_chat(req)
    assert res.intent == "preference_update"
    assert "Saved to your profile memory" in res.reply
    assert res.constraints.brand == "Lenovo"
    assert res.constraints.budget_max == 70000.0

    # Verify SQLite persistence
    pref_repo = PreferenceRepository(db_session)
    saved_pref = pref_repo.get_by_user_id("user_assistant_test")
    assert saved_pref is not None
    assert saved_pref.budget_max == 70000.0
    assert "Lenovo" in saved_pref.preferred_brands

def test_shopping_assistant_clarification(db_session):
    assistant = GroundedShoppingAssistant(db_session)
    req = ChatRequest(
        message="good stuff",
        user_id="user_assistant_test"
    )
    res = assistant.process_chat(req)
    assert res.intent == "clarification"
    assert "Could you specify" in res.reply
