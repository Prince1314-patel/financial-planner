import streamlit as st
from typing import Dict, Any, List
from backend.utils.validators import validate_user_input
from backend.models.user_profile import UserProfile
from backend.services.financial_engine import analyze_user_profile
from backend.services.ai_service import get_ai_recommendation
import re

def get_form_steps() -> List[Dict[str, str]]:
    """Get the list of form steps and their associated fields.
    
    Returns:
        List of dictionaries containing step titles and fields
    """
    return [
        {'title': 'Income & Loans', 'fields': ['salary', 'loans', 'expenses']},
        {'title': 'Personal Profile', 'fields': ['age', 'risk_tolerance', 'time_horizon']},
        {'title': 'Investments & Goals', 'fields': ['existing_investments', 'goals']}
    ]

def validate_step_fields(step_fields: List[str], user_input: Dict[str, Any]) -> List[str]:
    """Validate the fields for the current form step.
    
    Args:
        step_fields: List of fields to validate
        user_input: Dictionary containing user input data
        
    Returns:
        List of validation error messages
    """
    errors = []
    for field in step_fields:
        val = user_input.get(field, None)
        if field == 'salary' and (val is None or val <= 0):
            errors.append('Please enter a valid monthly salary.')
        elif field == 'expenses' and (val is None or val < 0):
            errors.append('Please enter your minimum monthly expenses.')
        elif field == 'age' and (val is None or val < 18):
            errors.append('Age must be 18 or older.')
        elif field == 'risk_tolerance' and val not in ['Conservative', 'Moderate', 'Aggressive']:
            errors.append('Select a valid risk tolerance.')
        elif field == 'time_horizon' and val not in ['<3 years', '3-5 years', '5-10 years', '>10 years']:
            errors.append('Select a valid investment time horizon.')
        elif field == 'goals' and (val is None or (isinstance(val, str) and not val.strip())) and field in step_fields:
            errors.append('Please enter at least one financial goal.')
        elif field == 'loans' and val is None:
            errors.append('Please specify if you have any loans by checking or unchecking the box.')
    return errors

def handle_form_navigation(
    submitted: bool = False,
    next_clicked: bool = False,
    back_clicked: bool = False,
    groq_api_key: str = None
) -> None:
    """Handle form navigation and submission logic.
    
    Args:
        submitted: Whether the form was submitted
        next_clicked: Whether the next button was clicked
        back_clicked: Whether the back button was clicked
        groq_api_key: API key for AI service
    """
    steps = get_form_steps()
    total_steps = len(steps)
    current_step = st.session_state['form_step']
    
    if back_clicked:
        st.session_state['form_step'] = max(0, current_step - 1)
        st.rerun()
    
    elif next_clicked:
        step_fields = steps[current_step]['fields']
        user_input = {k: st.session_state['form_data'][k] for k in step_fields}
        errors = validate_step_fields(step_fields, user_input)
        if errors:
            st.error("\n".join(errors))
        else:
            st.session_state['form_step'] = min(total_steps-1, current_step + 1)
            st.rerun()
    
    elif submitted:
        user_input = st.session_state['form_data']
        errors = validate_user_input(user_input)
        if errors:
            st.error("\n".join(errors))
        else:
            process_form_submission(user_input, groq_api_key)

def process_form_submission(user_input: Dict[str, Any], groq_api_key: str) -> None:
    """Process the form submission and generate recommendations.
    
    Args:
        user_input: Dictionary containing user input data
        groq_api_key: API key for AI service
    """
    profile = UserProfile(**user_input)
    metrics = analyze_user_profile(profile)
    
    with st.spinner("Consulting AI for your personalized recommendation..."):
        ai_result = get_ai_recommendation(profile, metrics, groq_api_key)
    
    # Process AI results
    narrative = ai_result['narrative']
    bullets = re.split(r'(?<=[.!?])\s+', narrative.strip())
    bullets = [b for b in bullets if b.strip()]
    
    # Calculate allocations
    allocations = ai_result["allocations"]
    investment_capacity = metrics.get("investment_capacity", 0)
    table_data = []
    for asset, pct in allocations.items():
        amount = round((pct / 100) * investment_capacity)
        table_data.append({
            "Asset Class": asset,
            "Percentage": f"{pct:.1f}%",
            "Amount (INR)": f"₹{amount:,.2f}"
        })
    
    # Update session state
    st.session_state.update({
        'ai_result': ai_result,
        'metrics': metrics,
        'table_data': table_data,
        'allocations': allocations,
        'bullets': bullets,
        'user_input': user_input
    })
    st.rerun()