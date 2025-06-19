import streamlit as st
import os
from dotenv import load_dotenv

# Initialize database first
from backend.database.database import init_db
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")

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
from backend.ui.auth_components import check_authentication, render_user_menu
from backend.ui.dashboard import render_dashboard, render_portfolio_comparison
from backend.services.portfolio_service import PortfolioService
from backend.services.market_service import MarketService
from backend.services.enhanced_financial_engine import EnhancedFinancialEngine
from backend.services.advanced_report_generator import AdvancedReportGenerator
from backend.ui.enhanced_analysis_components import (
    render_financial_health_dashboard,
    render_personalized_insights,
    render_what_if_scenarios,
    render_advanced_portfolio_analysis,
    render_goal_progress_tracker,
    render_market_context_integration,
    render_tax_optimization_planner,
    render_comprehensive_report_generator
)
from backend.database.database import SessionLocal
from backend.services.auth_service import AuthService
from backend.models.user_profile import UserProfile

load_dotenv()

def load_groq_api_key():
    """Load the GROQ API key from the .env file."""
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")
    return GROQ_API_KEY

def add_custom_css():
    """Add custom CSS for better UI"""
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
        .nav-button {
            margin: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(0,0,0,0.2);
            color: white;
            text-decoration: none;
        }
        .nav-button:hover {
            background: rgba(75, 86, 210, 0.3);
        }
        .nav-button.active {
            background: linear-gradient(45deg, #4B56D2, #47B5FF);
        }
        </style>
    """, unsafe_allow_html=True)

def render_navigation():
    """Render navigation menu"""
    current_user = AuthService.get_current_user()
    if not current_user:
        return
    
    # Initialize current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Financial Analysis'
    
    # Navigation in sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        
        pages = {
            "📊 Dashboard": "Dashboard",
            "💰 Financial Analysis": "Financial Analysis", 
            "📈 Portfolio Comparison": "Portfolio Comparison",
            "🌍 Market Data": "Market Data"
        }
        
        for display_name, page_name in pages.items():
            if st.button(display_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

def update_market_data_background():
    """Update market data in background"""
    try:
        db = SessionLocal()
        
        # Get default symbols
        all_symbols = []
        for symbols in MarketService.DEFAULT_SYMBOLS.values():
            all_symbols.extend(symbols)
        
        # Fetch and save market data
        market_data = MarketService.get_market_data(all_symbols[:10])  # Limit to avoid rate limits
        if market_data:
            MarketService.save_market_data(db, market_data)
        
        db.close()
    except Exception as e:
        # Silent fail for background updates
        pass

def render_financial_analysis_page():
    """Render the main financial analysis page"""
    st.title("AI Financial Advisor: Portfolio Diversification")
    st.markdown("""
    <div style='background: linear-gradient(45deg, rgba(75, 86, 210, 0.2), rgba(19, 99, 223, 0.2));
         padding: 1rem; border-radius: 15px; margin-bottom: 2rem; border: 1px solid rgba(255,255,255,0.1);'>
    Get personalized, AI-powered portfolio diversification advice. Your data is saved to track your progress over time.
    </div>
    """, unsafe_allow_html=True)
    
    # Display essential financial rules and tips
    with st.expander("Essential Investing Rules & Tips", expanded=False):
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
    
    # Enhanced form navigation with database saving
    if submit or next or back:
        db = SessionLocal()
        try:
            # Save financial profile when form is submitted
            if submit:
                financial_profile = PortfolioService.save_financial_profile(db, st.session_state['form_data'])
                st.session_state['current_financial_profile_id'] = financial_profile.id if financial_profile else None
                
                # Enhanced financial analysis
                if financial_profile:
                    current_user = AuthService.get_current_user()
                    user_id = current_user['id'] if current_user else 0
                    
                    # Create UserProfile object for enhanced analysis
                    user_profile = UserProfile(
                        salary=st.session_state['form_data']['salary'],
                        loans=st.session_state['form_data'].get('loans', 'No'),
                        expenses=st.session_state['form_data']['expenses'],
                        age=st.session_state['form_data']['age'],
                        risk_tolerance=st.session_state['form_data']['risk_tolerance'],
                        time_horizon=st.session_state['form_data']['time_horizon'],
                        existing_investments=st.session_state['form_data'].get('existing_investments', ''),
                        goals=st.session_state['form_data']['goals']
                    )
                    
                    # Calculate enhanced metrics
                    enhanced_metrics = EnhancedFinancialEngine.calculate_advanced_metrics(
                        user_profile, db, user_id
                    )
                    
                    # Generate personalized allocation
                    enhanced_allocations = EnhancedFinancialEngine.generate_personalized_allocation(
                        user_profile, enhanced_metrics
                    )
                    
                    # Store enhanced data in session
                    st.session_state['enhanced_metrics'] = enhanced_metrics
                    st.session_state['enhanced_allocations'] = enhanced_allocations
                    st.session_state['user_profile_data'] = user_profile.dict()
            
            # Handle navigation
            handle_form_navigation(
                submitted=bool(submit),
                next_clicked=bool(next),
                back_clicked=bool(back),
                groq_api_key=groq_api_key
            )
            
            # Save portfolio if analysis was completed
            if submit and st.session_state.get('ai_result') and st.session_state.get('current_financial_profile_id'):
                # Use enhanced allocations if available
                allocations_to_save = st.session_state.get('enhanced_allocations', st.session_state.get('allocations', {}))
                metrics_to_save = st.session_state.get('enhanced_metrics', st.session_state.get('metrics', {}))
                
                portfolio = PortfolioService.save_portfolio(
                    db,
                    st.session_state['current_financial_profile_id'],
                    allocations_to_save,
                    metrics_to_save,
                    st.session_state.get('ai_narrative', ''),
                    st.session_state.get('ai_recommendations', ''),
                    st.session_state.get('risk_level', 'Moderate')
                )
                if portfolio:
                    st.success("✅ Enhanced portfolio analysis saved successfully! View it in your Dashboard.")
        
        finally:
            db.close()
    
    # Display results if available
    if st.session_state['ai_result']:
        st.markdown("""
        <div style='background: linear-gradient(45deg, rgba(75, 86, 210, 0.1), rgba(19, 99, 223, 0.1));
             padding: 2rem; border-radius: 15px; margin: 2rem 0; border: 1px solid rgba(255,255,255,0.1);'>
        <h2 style='color: #ffffff; margin-bottom: 1.5rem;'>🚀 Your Enhanced Financial Analysis</h2>
        """, unsafe_allow_html=True)
        
        # Use enhanced metrics if available
        metrics_to_display = st.session_state.get('enhanced_metrics', st.session_state.get('metrics', {}))
        allocations_to_display = st.session_state.get('enhanced_allocations', st.session_state.get('allocations', {}))
        user_profile_data = st.session_state.get('user_profile_data', {})
        
        # Financial Health Dashboard
        if metrics_to_display:
            render_financial_health_dashboard(metrics_to_display)
            st.markdown("---")
        
        # Personalized Insights
        if metrics_to_display and user_profile_data:
            render_personalized_insights(metrics_to_display, user_profile_data)
            st.markdown("---")
        
        # What-If Scenarios
        if metrics_to_display:
            render_what_if_scenarios(metrics_to_display)
            st.markdown("---")
        
        # Advanced Portfolio Analysis
        if allocations_to_display and metrics_to_display:
            render_advanced_portfolio_analysis(allocations_to_display, metrics_to_display)
            st.markdown("---")
        
        # Goal Progress Tracker
        if metrics_to_display:
            render_goal_progress_tracker(metrics_to_display)
            st.markdown("---")
        
        # Market Context Integration
        render_market_context_integration(metrics_to_display)
        st.markdown("---")
        
        # Tax Optimization Planner
        if metrics_to_display:
            render_tax_optimization_planner(metrics_to_display)
            st.markdown("---")
        
        # Traditional displays (for backward compatibility)
        with st.expander("📊 Traditional Analysis View", expanded=False):
            # Display traditional metrics
            if st.session_state.get('metrics'):
                display_metrics_table(st.session_state['metrics'])
            
            # Download Excel Report Button
            if all(key in st.session_state for key in ['metrics', 'allocations', 'table_data', 'bullets']):
                download_excel_report(
                    st.session_state['metrics'],
                    st.session_state['allocations'],
                    st.session_state['table_data'],
                    st.session_state['bullets']
                )
            
            # Traditional Portfolio Visualization
            if st.session_state.get('allocations'):
                st.plotly_chart(create_allocation_chart(st.session_state['allocations']), use_container_width=True)
                st.plotly_chart(create_risk_return_chart(st.session_state['allocations']), use_container_width=True)
            
            # Traditional allocation table
            if st.session_state.get('table_data'):
                display_allocation_table(st.session_state['table_data'])
            
            # AI Recommendations
            if st.session_state.get('bullets'):
                with st.expander("🎯 AI Investment Recommendations", expanded=False):
                    display_recommendation_bullets(st.session_state['bullets'])
        
        # Comprehensive Report Generator
        if metrics_to_display and allocations_to_display and user_profile_data:
            st.markdown("---")
            render_comprehensive_report_generator(
                metrics_to_display, 
                allocations_to_display, 
                {"narrative": st.session_state.get('ai_narrative', ''), "recommendations": st.session_state.get('ai_recommendations', '')},
                user_profile_data
            )
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_market_data_page():
    """Render market data page"""
    st.title("🌍 Market Data")
    
    # Update market data
    if st.button("🔄 Refresh Market Data"):
        with st.spinner("Updating market data..."):
            update_market_data_background()
            st.success("Market data updated!")
            st.rerun()
    
    db = SessionLocal()
    try:
        # Get market summary
        market_summary = MarketService.get_market_summary(db)
        
        if market_summary:
            # Market overview
            st.subheader("📊 Market Overview")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tracked Symbols", market_summary.get('total_symbols', 0))
            
            with col2:
                asset_classes = market_summary.get('by_asset_class', {})
                if asset_classes:
                    avg_performance = sum(data['avg_change'] for data in asset_classes.values()) / len(asset_classes)
                    st.metric("Avg Performance", f"{avg_performance:.2f}%")
            
            with col3:
                if asset_classes:
                    best_class = max(asset_classes.items(), key=lambda x: x[1]['avg_change'])
                    st.metric("Best Asset Class", f"{best_class[0]} ({best_class[1]['avg_change']:+.2f}%)")
            
            # Performance by asset class
            st.subheader("📈 Performance by Asset Class")
            
            if asset_classes:
                asset_data = []
                for asset_class, data in asset_classes.items():
                    asset_data.append({
                        'Asset Class': asset_class.title(),
                        'Average Change %': data['avg_change'],
                        'Number of Symbols': data['count']
                    })
                
                import pandas as pd
                df = pd.DataFrame(asset_data)
                
                # Create bar chart
                import plotly.express as px
                fig = px.bar(df, x='Asset Class', y='Average Change %', 
                           title='Average Performance by Asset Class',
                           color='Average Change %',
                           color_continuous_scale='RdYlGn')
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Top performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Top Gainers")
                gainers = market_summary.get('top_gainers', [])
                if gainers:
                    for gainer in gainers:
                        st.write(f"**{gainer['symbol']}**: +{gainer['change_percent']:.2f}% (₹{gainer['current_price']:.2f})")
                else:
                    st.write("No gainers data available")
            
            with col2:
                st.subheader("📉 Top Losers")
                losers = market_summary.get('top_losers', [])
                if losers:
                    for loser in losers:
                        st.write(f"**{loser['symbol']}**: {loser['change_percent']:.2f}% (₹{loser['current_price']:.2f})")
                else:
                    st.write("No losers data available")
        
        else:
            st.info("No market data available. Click 'Refresh Market Data' to update.")
    
    finally:
        db.close()

def main():
    st.set_page_config(
        page_title="AI Financial Advisor", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    add_custom_css()
    
    # Check authentication
    check_authentication()
    
    # Update market data in background (non-blocking)
    if st.session_state.get('last_market_update') is None:
        update_market_data_background()
        st.session_state['last_market_update'] = True
    
    # Render navigation
    render_navigation()
    
    # Render current page
    current_page = st.session_state.get('current_page', 'Financial Analysis')
    
    if current_page == 'Dashboard':
        render_dashboard()
    elif current_page == 'Financial Analysis':
        render_financial_analysis_page()
    elif current_page == 'Portfolio Comparison':
        render_portfolio_comparison()
    elif current_page == 'Market Data':
        render_market_data_page()

if __name__ == "__main__":
    main()