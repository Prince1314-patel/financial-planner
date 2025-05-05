from pydantic import BaseModel, Field, validator
from typing import Dict, List
from datetime import datetime

class PortfolioRecommendation(BaseModel):
    """Portfolio recommendation model containing asset allocations and advice.

    This model represents a complete investment portfolio recommendation including
    asset allocations, narrative explanation, and actionable next steps.
    """
    allocations: Dict[str, float] = Field(
        ...,
        description="Asset allocation percentages",
        example={"Stocks": 60.0, "Bonds": 30.0, "Cash": 10.0}
    )
    narrative: str = Field(
        ...,
        min_length=10,
        description="Detailed explanation of the investment strategy"
    )
    next_steps: str = Field(
        ...,
        min_length=10,
        description="Actionable steps for implementing the recommendation"
    )
    risk_level: str = Field(
        ...,
        description="Overall risk level of the portfolio"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the recommendation was generated"
    )

    @validator('allocations')
    def validate_allocations(cls, v):
        if not v:
            raise ValueError('Allocations cannot be empty')
        total = sum(v.values())
        if not (99.0 <= total <= 101.0):  # Allow for small floating-point differences
            raise ValueError(f'Allocation percentages must sum to 100% (got {total}%)')
        return v
