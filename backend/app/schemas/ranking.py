from typing import Optional
from pydantic import BaseModel, Field

class RankingWeights(BaseModel):
    semantic: float = Field(0.35, ge=0.0, le=1.0)
    keyword: float = Field(0.20, ge=0.0, le=1.0)
    specification: float = Field(0.20, ge=0.0, le=1.0)
    budget: float = Field(0.15, ge=0.0, le=1.0)
    rating: float = Field(0.10, ge=0.0, le=1.0)

    def normalize(self) -> "RankingWeights":
        total = self.semantic + self.keyword + self.specification + self.budget + self.rating
        if total <= 0:
            return RankingWeights()
        return RankingWeights(
            semantic=self.semantic / total,
            keyword=self.keyword / total,
            specification=self.specification / total,
            budget=self.budget / total,
            rating=self.rating / total
        )
