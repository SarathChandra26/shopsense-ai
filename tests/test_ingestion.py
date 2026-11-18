import pytest
from backend.app.ingestion.cleaner import clean_price, clean_rating, clean_string, clean_specifications
from backend.app.ingestion.validator import validate_product_data
from backend.app.repositories.product_repository import ProductRepository
from backend.app.schemas.product import ProductCreate, ProductUpdate

def test_cleaner_functions():
    assert clean_price("₹68,990.00") == 68990.0
    assert clean_price("$1,200") == 1200.0
    assert clean_price(None) == 0.0
    assert clean_rating("4.85") == 4.9
    assert clean_rating(10.0) == 5.0
    assert clean_rating(-2.0) == 1.0
    assert clean_string("  Lenovo   Legion  ") == "Lenovo Legion"
    
    specs = clean_specifications({"RAM GB": 16, "Processor": "Intel i7 "})
    assert specs == {"ram_gb": 16, "processor": "Intel i7"}

def test_validator_valid_and_invalid():
    valid_data = {
        "name": "Lenovo IdeaPad Gaming 3",
        "brand": "Lenovo",
        "category": "Laptops",
        "price": 65000.0,
        "description": "Gaming laptop with 16 GB RAM"
    }
    is_valid, errs, prod = validate_product_data(valid_data)
    assert is_valid is True
    assert prod.brand == "Lenovo"
    assert prod.price == 65000.0

    # Invalid Category
    invalid_cat = dict(valid_data, category="Spaceships")
    is_valid, errs, _ = validate_product_data(invalid_cat)
    assert is_valid is False
    assert any("category" in e.lower() for e in errs)

    # Invalid Price
    invalid_price = dict(valid_data, price=-500)
    is_valid, errs, _ = validate_product_data(invalid_price)
    assert is_valid is False
    assert any("price" in e.lower() for e in errs)

def test_product_crud_and_duplicates(db_session):
    repo = ProductRepository(db_session)
    prod_in = ProductCreate(
        id="TEST-LAP-001",
        name="Dell XPS 13",
        brand="Dell",
        category="Laptops",
        price=95000.0,
        description="Ultra-portable developer workstation",
        specifications={"ram_gb": 16, "processor": "Intel Core i7"}
    )
    p = repo.create(prod_in)
    assert p.id == "TEST-LAP-001"
    assert p.price == 95000.0

    # Read
    fetched = repo.get_by_id("TEST-LAP-001")
    assert fetched is not None
    assert fetched.name == "Dell XPS 13"

    # Duplicate detection by ID and by name+brand
    assert repo.get_by_name_and_brand("Dell XPS 13", "Dell") is not None

    # Update
    update_in = ProductUpdate(price=92000.0, specifications={"ram_gb": 32})
    updated = repo.update("TEST-LAP-001", update_in)
    assert updated.price == 92000.0
    u_dict = repo.format_product_dict(updated)
    assert u_dict["specifications"]["ram_gb"] == 32.0

    # Delete
    deleted = repo.delete("TEST-LAP-001")
    assert deleted is True
    assert repo.get_by_id("TEST-LAP-001") is None
