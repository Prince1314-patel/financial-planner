from backend.models.user_profile import UserProfile, RiskTolerance, TimeHorizon
from typing import Dict, Any
from datetime import datetime
from backend.utils.formatters import format_currency, format_percentage, format_number

def calculate_risk_score(risk_tolerance: RiskTolerance, age: int, time_horizon: TimeHorizon) -> float:
    """Calculate a normalized risk score based on user's risk tolerance, age, and investment horizon."""
    # Base risk score from risk tolerance
    base_score = {
        RiskTolerance.CONSERVATIVE: 1.0,
        RiskTolerance.MODERATE: 2.0,
        RiskTolerance.AGGRESSIVE: 3.0
    }[risk_tolerance]
    
    # Age factor (decreases risk as age increases)
    age_factor = max(0.5, (100 - age) / 100)
    
    # Time horizon factor (increases risk for longer horizons)
    horizon_factor = {
        TimeHorizon.SHORT: 0.8,
        TimeHorizon.MEDIUM: 1.0,
        TimeHorizon.LONG: 1.2,
        TimeHorizon.VERY_LONG: 1.4
    }[time_horizon]
    
    return round(base_score * age_factor * horizon_factor, 2)

def analyze_user_profile(profile: UserProfile) -> Dict[str, Any]:
    """Analyze user profile to generate comprehensive financial metrics.
    
    Args:
        profile: User's financial profile including income, expenses, and preferences
        
    Returns:
        Dictionary containing calculated financial metrics and risk assessment
    """
    # Calculate disposable income
    disposable_income = max(0, profile.salary - profile.expenses)
    
    # Calculate lifestyle allocation for young users
    lifestyle_allocation = 0
    if profile.age <= 25 and disposable_income > 5000:
        # Allocate 25% of disposable income for lifestyle/entertainment
        lifestyle_allocation = round(disposable_income * 0.25)
        investment_capacity = disposable_income - lifestyle_allocation
    else:
        investment_capacity = disposable_income
    
    # Calculate risk score
    risk_score = calculate_risk_score(
        profile.risk_tolerance,
        profile.age,
        profile.time_horizon
    )
    
    # Parse loan information (basic implementation)
    has_loans = bool(profile.loans.strip())
    
    metrics = {
        "investment_capacity": investment_capacity,
        "lifestyle_allocation": lifestyle_allocation,
        "monthly_savings_ratio": float(format_percentage(investment_capacity / profile.salary * 100, 2).rstrip('%')) if profile.salary > 0 else 0,
        "risk_score": float(format_number(risk_score, 2)),
        "age": profile.age,
        "has_loans": has_loans,
        "time_horizon": profile.time_horizon,
        "analysis_timestamp": datetime.now().isoformat(),
        "emergency_fund_target": profile.expenses * 6  # 6 months of expenses
    }
    
    return metrics
