import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.session import SessionLocal
from backend.app.database.fts_index import index_product_fts
from backend.app.repositories.product_repository import ProductRepository
from backend.app.ingestion.validator import validate_product_data
from backend.app.embeddings.embedder import get_embedder, ProductEmbedder
from backend.app.vector_store.chroma_client import get_vector_store

def import_products_from_csv(
    csv_path: Path,
    db: Session,
    batch_size: int = 64
) -> Dict[str, Any]:
    """
    Import products from a CSV file into:
    1. SQLite relational tables
    2. SQLite FTS5 full-text search table
    3. ChromaDB vector database
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")

    logger.info(f"Starting product import from CSV: {csv_path}")
    repo = ProductRepository(db)
    embedder = get_embedder()
    vector_store = get_vector_store()

    inserted_count = 0
    updated_count = 0
    error_count = 0

    pending_vector_ids = []
    pending_vector_texts = []
    pending_vector_metas = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse specifications if stringified JSON
            specs = row.get("specifications", "{}")
            if isinstance(specs, str):
                try:
                    specs = json.loads(specs)
                except Exception:
                    specs = {}
            row["specifications"] = specs

            is_valid, errors, validated_prod = validate_product_data(row)
            if not is_valid or not validated_prod:
                error_count += 1
                logger.warning(f"Skipping invalid row: {errors}")
                continue

            # Check if product already exists by ID
            existing = None
            if validated_prod.id:
                existing = repo.get_by_id(validated_prod.id)
            elif validated_prod.name and validated_prod.brand:
                existing = repo.get_by_name_and_brand(validated_prod.name, validated_prod.brand)

            if existing:
                # Update existing
                from backend.app.schemas.product import ProductUpdate
                update_in = ProductUpdate(
                    name=validated_prod.name,
                    brand=validated_prod.brand,
                    category=validated_prod.category,
                    description=validated_prod.description,
                    price=validated_prod.price,
                    original_price=validated_prod.original_price,
                    rating=validated_prod.rating,
                    review_count=validated_prod.review_count,
                    availability_status=validated_prod.availability_status,
                    specifications=validated_prod.specifications
                )
                db_prod = repo.update(existing.id, update_in)
                prod_id = existing.id
                updated_count += 1
            else:
                db_prod = repo.create(validated_prod)
                prod_id = db_prod.id
                inserted_count += 1

            # Prepare searchable text for FTS and ChromaDB
            prod_dict = repo.format_product_dict(db_prod)
            searchable_text = ProductEmbedder.build_searchable_text(prod_dict)

            # Update FTS5 index
            specs_summary = "; ".join([f"{k}: {v}" for k, v in prod_dict.get("specifications", {}).items()])
            index_product_fts(
                db=db,
                product_id=prod_id,
                name=db_prod.name,
                brand=db_prod.brand,
                category=db_prod.category,
                description=db_prod.description,
                specifications_text=specs_summary
            )

            # Buffer for batch embedding
            pending_vector_ids.append(prod_id)
            pending_vector_texts.append(searchable_text)
            pending_vector_metas.append({
                "product_id": prod_id,
                "name": db_prod.name,
                "brand": db_prod.brand,
                "category": db_prod.category,
                "price": float(db_prod.price),
                "rating": float(db_prod.rating),
                "availability": db_prod.availability_status
            })

            # Flush vector batch when full
            if len(pending_vector_ids) >= batch_size:
                embs = embedder.encode_batch(pending_vector_texts)
                vector_store.upsert_products_batch(
                    ids=pending_vector_ids,
                    embeddings=embs,
                    documents=pending_vector_texts,
                    metadatas=pending_vector_metas
                )
                pending_vector_ids.clear()
                pending_vector_texts.clear()
                pending_vector_metas.clear()
                logger.info(f"Indexed batch into ChromaDB. Progress: {inserted_count + updated_count} products.")

    # Flush remaining batch
    if pending_vector_ids:
        embs = embedder.encode_batch(pending_vector_texts)
        vector_store.upsert_products_batch(
            ids=pending_vector_ids,
            embeddings=embs,
            documents=pending_vector_texts,
            metadatas=pending_vector_metas
        )
        pending_vector_ids.clear()
        pending_vector_texts.clear()
        pending_vector_metas.clear()

    summary = {
        "inserted": inserted_count,
        "updated": updated_count,
        "errors": error_count,
        "total_processed": inserted_count + updated_count,
        "total_in_chroma": vector_store.get_count()
    }
    logger.info(f"Product import completed: {summary}")
    return summary

if __name__ == "__main__":
    db = SessionLocal()
    try:
        res = import_products_from_csv(settings.PRODUCTS_CSV_PATH, db)
        print("Import Results:", res)
    finally:
        db.close()
