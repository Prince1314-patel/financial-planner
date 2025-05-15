import streamlit as st

import os
import load_dotenv

from backend.ui.session_state import initialize_session_state
from backend.ui.form_navigation import get_form_steps, handle_form_navigation
from backend.ui.loan_handler import render_loan_section
from backend.ui.visualization import (
    create_allocation_chart,
    display_metrics_table,
    display_allocation_table,
    display_recommendation_bullets,
    create_risk_return_chart,
    download_excel_report
)

load_dotenv()
# Load secrets
def load_groq_api_key():
    """Load the GROQ API key from the .env file."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get GROQ API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")
    return GROQ_API_KEY

def main():
    st.set_page_config(page_title="AI Financial Advisor", layout="centered")
    
    # Add custom CSS for better UI
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        .main > div {
            padding: 2rem;
            border-radius: 15px;
            background: linear-gradient(45deg, rgba(75, 86, 210, 0.1), rgba(19, 99, 223, 0.1));
            border: 1px solid rgba(255,255,255,0.1);
        }
        h1 {
            color: #ffffff;
            margin-bottom: 1.5rem;
        }
        .stButton button {
            width: 100%;
            border-radius: 8px;
            background: linear-gradient(45deg, #4B56D2, #47B5FF);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
        }
        .stButton button:hover {
            background: linear-gradient(45deg, #47B5FF, #4B56D2);
        }
        .stSelectbox > div > div {
            background-color: rgba(0,0,0,0.2) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
        }
        .stTextInput > div > div > input {
            background-color: rgba(0,0,0,0.2) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
        }
        .stNumberInput > div > div > input {
            background-color: rgba(0,0,0,0.2) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
        }
        .stTextArea > div > div > textarea {
            background-color: rgba(0,0,0,0.2) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
        }
        .stProgress > div > div > div {
            background: linear-gradient(45deg, #4B56D2, #47B5FF) !important;
        }
        .stExpander {
            background: rgba(0,0,0,0.2) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("AI Financial Advisor: Portfolio Diversification")
    st.markdown("""
    <div style='background: linear-gradient(45deg, rgba(75, 86, 210, 0.2), rgba(19, 99, 223, 0.2));
         padding: 1rem; border-radius: 15px; margin-bottom: 2rem; border: 1px solid rgba(255,255,255,0.1);'>
    Welcome! Get personalized, AI-powered portfolio diversification advice. No login required. No data is stored.
    </div>
    """, unsafe_allow_html=True)
    
    # Display essential financial rules and tips
    with st.expander("Essential Investing Rules & Tips", expanded=True):
        st.markdown("""
        **Essential Financial Rules for Investing & Diversification:**

        1. **The Rule of 100:** Subtract your age from 100 to estimate the % of your portfolio in equities; the rest in bonds/fixed income.
        2. **Emergency Fund:** Always keep 3–6 months of expenses in an emergency fund before investing.
        3. **Diversify:** Mix asset classes—equities, bonds, real estate, gold, etc.
        4. **Align With Risk Tolerance:** Match your portfolio to your risk comfort.
        5. **Time Horizon:** Invest conservatively if you need money soon; take more risk if investing for the long term.
        6. **Rebalance:** Regularly review and adjust your portfolio.
        7. **Avoid Market Timing:** Invest regularly instead of trying to time the market.
        8. **Minimize Costs:** Prefer low-cost index funds/ETFs.
        9. **Tax Efficiency:** Consider tax impacts (long/short-term gains).
        10. **Set Clear Goals:** Know your investment objectives and match your strategy.

        *These rules will help guide your investment decisions and the AI's recommendations.*
        """)
    
    # Initialize session state
    initialize_session_state()
    
    # Get form steps and current step
    steps = get_form_steps()
    total_steps = len(steps)
    current_step = st.session_state['form_step']
    
    # Display progress bar
    st.progress((current_step+1)/total_steps, text=f"Step {current_step+1} of {total_steps}: {steps[current_step]['title']}")
    
    # Form for current step
    with st.form(key=f"financial_profile_form_{current_step}"):
        st.subheader(f"{steps[current_step]['title']}")
        
        # Step 1: Income & Emergency Fund
        if current_step == 0:
            col1, col2 = st.columns(2)
            
            with col1:
                salary = st.number_input(
                    "Monthly Salary/Income (INR)",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    value=float(st.session_state['form_data']['salary']),
                    help="Your total monthly take-home income"
                )
                
                expenses = st.number_input(
                    "Monthly Minimum Expenses (INR)",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    value=float(st.session_state['form_data']['expenses']),
                    help="Essential monthly expenses including EMIs"
                )
            
            with col2:
                emergency_fund = st.number_input(
                    "Emergency Fund (INR)",
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f",
                    value=float(st.session_state['form_data'].get('emergency_fund', 0.0)),
                    help="Current emergency fund savings"
                )
                
                emergency_months = st.slider(
                    "Desired Emergency Fund (months of expenses)",
                    min_value=3,
                    max_value=12,
                    value=int(st.session_state['form_data'].get('emergency_months', 6)),
                    help="How many months of expenses you want to keep as emergency fund"
                )
            
            st.session_state['form_data']['salary'] = salary
            st.session_state['form_data']['expenses'] = expenses
            st.session_state['form_data']['emergency_fund'] = emergency_fund
            st.session_state['form_data']['emergency_months'] = emergency_months
            
            # Handle loans section inside form
            loans = render_loan_section()
            st.session_state['form_data']['loans'] = loans
        
        # Step 2: Personal Profile
        elif current_step == 1:
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input(
                    "Age",
                    min_value=18,
                    max_value=100,
                    value=st.session_state['form_data']['age'],
                    help="Your current age"
                )
                
                risk_tolerance = st.select_slider(
                    "Risk Tolerance",
                    options=['Conservative', 'Moderate', 'Aggressive'],
                    value=st.session_state['form_data']['risk_tolerance'],
                    help="Your comfort level with investment risk"
                )
            
            with col2:
                time_horizon = st.select_slider(
                    "Investment Time Horizon",
                    options=['<3 years', '3-5 years', '5-10 years', '>10 years'],
                    value=st.session_state['form_data']['time_horizon'],
                    help="How long you plan to stay invested"
                )
            
            st.session_state['form_data']['age'] = age
            st.session_state['form_data']['risk_tolerance'] = risk_tolerance
            st.session_state['form_data']['time_horizon'] = time_horizon
        
        # Step 3: Investments & Goals
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                existing_investments = st.text_area(
                    "Existing Investments (Optional)",
                    value=st.session_state['form_data']['existing_investments'],
                    help="Brief description of your current investments"
                )
            
            with col2:
                goals = st.text_area(
                    "Financial Goals",
                    value=st.session_state['form_data']['goals'],
                    help="Your investment objectives"
                )
            
            st.session_state['form_data']['existing_investments'] = existing_investments
            st.session_state['form_data']['goals'] = goals
        
        # Navigation buttons
        cols = st.columns([1, 1, 1])
        with cols[0]:
            back = st.form_submit_button("← Back") if current_step > 0 else None
        with cols[1]:
            next = st.form_submit_button("Next →") if current_step < total_steps - 1 else None
        with cols[2]:
            submit = st.form_submit_button("Get Advice 💸") if current_step == total_steps - 1 else None
    
    # Handle form navigation
    groq_api_key = load_groq_api_key()
    handle_form_navigation(
        submitted=bool(submit),
        next_clicked=bool(next),
        back_clicked=bool(back),
        groq_api_key=groq_api_key
    )
    
    # Display results if available
    if st.session_state['ai_result']:
        st.markdown("""
        <div style='background: linear-gradient(45deg, rgba(75, 86, 210, 0.1), rgba(19, 99, 223, 0.1));
             padding: 2rem; border-radius: 15px; margin: 2rem 0; border: 1px solid rgba(255,255,255,0.1);'>
        <h2 style='color: #ffffff; margin-bottom: 1.5rem;'>Your Personalized Financial Analysis</h2>
        """, unsafe_allow_html=True)
        
        # Display metrics and recommendations
        display_metrics_table(st.session_state['metrics'])
        
        # Download Excel Report Button
        download_excel_report(
            st.session_state['metrics'],
            st.session_state['allocations'],
            st.session_state['table_data'],
            st.session_state['bullets']
        )
        
        # Portfolio Visualization
        st.markdown("<h3 style='color: #ffffff; margin: 2rem 0 1rem;'>Portfolio Visualization</h3>", unsafe_allow_html=True)
        
        # Display plots vertically
        st.plotly_chart(create_allocation_chart(st.session_state['allocations']), use_container_width=True)
        st.plotly_chart(create_risk_return_chart(st.session_state['allocations']), use_container_width=True)
        
        # Display allocation table
        display_allocation_table(st.session_state['table_data'])
        
        # AI Recommendations with dropdown
        st.markdown("<h3 style='color: #ffffff; margin: 2rem 0 1rem;'>Investment Strategy</h3>", unsafe_allow_html=True)
        
        with st.expander("🎯 AI Investment Recommendations", expanded=True):
            display_recommendation_bullets(st.session_state['bullets'])
        
        # Next Steps with dropdown
        with st.expander("📋 Next Steps", expanded=True):
            st.markdown("""
            <style>
            .next-step {
                background: rgba(0,0,0,0.2);
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                border: 1px solid rgba(255,255,255,0.05);
            }
            </style>
            """, unsafe_allow_html=True)
            
            next_steps = [
                "1. Review and understand your recommended portfolio allocation",
                "2. Set up or increase your emergency fund as recommended",
                "3. Research low-cost index funds/ETFs that match your allocation",
                "4. Open a trading account if you don't have one",
                "5. Start implementing the investment plan gradually",
                "6. Set up automatic monthly investments if possible",
                "7. Schedule quarterly portfolio reviews",
                "8. Consider consulting with a tax advisor for tax-efficient investing"
            ]
            
            for step in next_steps:
                st.markdown(f"<div class='next-step'>{step}</div>", unsafe_allow_html=True)
        
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()