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
    """Render portfolio comparison tool"""
    st.subheader("📊 Portfolio Comparison")
    
    db = SessionLocal()
    
    try:
        portfolios = PortfolioService.get_user_portfolios(db, limit=20)
        
        if len(portfolios) < 2:
            st.info("You need at least 2 portfolios to compare.")
            return
        
        # Select portfolios to compare
        portfolio_options = {
            f"{p.created_at.strftime('%Y-%m-%d %H:%M')} - {p.risk_level}": p.id 
            for p in portfolios
        }
        
        selected_portfolios = st.multiselect(
            "Select portfolios to compare (max 4):",
            options=list(portfolio_options.keys()),
            max_selections=4
        )
        
        if len(selected_portfolios) >= 2:
            selected_ids = [portfolio_options[p] for p in selected_portfolios]
            comparison_data = PortfolioService.get_portfolio_comparison(db, selected_ids)
            
            if comparison_data:
                # Create comparison visualization
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Asset Allocation Comparison', 'Risk Level Comparison', 
                                   'Investment Capacity', 'Savings Ratio'),
                    specs=[[{"type": "bar"}, {"type": "bar"}],
                           [{"type": "bar"}, {"type": "bar"}]]
                )
                
                # Asset allocation comparison
                for data in comparison_data:
                    date_str = data['created_at'].strftime('%Y-%m-%d')
                    allocations = data['allocations']
                    
                    fig.add_trace(
                        go.Bar(x=list(allocations.keys()), y=list(allocations.values()),
                               name=date_str, showlegend=True),
                        row=1, col=1
                    )
                
                fig.update_layout(
                    height=600,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary table
                st.markdown("**Comparison Summary:**")
                summary_data = []
                for data in comparison_data:
                    summary_data.append({
                        'Date': data['created_at'].strftime('%Y-%m-%d %H:%M'),
                        'Risk Level': data['risk_level'],
                        'Investment Capacity': f"₹{data['metrics'].get('investment_capacity', 0):,.0f}",
                        'Savings Ratio': f"{data['metrics'].get('monthly_savings_ratio', 0):.1f}%"
                    })
                
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    
    finally:
        db.close()