import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional
from backend.services.enhanced_financial_engine import EnhancedFinancialEngine
from backend.services.advanced_report_generator import AdvancedReportGenerator
from backend.services.portfolio_service import PortfolioService
from backend.services.market_service import MarketService
from backend.database.database import SessionLocal
from backend.services.auth_service import AuthService

def render_financial_health_dashboard(metrics: Dict[str, Any]):
    """Render comprehensive financial health dashboard"""
    
    st.subheader("📊 Financial Health Dashboard")
    
    health_score = metrics.get('financial_health_score', 0)
    
    # Health score gauge
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = health_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Financial Health Score"},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkgreen" if health_score >= 70 else "orange" if health_score >= 50 else "red"},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 70], 'color': "gray"},
                {'range': [70, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Key metrics cards
        st.metric("💰 Investment Capacity", f"₹{metrics.get('investment_capacity', 0):,.0f}/month")
        st.metric("💳 Savings Rate", f"{metrics.get('savings_rate', 0):.1f}%")
        st.metric("🛡️ Emergency Fund", f"{metrics.get('emergency_fund_months', 0):.1f} months")
        
        # Lifecycle stage
        lifecycle_stage = metrics.get('lifecycle_stage', {})
        if lifecycle_stage:
            st.info(f"**Life Stage:** {lifecycle_stage.get('stage', 'Unknown').replace('_', ' ').title()}")

def render_personalized_insights(metrics: Dict[str, Any], user_profile: Dict[str, Any]):
    """Render personalized insights based on user data and trends"""
    
    st.subheader("🎯 Personalized Insights")
    
    # Income and expense trends
    income_trend = metrics.get('income_trend', {})
    expense_trend = metrics.get('expense_trend', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Income Trend**")
        if income_trend.get('trend') != 'insufficient_data':
            change_percent = income_trend.get('change_percent', 0)
            trend_color = "green" if change_percent > 0 else "red"
            st.markdown(f"<span style='color: {trend_color}'>{change_percent:+.1f}%</span> vs last analysis", unsafe_allow_html=True)
            st.info(income_trend.get('recommendation', 'Continue tracking'))
        else:
            st.info("Complete more analyses to see income trends")
    
    with col2:
        st.markdown("**💸 Expense Trend**")
        if expense_trend.get('trend') != 'insufficient_data':
            change_percent = expense_trend.get('change_percent', 0)
            trend_color = "red" if change_percent > 10 else "orange" if change_percent > 0 else "green"
            st.markdown(f"<span style='color: {trend_color}'>{change_percent:+.1f}%</span> vs last analysis", unsafe_allow_html=True)
            st.info(expense_trend.get('alert', 'Expenses stable'))
        else:
            st.info("Continue tracking for expense trends")
    
    # Goal analysis
    goal_analysis = metrics.get('goal_analysis', {})
    if goal_analysis and goal_analysis.get('detected_goals'):
        st.markdown("**🎯 Detected Financial Goals**")
        
        detected_goals = goal_analysis.get('detected_goals', [])
        goal_emojis = {
            'retirement': '🏖️',
            'home': '🏠',
            'education': '🎓',
            'travel': '✈️',
            'business': '💼',
            'emergency': '🚨'
        }
        
        for goal in detected_goals:
            emoji = goal_emojis.get(goal, '🎯')
            st.write(f"{emoji} {goal.title()}")
        
        # Show goal recommendations
        recommendations = goal_analysis.get('recommendations', [])
        if recommendations:
            with st.expander("Goal-Specific Recommendations"):
                for rec in recommendations:
                    st.markdown(f"**{rec['goal']}**")
                    st.write(f"• Timeline: {rec['timeline']}")
                    st.write(f"• Monthly Investment: ₹{rec['monthly_investment']:,.0f}")
                    st.write(f"• Strategy: {rec['strategy']}")
                    st.markdown("---")

def render_what_if_scenarios(metrics: Dict[str, Any]):
    """Render interactive what-if scenario analysis"""
    
    st.subheader("🔮 What-If Scenarios")
    
    base_investment = metrics.get('investment_capacity', 0)
    base_age = metrics.get('user_age', 30)
    
    # Interactive sliders
    col1, col2, col3 = st.columns(3)
    
    with col1:
        investment_multiplier = st.slider(
            "Investment Amount Multiplier", 
            min_value=0.5, 
            max_value=2.0, 
            value=1.0, 
            step=0.1,
            help="Adjust monthly investment amount"
        )
    
    with col2:
        years_to_invest = st.slider(
            "Investment Time Horizon", 
            min_value=1, 
            max_value=30, 
            value=10, 
            step=1,
            help="Years to stay invested"
        )
    
    with col3:
        expected_return = st.slider(
            "Expected Annual Return (%)", 
            min_value=6.0, 
            max_value=18.0, 
            value=12.0, 
            step=0.5,
            help="Expected annual return rate"
        )
    
    # Calculate scenarios
    adjusted_investment = base_investment * investment_multiplier
    monthly_return = expected_return / 100 / 12
    months = years_to_invest * 12
    
    if monthly_return > 0:
        future_value = adjusted_investment * (((1 + monthly_return) ** months - 1) / monthly_return)
    else:
        future_value = adjusted_investment * months
    
    total_invested = adjusted_investment * months
    gains = future_value - total_invested
    
    # Display results
    st.markdown("**Scenario Results:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Monthly Investment", f"₹{adjusted_investment:,.0f}")
        st.metric("Total Invested", f"₹{total_invested:,.0f}")
    
    with col2:
        st.metric("Future Value", f"₹{future_value:,.0f}")
        st.metric("Total Gains", f"₹{gains:,.0f}")
    
    with col3:
        st.metric("Wealth Multiplier", f"{future_value/total_invested:.1f}x")
        annualized_return = ((future_value / total_invested) ** (1/years_to_invest) - 1) * 100
        st.metric("Effective Annual Return", f"{annualized_return:.1f}%")
    
    # Visualization
    years_list = list(range(1, years_to_invest + 1))
    invested_values = [adjusted_investment * 12 * year for year in years_list]
    
    future_values = []
    for year in years_list:
        months_temp = year * 12
        if monthly_return > 0:
            fv_temp = adjusted_investment * (((1 + monthly_return) ** months_temp - 1) / monthly_return)
        else:
            fv_temp = adjusted_investment * months_temp
        future_values.append(fv_temp)
    
    # Create growth chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years_list,
        y=invested_values,
        mode='lines+markers',
        name='Total Invested',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=years_list,
        y=future_values,
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='green', width=3)
    ))
    
    fig.update_layout(
        title='Investment Growth Projection',
        xaxis_title='Years',
        yaxis_title='Amount (₹)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_advanced_portfolio_analysis(allocations: Dict[str, float], metrics: Dict[str, Any]):
    """Render advanced portfolio analysis with modern visualizations"""
    
    st.subheader("📊 Advanced Portfolio Analysis")
    
    if not allocations:
        st.warning("No allocation data available")
        return
    
    # Portfolio composition with enhanced visuals
    col1, col2 = st.columns(2)
    
    with col1:
        # Sunburst chart for hierarchical view
        # Categorize assets
        asset_categories = {
            'Equity': ['Large Cap Stocks', 'Mid Cap Stocks', 'Small Cap Stocks', 'International Stocks'],
            'Debt': ['Government Bonds', 'Corporate Bonds'],
            'Alternative': ['Gold/Commodities', 'Cash/FD', 'Real Estate']
        }
        
        # Prepare data for sunburst
        labels = ['Portfolio']
        parents = ['']
        values = [100]
        
        for category, assets in asset_categories.items():
            category_value = sum(allocations.get(asset, 0) for asset in assets)
            if category_value > 0:
                labels.append(category)
                parents.append('Portfolio')
                values.append(category_value)
                
                for asset in assets:
                    asset_value = allocations.get(asset, 0)
                    if asset_value > 0:
                        labels.append(asset)
                        parents.append(category)
                        values.append(asset_value)
        
        fig_sunburst = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>',
            maxdepth=2
        ))
        
        fig_sunburst.update_layout(
            title="Portfolio Composition",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig_sunburst, use_container_width=True)
    
    with col2:
        # Risk-return scatter plot
        asset_risk_return = {
            'Large Cap Stocks': {'return': 12, 'risk': 15},
            'Mid Cap Stocks': {'return': 14, 'risk': 20},
            'Small Cap Stocks': {'return': 16, 'risk': 25},
            'International Stocks': {'return': 10, 'risk': 18},
            'Government Bonds': {'return': 7, 'risk': 5},
            'Corporate Bonds': {'return': 8.5, 'risk': 7},
            'Gold/Commodities': {'return': 8, 'risk': 20},
            'Cash/FD': {'return': 6, 'risk': 1},
            'Real Estate': {'return': 11, 'risk': 12}
        }
        
        # Create scatter plot
        assets = []
        returns = []
        risks = []
        sizes = []
        
        for asset, allocation in allocations.items():
            if allocation > 0 and asset in asset_risk_return:
                assets.append(asset)
                returns.append(asset_risk_return[asset]['return'])
                risks.append(asset_risk_return[asset]['risk'])
                sizes.append(allocation * 5)  # Scale for visualization
        
        fig_scatter = go.Figure(go.Scatter(
            x=risks,
            y=returns,
            mode='markers+text',
            text=assets,
            textposition="top center",
            marker=dict(
                size=sizes,
                color=returns,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Expected Return (%)")
            ),
            hovertemplate='<b>%{text}</b><br>Risk: %{x}%<br>Return: %{y}%<extra></extra>'
        ))
        
        fig_scatter.update_layout(
            title="Risk-Return Profile",
            xaxis_title="Risk (Volatility %)",
            yaxis_title="Expected Return (%)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Portfolio metrics
    st.markdown("**Portfolio Metrics**")
    
    # Calculate portfolio metrics
    portfolio_return = sum(
        allocations.get(asset, 0) * asset_risk_return.get(asset, {}).get('return', 8) / 100
        for asset in allocations.keys()
    )
    
    portfolio_risk = sum(
        allocations.get(asset, 0) * asset_risk_return.get(asset, {}).get('risk', 15) / 100
        for asset in allocations.keys()
    )
    
    sharpe_ratio = (portfolio_return - 0.06) / portfolio_risk if portfolio_risk > 0 else 0  # Assuming 6% risk-free rate
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Expected Return", f"{portfolio_return:.1f}%")
    
    with col2:
        st.metric("Portfolio Risk", f"{portfolio_risk:.1f}%")
    
    with col3:
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
    
    with col4:
        diversification_score = AdvancedReportGenerator._calculate_diversification_score(allocations)
        st.metric("Diversification Score", f"{diversification_score}/100")

def render_goal_progress_tracker(metrics: Dict[str, Any]):
    """Render goal progress tracking with timelines"""
    
    st.subheader("🎯 Goal Progress Tracker")
    
    goal_analysis = metrics.get('goal_analysis', {})
    
    if not goal_analysis or not goal_analysis.get('detected_goals'):
        st.info("No specific goals detected. Add your financial goals in the analysis form to see progress tracking.")
        return
    
    detected_goals = goal_analysis.get('detected_goals', [])
    recommendations = goal_analysis.get('recommendations', [])
    
    # Create goal progress visualization
    for rec in recommendations:
        goal_name = rec['goal']
        timeline = rec['timeline']
        monthly_investment = rec['monthly_investment']
        
        st.markdown(f"**{goal_name}**")
        
        # Extract timeline years
        timeline_years = 5  # Default
        if 'year' in timeline.lower():
            try:
                timeline_years = int(timeline.split()[0])
            except:
                timeline_years = 5
        
        # Calculate progress (assuming current investment is being made)
        current_investment = metrics.get('investment_capacity', 0)
        progress_percentage = min(100, (current_investment / monthly_investment) * 100) if monthly_investment > 0 else 0
        
        # Progress bar
        progress_bar = st.progress(progress_percentage / 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Timeline", timeline)
        
        with col2:
            st.metric("Monthly Need", f"₹{monthly_investment:,.0f}")
        
        with col3:
            st.metric("Current Progress", f"{progress_percentage:.0f}%")
        
        # Recommendations
        st.info(f"Strategy: {rec['strategy']}")
        st.markdown("---")

def render_market_context_integration(metrics: Dict[str, Any]):
    """Render market context integration with live data"""
    
    st.subheader("🌍 Market Context & Timing")
    
    # Get market data
    db = SessionLocal()
    try:
        market_summary = MarketService.get_market_summary(db)
        
        if market_summary:
            # Market overview
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Market Sentiment", "Mixed")  # Would be calculated from actual data
            
            with col2:
                asset_classes = market_summary.get('by_asset_class', {})
                if asset_classes:
                    avg_change = sum(data['avg_change'] for data in asset_classes.values()) / len(asset_classes)
                    st.metric("Avg Market Change", f"{avg_change:+.2f}%")
            
            with col3:
                st.metric("Volatility Index", "Medium")  # Would be calculated
            
            # Investment timing suggestions
            st.markdown("**Market-Based Suggestions:**")
            
            if asset_classes:
                suggestions = []
                
                for asset_class, data in asset_classes.items():
                    avg_change = data['avg_change']
                    
                    if avg_change < -5:
                        suggestions.append(f"✅ {asset_class.title()} showing weakness - good SIP opportunity")
                    elif avg_change > 10:
                        suggestions.append(f"⚠️ {asset_class.title()} at highs - consider gradual entry")
                    else:
                        suggestions.append(f"📊 {asset_class.title()} stable - continue regular investments")
                
                for suggestion in suggestions:
                    st.write(suggestion)
            
            # SIP timing recommendation
            st.info("💡 **SIP Timing:** Market timing is difficult. Continue systematic investments regardless of market conditions for best long-term results.")
        
        else:
            st.info("Market data not available. Enable market data updates for contextual insights.")
    
    finally:
        db.close()

def render_tax_optimization_planner(metrics: Dict[str, Any]):
    """Render tax optimization planning interface"""
    
    st.subheader("💰 Tax Optimization Planner")
    
    tax_suggestions = metrics.get('tax_suggestions', [])
    investment_capacity = metrics.get('investment_capacity', 0)
    annual_investment = investment_capacity * 12
    
    if not tax_suggestions:
        st.info("Complete your financial profile to get personalized tax optimization suggestions.")
        return
    
    # Tax savings potential
    total_savings = sum(
        46800 if sug.get('type') == 'ELSS Investment' else
        15600 if sug.get('type') == 'NPS Investment' else 0
        for sug in tax_suggestions
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Potential Tax Savings", f"₹{total_savings:,.0f}")
    
    with col2:
        st.metric("Annual Investment", f"₹{annual_investment:,.0f}")
    
    # Tax-efficient allocation
    st.markdown("**Tax-Efficient Investment Allocation:**")
    
    # Create tax-efficient portfolio visualization
    tax_efficient_allocation = {}
    
    if annual_investment >= 150000:
        tax_efficient_allocation['ELSS (80C)'] = min(150000, annual_investment * 0.3)
    
    if annual_investment >= 50000:
        tax_efficient_allocation['NPS (80CCD1B)'] = 50000
    
    if annual_investment >= 150000:
        tax_efficient_allocation['PPF'] = min(150000, annual_investment * 0.2)
    
    remaining = annual_investment - sum(tax_efficient_allocation.values())
    if remaining > 0:
        tax_efficient_allocation['Regular Investments'] = remaining
    
    if tax_efficient_allocation:
        # Pie chart for tax allocation
        fig_tax = px.pie(
            values=list(tax_efficient_allocation.values()),
            names=list(tax_efficient_allocation.keys()),
            title="Tax-Efficient Annual Allocation"
        )
        
        fig_tax.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig_tax, use_container_width=True)
    
    # Detailed tax suggestions
    st.markdown("**Detailed Tax Strategies:**")
    
    for suggestion in tax_suggestions:
        with st.expander(f"💡 {suggestion['type']}"):
            st.write(f"**Description:** {suggestion['description']}")
            st.write(f"**Tax Benefit:** {suggestion['tax_benefit']}")
            st.write(f"**Recommended Allocation:** {suggestion['allocation']}")

def render_comprehensive_report_generator(metrics: Dict[str, Any], allocations: Dict[str, float], 
                                        ai_analysis: Dict[str, Any], user_profile: Dict[str, Any]):
    """Render comprehensive report generation interface"""
    
    st.subheader("📋 Comprehensive Report Generator")
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Executive Summary", "Detailed Analysis", "Goal-Focused", "Tax Optimization", "Complete Report"]
        )
    
    with col2:
        report_format = st.selectbox(
            "Format",
            ["Interactive (Streamlit)", "PDF Download", "Excel Workbook", "Email Summary"]
        )
    
    # Generate report
    if st.button("Generate Comprehensive Report", type="primary"):
        with st.spinner("Generating comprehensive report..."):
            # Generate report data
            report_data = AdvancedReportGenerator.generate_comprehensive_report(
                metrics, allocations, ai_analysis, user_profile
            )
            
            # Display based on selection
            if report_type == "Executive Summary":
                render_executive_summary_report(report_data)
            elif report_type == "Detailed Analysis":
                render_detailed_analysis_report(report_data)
            elif report_type == "Goal-Focused":
                render_goal_focused_report(report_data)
            elif report_type == "Tax Optimization":
                render_tax_optimization_report(report_data)
            else:  # Complete Report
                render_complete_report(report_data)

def render_executive_summary_report(report_data: Dict[str, Any]):
    """Render executive summary report"""
    
    st.markdown("## 📊 Executive Summary Report")
    
    executive_summary = report_data.get('executive_summary', {})
    
    # Financial status
    status = executive_summary.get('financial_status', 'Unknown')
    status_color = executive_summary.get('status_color', 'blue')
    
    st.markdown(f"### Financial Status: <span style='color: {status_color}'>{status}</span>", unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Health Score", f"{executive_summary.get('health_score', 0)}/100")
    
    with col2:
        st.metric("Monthly Investment", f"₹{executive_summary.get('monthly_investment_capacity', 0):,.0f}")
    
    with col3:
        st.metric("Savings Rate", f"{executive_summary.get('savings_rate', 0):.1f}%")
    
    # Key insights
    st.markdown("### 🎯 Key Insights")
    insights = executive_summary.get('key_insights', [])
    for insight in insights:
        st.write(f"• {insight}")
    
    # Top recommendations
    st.markdown("### 📋 Top Recommendations")
    recommendations = executive_summary.get('top_recommendations', [])
    for rec in recommendations:
        st.write(f"• {rec}")

def render_detailed_analysis_report(report_data: Dict[str, Any]):
    """Render detailed analysis report"""
    
    st.markdown("## 📈 Detailed Financial Analysis")
    
    # Financial health breakdown
    financial_health = report_data.get('financial_health', {})
    
    st.markdown("### 🏥 Financial Health Breakdown")
    
    components = financial_health.get('components', {})
    for component, data in components.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{component}**")
            st.write(data.get('details', ''))
        
        with col2:
            score = data.get('score', 0)
            max_score = data.get('max_score', 100)
            st.progress(score / max_score)
            st.write(f"{score}/{max_score}")
        
        with col3:
            status = data.get('status', 'Unknown')
            status_color = "green" if status == "Good" else "orange" if status == "Fair" else "red"
            st.markdown(f"<span style='color: {status_color}'>{status}</span>", unsafe_allow_html=True)
    
    # Portfolio analysis
    portfolio_analysis = report_data.get('portfolio_analysis', {})
    
    if portfolio_analysis and 'allocation_summary' in portfolio_analysis:
        st.markdown("### 📊 Portfolio Analysis")
        
        allocation_summary = portfolio_analysis['allocation_summary']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Equity %", f"{allocation_summary.get('equity_percent', 0):.1f}%")
        
        with col2:
            st.metric("Debt %", f"{allocation_summary.get('debt_percent', 0):.1f}%")
        
        with col3:
            st.metric("Alternative %", f"{allocation_summary.get('alternative_percent', 0):.1f}%")
        
        # Risk metrics
        risk_metrics = portfolio_analysis.get('risk_metrics', {})
        st.markdown("**Risk Metrics:**")
        st.write(f"• Expected Annual Return: {risk_metrics.get('expected_annual_return', 0):.1f}%")
        st.write(f"• Risk Level: {risk_metrics.get('risk_level', 'Unknown')}")
        st.write(f"• Diversification Score: {risk_metrics.get('diversification_score', 0)}/100")

def render_goal_focused_report(report_data: Dict[str, Any]):
    """Render goal-focused report"""
    
    st.markdown("## 🎯 Goal-Focused Analysis")
    
    goal_tracking = report_data.get('goal_tracking', {})
    
    if not goal_tracking or goal_tracking.get('message'):
        st.info("No specific goals detected in your analysis.")
        return
    
    detected_goals = goal_tracking.get('detected_goals', [])
    goal_recommendations = goal_tracking.get('goal_recommendations', [])
    
    st.markdown(f"### Detected Goals: {', '.join(detected_goals).title()}")
    
    # Goal recommendations
    for rec in goal_recommendations:
        with st.expander(f"🎯 {rec['goal']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Timeline:** {rec['timeline']}")
                st.write(f"**Monthly Investment:** ₹{rec['monthly_investment']:,.0f}")
            
            with col2:
                st.write(f"**Strategy:** {rec['strategy']}")
    
    # Tracking suggestions
    tracking_suggestions = goal_tracking.get('tracking_suggestions', [])
    
    if tracking_suggestions:
        st.markdown("### 📊 Tracking Suggestions")
        for suggestion in tracking_suggestions:
            st.write(f"• {suggestion}")

def render_tax_optimization_report(report_data: Dict[str, Any]):
    """Render tax optimization report"""
    
    st.markdown("## 💰 Tax Optimization Report")
    
    tax_analysis = report_data.get('tax_optimization', {})
    
    if not tax_analysis:
        st.info("Complete your financial profile to get tax optimization analysis.")
        return
    
    # Tax savings potential
    savings_potential = tax_analysis.get('tax_savings_potential', 0)
    st.metric("Annual Tax Savings Potential", f"₹{savings_potential:,.0f}")
    
    # Tax-efficient instruments
    instruments = tax_analysis.get('tax_efficient_instruments', [])
    
    if instruments:
        st.markdown("### 🏛️ Recommended Tax-Efficient Instruments")
        for instrument in instruments:
            st.write(f"• {instrument}")
    
    # Detailed suggestions
    detailed_suggestions = tax_analysis.get('detailed_suggestions', [])
    
    if detailed_suggestions:
        st.markdown("### 📋 Detailed Tax Strategies")
        
        for suggestion in detailed_suggestions:
            with st.expander(f"💡 {suggestion.get('type', 'Tax Strategy')}"):
                st.write(f"**Description:** {suggestion.get('description', '')}")
                st.write(f"**Tax Benefit:** {suggestion.get('tax_benefit', '')}")
                st.write(f"**Allocation:** {suggestion.get('allocation', '')}")

def render_complete_report(report_data: Dict[str, Any]):
    """Render complete comprehensive report"""
    
    st.markdown("# 📊 Complete Financial Analysis Report")
    st.markdown(f"*Generated on: {datetime.now().strftime('%B %d, %Y')}*")
    
    # Render all sections
    render_executive_summary_report(report_data)
    st.markdown("---")
    
    render_detailed_analysis_report(report_data)
    st.markdown("---")
    
    render_goal_focused_report(report_data)
    st.markdown("---")
    
    render_tax_optimization_report(report_data)
    st.markdown("---")
    
    # Action plan
    action_plan = report_data.get('action_plan', {})
    
    if action_plan:
        st.markdown("## 📋 Action Plan")
        
        # Immediate actions
        immediate_actions = action_plan.get('immediate_actions', [])
        if immediate_actions:
            st.markdown("### ⚡ Immediate Actions (Next 30 Days)")
            for action in immediate_actions:
                st.write(f"• **{action['action']}** - {action['timeline']} (Priority: {action['priority']})")
        
        # Short-term actions
        short_term_actions = action_plan.get('short_term_actions', [])
        if short_term_actions:
            st.markdown("### 📅 Short-term Actions (Next 3 Months)")
            for action in short_term_actions:
                st.write(f"• **{action['action']}** - {action['timeline']} (Priority: {action['priority']})")
                if 'details' in action:
                    st.write(f"  ℹ️ {action['details']}")
        
        # Review schedule
        review_schedule = action_plan.get('review_schedule', {})
        if review_schedule:
            st.markdown("### 📊 Review Schedule")
            for frequency, tasks in review_schedule.items():
                st.write(f"**{frequency}:**")
                for task in tasks:
                    st.write(f"• {task}")
    
    # Benchmarking
    benchmarking = report_data.get('benchmarking', {})
    
    if benchmarking:
        st.markdown("## 📊 Benchmarking")
        
        age_group = benchmarking.get('age_group', 'Unknown')
        st.write(f"**Comparison Group:** {age_group}")
        
        performance = benchmarking.get('your_performance', {})
        
        for metric, data in performance.items():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{metric.replace('_', ' ').title()}**")
            
            with col2:
                st.write(f"Your: {data.get('your_rate', data.get('your_months', 'N/A'))}")
            
            with col3:
                status = data.get('status', 'Unknown')
                status_color = "green" if status in ["Above", "Adequate"] else "red"
                st.markdown(f"<span style='color: {status_color}'>{status}</span>", unsafe_allow_html=True)