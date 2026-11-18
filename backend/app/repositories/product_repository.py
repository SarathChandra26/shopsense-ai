from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from backend.app.models.product import Product, ProductSpecification, ProductCategory
from backend.app.schemas.product import ProductCreate, ProductUpdate
from backend.app.core.logging import logger

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_ids(self, product_ids: List[str]) -> List[Product]:
        if not product_ids:
            return []
        return self.db.query(Product).filter(Product.id.in_(product_ids)).all()

    def get_by_name_and_brand(self, name: str, brand: str) -> Optional[Product]:
        return self.db.query(Product).filter(
            Product.name == name,
            Product.brand == brand
        ).first()

    def list_products(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        availability: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[int, List[Product]]:
        query = self.db.query(Product)
        if category:
            query = query.filter(Product.category == category)
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if min_rating is not None:
            query = query.filter(Product.rating >= min_rating)
        if availability:
            query = query.filter(Product.availability_status == availability)

        total = query.count()
        items = query.order_by(Product.rating.desc(), Product.price.asc()).offset(skip).limit(limit).all()
        return total, items

    def get_all_product_ids(self) -> List[str]:
        results = self.db.query(Product.id).all()
        return [r[0] for r in results]

    def create(self, product_in: ProductCreate) -> Product:
        # Generate ID if absent
        prod_id = product_in.id
        if not prod_id:
            import uuid
            prefix = product_in.category[:3].upper() if product_in.category else "PRD"
            prod_id = f"PROD-{prefix}-{uuid.uuid4().hex[:8].upper()}"

        db_product = Product(
            id=prod_id,
            name=product_in.name,
            brand=product_in.brand,
            category=product_in.category,
            description=product_in.description,
            price=product_in.price,
            original_price=product_in.original_price,
            rating=product_in.rating,
            review_count=product_in.review_count,
            availability_status=product_in.availability_status,
            image_url=product_in.image_url,
            source=product_in.source,
            is_demo=product_in.is_demo
        )
        self.db.add(db_product)
        self.db.flush()

        # Add specifications
        if product_in.specifications:
            for k, v in product_in.specifications.items():
                is_num = False
                num_val = None
                unit = None
                if isinstance(v, (int, float)):
                    is_num = True
                    num_val = float(v)
                elif isinstance(v, str):
                    # Try parsing numbers e.g. "16 GB" -> 16.0
                    import re
                    match = re.match(r"^([\d.]+)\s*([a-zA-Z%]+)?$", v.strip())
                    if match:
                        try:
                            num_val = float(match.group(1))
                            is_num = True
                            unit = match.group(2)
                        except ValueError:
                            pass
                
                spec = ProductSpecification(
                    product_id=prod_id,
                    spec_key=k,
                    spec_value=str(v),
                    is_numeric=is_num,
                    numeric_value=num_val,
                    unit=unit
                )
                self.db.add(spec)

        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def update(self, product_id: str, product_update: ProductUpdate) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if not product:
            return None

        update_data = product_update.dict(exclude_unset=True)
        specs_data = update_data.pop("specifications", None)

        for field, value in update_data.items():
            setattr(product, field, value)

        if specs_data is not None:
            # Delete old specs and replace
            self.db.query(ProductSpecification).filter(
                ProductSpecification.product_id == product_id
            ).delete()
            
            for k, v in specs_data.items():
                is_num = isinstance(v, (int, float))
                num_val = float(v) if is_num else None
                spec = ProductSpecification(
                    product_id=product_id,
                    spec_key=k,
                    spec_value=str(v),
                    is_numeric=is_num,
                    numeric_value=num_val
                )
                self.db.add(spec)

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: str) -> bool:
        product = self.get_by_id(product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()
        return True

    def format_product_dict(self, p: Product) -> Dict[str, Any]:
        """Convert Product ORM instance into serializable dict with specs."""
        specs = {}
        for s in p.specifications:
            specs[s.spec_key] = s.numeric_value if s.is_numeric and s.numeric_value is not None else s.spec_value
            
        return {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "description": p.description,
            "price": p.price,
            "original_price": p.original_price,
            "rating": p.rating,
            "review_count": p.review_count,
            "availability_status": p.availability_status,
            "image_url": p.image_url,
            "source": p.source,
            "is_demo": p.is_demo,
            "specifications": specs,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
