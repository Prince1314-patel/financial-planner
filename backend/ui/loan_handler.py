import streamlit as st
from typing import Dict, Any, List

def render_loan_section() -> str:
    """Render the loan input section in the Streamlit form.
    
    Returns:
        String indicating whether user has loans or not
    """
    st.markdown("""
        <style>
        .loan-container {
            background: linear-gradient(45deg, rgba(75, 86, 210, 0.1), rgba(19, 99, 223, 0.1));
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .loan-title {
            color: #ffffff;
            margin-bottom: 1rem;
            font-size: 1.5rem;
            font-weight: 600;
        }
        </style>
        <div class="loan-container">
        <h3 class="loan-title">Outstanding Loans</h3>
    """, unsafe_allow_html=True)
    
    has_loans = st.toggle(
        "I have outstanding loans",
        value=False,
        help="Turn ON if you have any loans; turn OFF if you don't."
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return "Yes" if has_loans else "No"