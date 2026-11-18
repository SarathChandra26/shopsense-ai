from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse
)
from backend.app.repositories.product_repository import ProductRepository
from backend.app.database.fts_index import index_product_fts, delete_product_fts
from backend.app.embeddings.embedder import get_embedder, ProductEmbedder
from backend.app.vector_store.chroma_client import get_vector_store
from backend.app.core.config import settings

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=ProductListResponse)
def list_products(
    category: Optional[str] = Query(None, description="Filter by product category"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    availability: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    repo = ProductRepository(db)
    skip = (page - 1) * page_size
    total, items = repo.list_products(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        availability=availability,
        skip=skip,
        limit=page_size
    )
    formatted = [ProductResponse(**repo.format_product_dict(p)) for p in items]
    return ProductListResponse(
        total=total,
        items=formatted,
        page=page,
        page_size=page_size
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    p = repo.get_by_id(product_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")
    return ProductResponse(**repo.format_product_dict(p))

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    
    # Check duplicate
    if product_in.id and repo.get_by_id(product_in.id):
        raise HTTPException(status_code=409, detail=f"Product with ID '{product_in.id}' already exists.")

    p = repo.create(product_in)
    p_dict = repo.format_product_dict(p)

    # 1. Update SQLite FTS5 index
    specs_str = "; ".join([f"{k}: {v}" for k, v in p_dict.get("specifications", {}).items()])
    index_product_fts(
        db=db,
        product_id=p.id,
        name=p.name,
        brand=p.brand,
        category=p.category,
        description=p.description,
        specifications_text=specs_str
    )

    # 2. Incrementally index into ChromaDB
    embedder = get_embedder()
    vector_store = get_vector_store()
    doc_text = ProductEmbedder.build_searchable_text(p_dict)
    emb = embedder.encode_text(doc_text)
    vector_store.upsert_product(
        product_id=p.id,
        embedding=emb,
        document=doc_text,
        metadata={
            "product_id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "price": float(p.price),
            "rating": float(p.rating),
            "availability": p.availability_status
        }
    )

    return ProductResponse(**p_dict)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, product_update: ProductUpdate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    p = repo.update(product_id, product_update)
    if not p:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")

    p_dict = repo.format_product_dict(p)

    # 1. Update SQLite FTS5 index
    specs_str = "; ".join([f"{k}: {v}" for k, v in p_dict.get("specifications", {}).items()])
    index_product_fts(
        db=db,
        product_id=p.id,
        name=p.name,
        brand=p.brand,
        category=p.category,
        description=p.description,
        specifications_text=specs_str
    )

    # 2. Incrementally update vector in ChromaDB
    embedder = get_embedder()
    vector_store = get_vector_store()
    doc_text = ProductEmbedder.build_searchable_text(p_dict)
    emb = embedder.encode_text(doc_text)
    vector_store.upsert_product(
        product_id=p.id,
        embedding=emb,
        document=doc_text,
        metadata={
            "product_id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "price": float(p.price),
            "rating": float(p.rating),
            "availability": p.availability_status
        }
    )

    return ProductResponse(**p_dict)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    success = repo.delete(product_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")

    # Remove from FTS and ChromaDB
    delete_product_fts(db, product_id)
    vector_store = get_vector_store()
    vector_store.delete_product(product_id)
    return None

@router.post("/import")
def import_catalogue(
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    from backend.app.ingestion.importer import import_products_from_csv
    
    target_path = settings.PRODUCTS_CSV_PATH
    if file:
        content = file.file.read()
        temp_import_path = settings.DATA_DIR / f"uploaded_{file.filename}"
        with open(temp_import_path, "wb") as f:
            f.write(content)
        target_path = temp_import_path

    summary = import_products_from_csv(target_path, db)
    return {"message": "Catalogue imported successfully", "summary": summary}
