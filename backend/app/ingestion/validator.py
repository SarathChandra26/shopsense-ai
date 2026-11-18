from typing import Dict, Any, List, Tuple, Optional
from backend.app.schemas.product import ProductCreate
from backend.app.core.logging import logger

VALID_CATEGORIES = {
    "Laptops",
    "Smartphones",
    "Headphones",
    "Smartwatches",
    "Monitors",
    "Keyboards",
    "Mice",
    "Tablets",
    "Gaming Accessories",
    "Storage Devices",
}

def validate_product_data(data: Dict[str, Any]) -> Tuple[bool, List[str], Optional[ProductCreate]]:
    """Validate a raw dictionary against product constraints."""
    errors = []
    
    # Check category
    category = data.get("category")
    if not category or category not in VALID_CATEGORIES:
        errors.append(f"Invalid category '{category}'. Must be one of: {sorted(list(VALID_CATEGORIES))}")
        
    # Check price
    price = data.get("price")
    try:
        price_val = float(price)
        if price_val <= 0:
            errors.append("Price must be greater than 0.")
    except (TypeError, ValueError):
        errors.append("Invalid price format.")

    # Check name & brand
    if not data.get("name") or len(str(data.get("name")).strip()) < 2:
        errors.append("Product name is too short or missing.")
    if not data.get("brand") or len(str(data.get("brand")).strip()) < 1:
        errors.append("Brand is required.")

    if errors:
        return False, errors, None

    try:
        validated = ProductCreate(
            id=data.get("id"),
            name=str(data["name"]).strip(),
            brand=str(data["brand"]).strip(),
            category=category,
            description=str(data.get("description", "")).strip(),
            price=float(price),
            original_price=float(data["original_price"]) if data.get("original_price") else None,
            rating=float(data.get("rating", 4.0)),
            review_count=int(data.get("review_count", 0)),
            availability_status=str(data.get("availability_status", "In Stock")),
            image_url=data.get("image_url"),
            source=data.get("source", "synthetic_catalogue"),
            is_demo=bool(data.get("is_demo", True)),
            specifications=data.get("specifications", {})
        )
        return True, [], validated
    except Exception as e:
        return False, [str(e)], None
