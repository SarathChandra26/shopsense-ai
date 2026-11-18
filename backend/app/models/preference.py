from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    preferred_categories = Column(Text, nullable=True)  # JSON or comma-separated list
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    preferred_brands = Column(Text, nullable=True)      # JSON or comma-separated list
    intended_usage = Column(Text, nullable=True)        # e.g., "coding, machine learning, gaming"
    preferred_specs = Column(Text, nullable=True)       # JSON dict: {"ram_gb": 16, "gpu_required": True}
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")
