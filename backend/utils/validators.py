from typing import Dict, List, Any
from backend.models.user_profile import RiskTolerance, TimeHorizon

def validate_user_input(user_input: Dict[str, Any]) -> List[str]:
    """Validate user input data before creating UserProfile.
    
    Args:
        user_input: Dictionary containing user input data
        
    Returns:
        List of validation error messages, empty if validation passes
    """
    errors = []
    
    # Salary validation
    try:
        salary = float(user_input.get("salary", 0))
        if salary <= 0:
            errors.append("Salary must be greater than 0.")
    except (ValueError, TypeError):
        errors.append("Invalid salary value.")
    
    # Expenses validation
    try:
        expenses = float(user_input.get("expenses", 0))
        if expenses < 0:
            errors.append("Expenses cannot be negative.")
        if expenses >= salary:
            errors.append("Expenses should be less than salary for meaningful investment advice.")
    except (ValueError, TypeError):
        errors.append("Invalid expenses value.")
    
    # Age validation
    try:
        age = int(user_input.get("age", 0))
        if age < 18:
            errors.append("Age must be 18 or older.")
        if age > 100:
            errors.append("Age must be 100 or younger.")
    except (ValueError, TypeError):
        errors.append("Invalid age value.")
    
    # Risk tolerance validation
    risk_tolerance = user_input.get("risk_tolerance", "")
    if not risk_tolerance or risk_tolerance not in [e.value for e in RiskTolerance]:
        errors.append(f"Invalid risk tolerance. Must be one of: {', '.join([e.value for e in RiskTolerance])}")
    
    # Time horizon validation
    time_horizon = user_input.get("time_horizon", "")
    if not time_horizon or time_horizon not in [e.value for e in TimeHorizon]:
        errors.append(f"Invalid time horizon. Must be one of: {', '.join([e.value for e in TimeHorizon])}")
    
    # Goals validation
    goals = user_input.get("goals", "")
    if not goals or not goals.strip():
        errors.append("Financial goals cannot be empty.")
    
    # Loans validation
    loans = user_input.get("loans", "")
    if loans not in ["Yes", "No"]:
        errors.append("Please specify if you have any loans by selecting Yes or No.")
    
    return errors
