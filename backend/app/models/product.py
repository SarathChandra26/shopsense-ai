from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category_rel")

class Product(Base):
    __tablename__ = "products"

    id = Column(String(64), primary_key=True, index=True)  # stable alphanumeric id e.g. PROD-LAP-001
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), ForeignKey("product_categories.name"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False, index=True)  # in INR
    original_price = Column(Float, nullable=True)
    rating = Column(Float, default=4.0, index=True)
    review_count = Column(Integer, default=0)
    availability_status = Column(String(50), default="In Stock", index=True)
    image_url = Column(String(500), nullable=True)
    source = Column(String(100), default="synthetic_catalogue")
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category_rel = relationship("ProductCategory", back_populates="products")
    specifications = relationship("ProductSpecification", back_populates="product", cascade="all, delete-orphan")
    saved_by = relationship("SavedProduct", back_populates="product", cascade="all, delete-orphan")
    feedback = relationship("ProductFeedback", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_product_category_price", "category", "price"),
        Index("ix_product_brand_category", "brand", "category"),
    )

class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(64), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    spec_key = Column(String(100), nullable=False, index=True)  # e.g., "ram_gb", "processor", "gpu"
    spec_value = Column(String(255), nullable=False)           # e.g., "16 GB", "Intel Core i7-13700H"
    is_numeric = Column(Boolean, default=False)
    numeric_value = Column(Float, nullable=True, index=True)    # e.g., 16.0
    unit = Column(String(50), nullable=True)                    # e.g., "GB", "Hz", "hours", "g"

    product = relationship("Product", back_populates="specifications")

    __table_args__ = (
        Index("ix_spec_product_key", "product_id", "spec_key"),
        Index("ix_spec_key_numeric", "spec_key", "numeric_value"),
    )
