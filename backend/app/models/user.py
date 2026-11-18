from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)  # user ID e.g. "default_user" or UUID
    username = Column(String(100), default="Guest User")
    created_at = Column(DateTime, default=datetime.utcnow)

    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    searches = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    saved_products = relationship("SavedProduct", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("ProductFeedback", back_populates="user", cascade="all, delete-orphan")
