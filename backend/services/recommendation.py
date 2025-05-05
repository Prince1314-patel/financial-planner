from backend.models.user_profile import UserProfile, RiskTolerance
from backend.models.portfolio import PortfolioRecommendation
from typing import Dict, Any
from datetime import datetime

def determine_risk_level(risk_score: float) -> str:
    """Determine the overall portfolio risk level based on the calculated risk score."""
    if risk_score < 1.0:
        return "Very Conservative"
    elif risk_score < 1.5:
        return "Conservative"
    elif risk_score < 2.0:
        return "Moderate Conservative"
    elif risk_score < 2.5:
        return "Moderate"
    elif risk_score < 3.0:
        return "Moderate Aggressive"
    else:
        return "Aggressive"

def validate_ai_result(ai_result: Dict[str, Any]) -> None:
    """Validate the AI result contains all required fields with appropriate values."""
    required_fields = ["allocations", "narrative", "next_steps"]
    for field in required_fields:
        if field not in ai_result:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(ai_result["allocations"], dict):
        raise ValueError("Allocations must be a dictionary")
    
    if not all(isinstance(v, (int, float)) for v in ai_result["allocations"].values()):
        raise ValueError("Allocation values must be numbers")

def generate_portfolio_recommendation(
    profile: UserProfile,
    metrics: Dict[str, Any],
    ai_result: Dict[str, Any]
) -> PortfolioRecommendation:
    """Generate a structured portfolio recommendation based on user profile and AI analysis.
    
    Args:
        profile: User's financial profile
        metrics: Calculated financial metrics
        ai_result: Raw AI recommendation output
        
    Returns:
        PortfolioRecommendation: Structured portfolio recommendation
        
    Raises:
        ValueError: If AI result is missing required fields or contains invalid data
    """
    # Validate AI result structure
    validate_ai_result(ai_result)
    
    # Determine overall risk level
    risk_level = determine_risk_level(metrics["risk_score"])
    
    # Convert allocation values to floats
    allocations = {k: float(v) for k, v in ai_result["allocations"].items()}
    
    return PortfolioRecommendation(
        allocations=allocations,
        narrative=ai_result["narrative"],
        next_steps=ai_result["next_steps"],
        risk_level=risk_level,
        generated_at=datetime.now()
    )
