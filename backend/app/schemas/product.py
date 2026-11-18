from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class SpecificationItem(BaseModel):
    spec_key: str
    spec_value: str
    is_numeric: bool = False
    numeric_value: Optional[float] = None
    unit: Optional[str] = None

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    brand: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5)
    price: float = Field(..., ge=0)
    original_price: Optional[float] = Field(None, ge=0)
    rating: float = Field(4.0, ge=1.0, le=5.0)
    review_count: int = Field(0, ge=0)
    availability_status: str = Field("In Stock", max_length=50)
    image_url: Optional[str] = None
    source: str = "synthetic_catalogue"
    is_demo: bool = True

class ProductCreate(ProductBase):
    id: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    availability_status: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None

class ProductResponse(ProductBase):
    id: str
    specifications: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    total: int
    items: List[ProductResponse]
    page: int
    page_size: int
