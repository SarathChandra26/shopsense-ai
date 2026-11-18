from backend.app.database.session import Base
from backend.app.models.product import ProductCategory, Product, ProductSpecification
from backend.app.models.user import User
from backend.app.models.preference import UserPreference
from backend.app.models.interaction import SearchHistory, SavedProduct, ProductFeedback, RecommendationHistory
from backend.app.models.evaluation import EvaluationRun

__all__ = [
    "Base",
    "ProductCategory",
    "Product",
    "ProductSpecification",
    "User",
    "UserPreference",
    "SearchHistory",
    "SavedProduct",
    "ProductFeedback",
    "RecommendationHistory",
    "EvaluationRun",
]
