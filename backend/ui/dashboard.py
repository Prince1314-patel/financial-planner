import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from backend.services.portfolio_service import PortfolioService
from backend.services.market_service import MarketService
from backend.services.auth_service import AuthService
from backend.database.database import SessionLocal
from datetime import datetime, timedelta
import json

def render_dashboard():
    """Render user dashboard with portfolio history and market overview"""
    st.title("📊 Dashboard")
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Get user's portfolios
        portfolios = PortfolioService.get_user_portfolios(db, limit=10)
        
        if not portfolios:
            st.info("No portfolio history found. Create your first portfolio analysis!")
            return
        
        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Portfolios", len(portfolios))
        
        with col2:
            latest_portfolio = portfolios[0] if portfolios else None
            risk_level = latest_portfolio.risk_level if latest_portfolio else "N/A"
            st.metric("Latest Risk Level", risk_level)
        
        with col3:
            # Calculate average investment capacity from recent portfolios
            recent_portfolios = portfolios[:3]
            avg_capacity = 0
            if recent_portfolios:
                capacities = [p.metrics.get('investment_capacity', 0) for p in recent_portfolios]
                avg_capacity = sum(capacities) / len(capacities)
            st.metric("Avg Investment Capacity", f"₹{avg_capacity:,.0f}")
        
        with col4:
            # Days since last analysis
            if latest_portfolio:
                days_since = (datetime.now() - latest_portfolio.created_at).days
                st.metric("Days Since Last Analysis", days_since)
            else:
                st.metric("Days Since Last Analysis", "N/A")
        
        st.markdown("---")
        
        # Portfolio History Chart
        st.subheader("📈 Portfolio Evolution")
        
        if len(portfolios) > 1:
            # Create portfolio evolution chart
            portfolio_data = []
            for portfolio in reversed(portfolios):  # Reverse to show chronological order
                allocations = portfolio.allocations
                for asset, percentage in allocations.items():
                    portfolio_data.append({
                        'Date': portfolio.created_at.strftime('%Y-%m-%d'),
                        'Asset Class': asset,
                        'Allocation %': percentage,
                        'Portfolio ID': portfolio.id
                    })
            
            df = pd.DataFrame(portfolio_data)
            
            if not df.empty:
                fig = px.line(df, x='Date', y='Allocation %', color='Asset Class',
                             title="Portfolio Allocation Over Time",
                             markers=True)
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Create more portfolio analyses to see evolution over time!")
        
        # Latest Portfolio Breakdown
        st.subheader("💼 Latest Portfolio")
        
        if latest_portfolio:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Portfolio allocation pie chart
                allocations = latest_portfolio.allocations
                fig = px.pie(
                    values=list(allocations.values()),
                    names=list(allocations.keys()),
                    title="Current Asset Allocation"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Key metrics
                metrics = latest_portfolio.metrics
                st.markdown("**Key Metrics:**")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Investment Capacity", f"₹{metrics.get('investment_capacity', 0):,.0f}")
                    st.metric("Risk Score", f"{metrics.get('risk_score', 0):.1f}")
                
                with col_b:
                    st.metric("Savings Ratio", f"{metrics.get('monthly_savings_ratio', 0):.1f}%")
                    st.metric("Age", f"{metrics.get('age', 0)}")
                
                st.markdown("---")
                st.markdown(f"**Created:** {latest_portfolio.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Market Overview
        st.subheader("🌍 Market Overview")
        render_market_overview(db)
        
        # Portfolio History Table
        st.subheader("📋 Portfolio History")
        
        # Create portfolio history dataframe
        history_data = []
        for portfolio in portfolios:
            history_data.append({
                'Date': portfolio.created_at.strftime('%Y-%m-%d %H:%M'),
                'Risk Level': portfolio.risk_level,
                'Investment Capacity': f"₹{portfolio.metrics.get('investment_capacity', 0):,.0f}",
                'Savings Ratio': f"{portfolio.metrics.get('monthly_savings_ratio', 0):.1f}%",
                'Actions': portfolio.id
            })
        
        if history_data:
            df_history = pd.DataFrame(history_data)
            
            # Display with action buttons
            for idx, row in df_history.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.write(row['Date'])
                with col2:
                    st.write(row['Risk Level'])
                with col3:
                    st.write(row['Investment Capacity'])
                with col4:
                    st.write(row['Savings Ratio'])
                with col5:
                    if st.button(f"View Details", key=f"view_{row['Actions']}"):
                        st.session_state[f'show_portfolio_{row["Actions"]}'] = True
                        st.rerun()
                
                # Show portfolio details if requested
                if st.session_state.get(f'show_portfolio_{row["Actions"]}', False):
                    portfolio = next(p for p in portfolios if p.id == row['Actions'])
                    with st.expander(f"Portfolio Details - {row['Date']}", expanded=True):
                        
                        col_detail1, col_detail2 = st.columns(2)
                        
                        with col_detail1:
                            st.markdown("**Asset Allocation:**")
                            for asset, percentage in portfolio.allocations.items():
                                st.write(f"• {asset}: {percentage}%")
                        
                        with col_detail2:
                            st.markdown("**AI Narrative:**")
                            st.write(portfolio.ai_narrative[:200] + "..." if len(portfolio.ai_narrative) > 200 else portfolio.ai_narrative)
                        
                        if st.button(f"Hide Details", key=f"hide_{row['Actions']}"):
                            st.session_state[f'show_portfolio_{row["Actions"]}'] = False
                            st.rerun()
    
    finally:
        db.close()

def render_market_overview(db):
    """Render market overview section"""
    try:
        # Get market summary
        market_summary = MarketService.get_market_summary(db)
        
        if not market_summary:
            st.info("No market data available. Market data will be updated automatically.")
            return
        
        # Market metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tracked Symbols", market_summary.get('total_symbols', 0))
        
        with col2:
            # Average performance across asset classes
            asset_classes = market_summary.get('by_asset_class', {})
            if asset_classes:
                avg_performance = sum(data['avg_change'] for data in asset_classes.values()) / len(asset_classes)
                st.metric("Avg Market Performance", f"{avg_performance:.2f}%")
            else:
                st.metric("Avg Market Performance", "N/A")
        
        with col3:
            # Best performing asset class
            if asset_classes:
                best_class = max(asset_classes.items(), key=lambda x: x[1]['avg_change'])
                st.metric("Best Asset Class", f"{best_class[0]} ({best_class[1]['avg_change']:+.2f}%)")
            else:
                st.metric("Best Asset Class", "N/A")
        
        # Top gainers and losers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Top Gainers:**")
            gainers = market_summary.get('top_gainers', [])
            if gainers:
                for gainer in gainers[:3]:
                    st.write(f"• {gainer['symbol']}: +{gainer['change_percent']:.2f}%")
            else:
                st.write("No gainers data available")
        
        with col2:
            st.markdown("**📉 Top Losers:**")
            losers = market_summary.get('top_losers', [])
            if losers:
                for loser in losers[:3]:
                    st.write(f"• {loser['symbol']}: {loser['change_percent']:.2f}%")
            else:
                st.write("No losers data available")
        
        st.markdown(f"*Last updated: {market_summary.get('last_updated', 'N/A')}*")
        
    except Exception as e:
        st.error(f"Error loading market data: {str(e)}")

def render_portfolio_comparison():
    """Enhanced portfolio comparison tool with detailed analysis"""
    st.title("📊 Portfolio Comparison")
    
    # Instructions for users
    with st.expander("ℹ️ How to Use Portfolio Comparison", expanded=False):
        st.markdown("""
        **Portfolio Comparison helps you:**
        - **Track Your Evolution:** See how your investment strategy has changed over time
        - **Compare Scenarios:** Analyze different risk profiles or financial situations
        - **Make Better Decisions:** Understand the impact of different allocation strategies
        
        **How to Use:**
        1. Select 2-4 portfolios from your history
        2. View side-by-side comparisons of allocations and metrics
        3. Analyze the differences in investment capacity and risk levels
        4. Use insights to refine your current strategy
        
        **Best Practices:**
        - Compare portfolios from different time periods to see evolution
        - Compare portfolios with different risk tolerances to understand trade-offs
        - Look for patterns in successful allocations
        """)
    
    db = SessionLocal()
    
    try:
        portfolios = PortfolioService.get_user_portfolios(db, limit=20)
        
        if len(portfolios) < 2:
            st.warning("⚠️ You need at least 2 portfolios to use comparison feature.")
            st.info("💡 Create more portfolio analyses with different parameters to see meaningful comparisons!")
            return
        
        st.success(f"✅ Found {len(portfolios)} portfolios available for comparison")
        
        # Portfolio selection with better display
        st.subheader("📋 Select Portfolios to Compare")
        
        portfolio_options = {}
        for p in portfolios:
            date_str = p.created_at.strftime('%Y-%m-%d %H:%M')
            investment_capacity = p.metrics.get('investment_capacity', 0)
            display_name = f"{date_str} | {p.risk_level} Risk | ₹{investment_capacity:,.0f} Capacity"
            portfolio_options[display_name] = p.id
        
        selected_portfolios = st.multiselect(
            "Choose portfolios to compare (2-4 recommended):",
            options=list(portfolio_options.keys()),
            max_selections=4,
            help="Select portfolios from different dates or with different risk profiles for meaningful comparison"
        )
        
        if len(selected_portfolios) >= 2:
            selected_ids = [portfolio_options[p] for p in selected_portfolios]
            comparison_data = PortfolioService.get_portfolio_comparison(db, selected_ids)
            
            if comparison_data:
                st.markdown("---")
                
                # Quick metrics comparison
                st.subheader("🎯 Quick Metrics Comparison")
                
                metrics_cols = st.columns(len(comparison_data))
                for idx, data in enumerate(comparison_data):
                    with metrics_cols[idx]:
                        date_str = data['created_at'].strftime('%m/%d/%Y')
                        st.markdown(f"**Portfolio {idx + 1}**")
                        st.markdown(f"📅 {date_str}")
                        st.metric("Investment Capacity", f"₹{data['metrics'].get('investment_capacity', 0):,.0f}")
                        st.metric("Risk Level", data['risk_level'])
                        st.metric("Savings Rate", f"{data['metrics'].get('monthly_savings_ratio', 0):.1f}%")
                
                # Detailed visualizations
                st.subheader("📈 Detailed Analysis")
                
                # Asset allocation comparison
                st.markdown("**Asset Allocation Comparison**")
                
                # Create side-by-side pie charts
                pie_cols = st.columns(len(comparison_data))
                for idx, data in enumerate(comparison_data):
                    with pie_cols[idx]:
                        allocations = data['allocations']
                        fig = px.pie(
                            values=list(allocations.values()),
                            names=list(allocations.keys()),
                            title=f"Portfolio {idx + 1}<br>{data['created_at'].strftime('%m/%d/%Y')}"
                        )
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white', size=10),
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Bar chart comparison
                st.markdown("**Side-by-Side Allocation Comparison**")
                
                # Prepare data for grouped bar chart
                all_assets = set()
                for data in comparison_data:
                    all_assets.update(data['allocations'].keys())
                
                comparison_df = []
                for idx, data in enumerate(comparison_data):
                    portfolio_name = f"Portfolio {idx + 1} ({data['created_at'].strftime('%m/%d')})"
                    for asset in all_assets:
                        allocation = data['allocations'].get(asset, 0)
                        comparison_df.append({
                            'Portfolio': portfolio_name,
                            'Asset Class': asset,
                            'Allocation %': allocation
                        })
                
                df = pd.DataFrame(comparison_df)
                
                if not df.empty:
                    fig = px.bar(
                        df, 
                        x='Asset Class', 
                        y='Allocation %', 
                        color='Portfolio',
                        barmode='group',
                        title="Asset Allocation Comparison",
                        text='Allocation %'
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=500
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Investment capacity trend
                st.markdown("**Investment Capacity Trend**")
                capacity_data = [
                    {
                        'Date': data['created_at'].strftime('%Y-%m-%d'),
                        'Investment Capacity': data['metrics'].get('investment_capacity', 0),
                        'Risk Level': data['risk_level']
                    }
                    for data in sorted(comparison_data, key=lambda x: x['created_at'])
                ]
                
                if len(capacity_data) > 1:
                    df_capacity = pd.DataFrame(capacity_data)
                    fig = px.line(
                        df_capacity, 
                        x='Date', 
                        y='Investment Capacity',
                        color='Risk Level',
                        markers=True,
                        title="Investment Capacity Over Time"
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed comparison table
                st.subheader("📋 Detailed Comparison Table")
                summary_data = []
                for idx, data in enumerate(comparison_data):
                    summary_data.append({
                        'Portfolio': f"Portfolio {idx + 1}",
                        'Date': data['created_at'].strftime('%Y-%m-%d %H:%M'),
                        'Risk Level': data['risk_level'],
                        'Investment Capacity': f"₹{data['metrics'].get('investment_capacity', 0):,.0f}",
                        'Savings Ratio': f"{data['metrics'].get('monthly_savings_ratio', 0):.1f}%",
                        'Health Score': f"{data['metrics'].get('health_score', 0):.0f}/100" if data['metrics'].get('health_score') else "N/A"
                    })
                
                df_summary = pd.DataFrame(summary_data)
                st.dataframe(df_summary, use_container_width=True)
                
                # Insights and recommendations
                st.subheader("💡 Comparison Insights")
                
                # Calculate insights
                capacities = [data['metrics'].get('investment_capacity', 0) for data in comparison_data]
                risk_levels = [data['risk_level'] for data in comparison_data]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Key Observations:**")
                    if len(set(capacities)) > 1:
                        max_capacity = max(capacities)
                        min_capacity = min(capacities)
                        change_percent = ((max_capacity - min_capacity) / min_capacity * 100) if min_capacity > 0 else 0
                        st.write(f"📈 Investment capacity varies by ₹{max_capacity - min_capacity:,.0f} ({change_percent:.1f}%)")
                    
                    if len(set(risk_levels)) > 1:
                        st.write("⚖️ Different risk levels show varying allocation strategies")
                    else:
                        st.write("🎯 Consistent risk level across all portfolios")
                
                with col2:
                    st.markdown("**Recommendations:**")
                    st.write("🔄 Compare portfolios over time to track your financial growth")
                    st.write("⚖️ Analyze risk vs. capacity trade-offs")
                    st.write("📊 Use allocation differences to fine-tune current strategy")
        
        elif len(selected_portfolios) == 1:
            st.info("Please select at least 2 portfolios to compare.")
        
        else:
            st.info("Select portfolios above to start comparison analysis.")
    
    finally:
        db.close()