import json
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.database.session import SessionLocal
from backend.app.models.product import Product
from backend.app.core.config import settings
from backend.app.core.logging import logger

def build_ground_truth_dataset(db: Session, output_path: Path = None):
    """Build a reproducible, realistic ground-truth evaluation testset with real database IDs."""
    if output_path is None:
        output_path = settings.EVALUATION_TESTSET_PATH

    # Helper to find products
    def find_pids(category: str, max_price: float = None, min_ram: float = None, keywords: list = None, limit: int = 5):
        q = db.query(Product).filter(Product.category == category)
        if max_price:
            q = q.filter(Product.price <= max_price)
        prods = q.all()
        matching = []
        for p in prods:
            specs = {s.spec_key: s.numeric_value or s.spec_value for s in p.specifications}
            if min_ram and float(specs.get("ram_gb", 0)) < min_ram:
                continue
            if keywords:
                text_to_check = f"{p.name} {p.description}".lower()
                if not any(k.lower() in text_to_check for k in keywords):
                    continue
            matching.append(p.id)
            if len(matching) >= limit:
                break
        return matching

    test_queries = [
        {
            "id": "eval-q01",
            "query": "laptop under 70000 for Python development with 16 GB RAM",
            "category": "Laptops",
            "constraints": {"category": "Laptops", "budget_max": 70000.0, "ram_gb": 16.0},
            "relevant_product_ids": find_pids("Laptops", max_price=70000.0, min_ram=16.0, limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q02",
            "query": "wireless noise cancelling over ear headphones for office calls",
            "category": "Headphones",
            "constraints": {"category": "Headphones"},
            "relevant_product_ids": find_pids("Headphones", keywords=["over-ear", "anc", "wh-", "quietcomfort", "momentum"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q03",
            "query": "fast PCIe 4.0 NVMe SSD storage 1TB or 2TB",
            "category": "Storage Devices",
            "constraints": {"category": "Storage Devices"},
            "relevant_product_ids": find_pids("Storage Devices", keywords=["nvme", "990", "sn850x", "t700"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q04",
            "query": "144Hz high refresh rate gaming monitor for PC setup",
            "category": "Monitors",
            "constraints": {"category": "Monitors"},
            "relevant_product_ids": find_pids("Monitors", keywords=["144hz", "165hz", "240hz", "ultragear"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q05",
            "query": "Apple iPhone with good battery and iOS",
            "category": "Smartphones",
            "constraints": {"category": "Smartphones", "brand": "Apple"},
            "relevant_product_ids": find_pids("Smartphones", keywords=["iphone"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q06",
            "query": "mechanical keyboard wireless with tactile switches",
            "category": "Keyboards",
            "constraints": {"category": "Keyboards"},
            "relevant_product_ids": find_pids("Keyboards", keywords=["mechanical", "wireless", "keychron"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q07",
            "query": "lightweight wireless mouse for competitive gaming and work",
            "category": "Mice",
            "constraints": {"category": "Mice"},
            "relevant_product_ids": find_pids("Mice", keywords=["wireless", "lightspeed", "dpi"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q08",
            "query": "productivity tablet with stylus support for college note taking",
            "category": "Tablets",
            "constraints": {"category": "Tablets"},
            "relevant_product_ids": find_pids("Tablets", keywords=["ipad", "tab", "stylus"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q09",
            "query": "smartwatch with GPS and heart rate tracking for running",
            "category": "Smartwatches",
            "constraints": {"category": "Smartwatches"},
            "relevant_product_ids": find_pids("Smartwatches", keywords=["gps", "heart rate", "garmin", "watch"], limit=6),
            "graded_relevance": {}
        },
        {
            "id": "eval-q10",
            "query": "budget smartphone under 35000 with 120Hz display and 5G",
            "category": "Smartphones",
            "constraints": {"category": "Smartphones", "budget_max": 35000.0},
            "relevant_product_ids": find_pids("Smartphones", max_price=35000.0, keywords=["120hz", "5g", "galaxy", "nord"], limit=6),
            "graded_relevance": {}
        }
    ]

    # Populate graded relevance: first 2 are 2 (highly relevant), rest are 1 (relevant)
    for q in test_queries:
        for idx, pid in enumerate(q["relevant_product_ids"]):
            q["graded_relevance"][pid] = 2 if idx < 2 else 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_queries, f, indent=2)

    logger.info(f"Built evaluation dataset with {len(test_queries)} queries at: {output_path}")
    return test_queries

if __name__ == "__main__":
    db = SessionLocal()
    try:
        tq = build_ground_truth_dataset(db)
        print(f"Generated {len(tq)} evaluation benchmark queries in {settings.EVALUATION_TESTSET_PATH}")
    finally:
        db.close()
