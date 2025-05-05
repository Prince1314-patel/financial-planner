import streamlit as st
from typing import Dict, Any

def initialize_session_state() -> None:
    """Initialize the Streamlit session state with default values.
    
    This function sets up the initial state for the application, including form data
    and result storage.
    """
    defaults = {
        'form_step': 0,
        'form_data': {
            'salary': 0.0,
            'loans': 'No',
            'expenses': 0.0,
            'emergency_fund': 0.0,
            'emergency_months': 6,
            'age': 18,
            'risk_tolerance': 'Moderate',
            'time_horizon': '5-10 years',
            'existing_investments': '',
            'goals': ''
        },
        'ai_result': None,
        'metrics': None,
        'table_data': None,
        'allocations': None,
        'bullets': None,
        'user_input': None,
    }
    
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_session_data(key: str) -> Any:
    """Get data from the session state.
    
    Args:
        key: The key to retrieve from session state
        
    Returns:
        The value associated with the key
    """
    return st.session_state.get(key)

def update_session_data(key: str, value: Any) -> None:
    """Update data in the session state.
    
    Args:
        key: The key to update in session state
        value: The new value to set
    """
    st.session_state[key] = value

def update_form_data(field: str, value: Any) -> None:
    """Update a specific field in the form data.
    
    Args:
        field: The form field to update
        value: The new value for the field
    """
    st.session_state['form_data'][field] = value

def clear_session_state() -> None:
    """Clear all data from the session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()