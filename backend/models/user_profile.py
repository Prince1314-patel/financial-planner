from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class RiskTolerance(str, Enum):
    CONSERVATIVE = "Conservative"
    MODERATE = "Moderate"
    AGGRESSIVE = "Aggressive"

class TimeHorizon(str, Enum):
    SHORT = "<3 years"
    MEDIUM = "3-5 years"
    LONG = "5-10 years"
    VERY_LONG = ">10 years"

class UserProfile(BaseModel):
    """User financial profile for portfolio recommendation.

    This model represents a user's financial profile including income, expenses,
    risk preferences, and investment goals.
    """
    salary: float = Field(..., gt=0, description="Monthly salary/income in INR")
    loans: str = Field(..., description="Whether user has outstanding loans (Yes/No)")
    expenses: float = Field(..., ge=0, description="Monthly minimum expenses in INR")
    age: int = Field(..., ge=18, le=100, description="User's age")
    risk_tolerance: RiskTolerance = Field(..., description="Investment risk tolerance level")
    time_horizon: TimeHorizon = Field(..., description="Investment time horizon")
    existing_investments: Optional[str] = Field(None, description="Optional details about existing investments")
    goals: str = Field(..., min_length=1, description="Financial goals like retirement, education, etc.")
    emergency_fund: float = Field(0, ge=0, description="Current emergency fund amount in INR")

    @validator('loans')
    def validate_loans(cls, v):
        if v not in ["Yes", "No"]:
            raise ValueError('Loans must be specified as Yes or No')
        return v

    @validator('goals')
    def validate_goals(cls, v):
        if not v.strip():
            raise ValueError('Financial goals cannot be empty')
        return v

    class Config:
        use_enum_values = True
