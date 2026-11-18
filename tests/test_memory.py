import pytest
from backend.app.memory.user_memory import UserMemoryManager
from backend.app.schemas.preference import UserPreferenceUpdate
from backend.app.repositories.interaction_repository import InteractionRepository
from backend.app.schemas.product import ProductCreate
from backend.app.repositories.product_repository import ProductRepository

def test_user_memory_persistence(db_session):
    manager = UserMemoryManager(db_session)
    user_id = "test_user_mem"

    updates = UserPreferenceUpdate(
        preferred_categories=["Laptops", "Monitors"],
        preferred_brands=["Lenovo", "Dell"],
        budget_max=75000.0,
        intended_usage="Python development"
    )
    res = manager.update_preferences(user_id, updates)
    assert res.budget_max == 75000.0
    assert "Lenovo" in res.preferred_brands
    assert "Laptops" in res.preferred_categories

    # Profile lookup
    profile = manager.get_user_profile(user_id)
    assert profile["preferences"]["budget_max"] == 75000.0
    assert profile["preferences"]["preferred_brands"] == ["Lenovo", "Dell"]

def test_interaction_feedback_and_saved(db_session):
    repo = InteractionRepository(db_session)
    prod_repo = ProductRepository(db_session)
    p = prod_repo.create(ProductCreate(
        id="TEST-SAVE-01",
        name="Test Item",
        brand="TestBrand",
        category="Monitors",
        price=15000.0,
        description="Monitor"
    ))

    # Save
    saved = repo.save_product("user_1", "TEST-SAVE-01", "Want to buy later")
    assert saved.id is not None
    saved_list = repo.get_saved_products("user_1")
    assert len(saved_list) == 1
    assert saved_list[0].id == "TEST-SAVE-01"

    # Feedback negative rejection
    repo.record_feedback("user_1", "TEST-SAVE-01", "too_expensive", "Over budget")
    negative_ids = repo.get_negative_product_ids("user_1")
    assert "TEST-SAVE-01" in negative_ids
