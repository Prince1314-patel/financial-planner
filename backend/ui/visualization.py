import streamlit as st
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import pdfkit
import base64
from typing import Dict, List, Any
from backend.utils.formatters import format_currency, format_percentage

def create_allocation_chart(allocations: Dict[str, float]) -> go.Figure:
    """Create a pie chart showing portfolio allocation.
    
    Args:
        allocations: Dictionary of asset classes and their percentages
        
    Returns:
        Plotly figure object
    """
    colors = ['#4B56D2', '#82C3EC', '#47B5FF', '#256D85', '#06283D', '#1363DF']
    
    fig = go.Figure(data=[go.Pie(
        labels=list(allocations.keys()),
        values=list(allocations.values()),
        hole=.4,
        textinfo='label+percent',
        marker=dict(colors=colors),
        textfont=dict(size=14, color='#ffffff'),
        hoverinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title={
            'text': 'Recommended Portfolio Allocation',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#ffffff'}
        },
        showlegend=True,
        legend=dict(
            font=dict(color='#ffffff', size=12),
            bgcolor='rgba(0,0,0,0)'
        ),
        width=800,
        height=600,  # Increased height for better visibility
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_risk_return_chart(allocations: Dict[str, float]) -> go.Figure:
    """Create a risk vs return scatter plot for different asset classes."""
    risk_return_data = {
        'Stocks': {'risk': 20, 'return': 12},
        'Bonds': {'risk': 5, 'return': 5},
        'Gold': {'risk': 15, 'return': 8},
        'Real Estate': {'risk': 12, 'return': 9},
        'Cash': {'risk': 1, 'return': 3},
        'Fixed Deposits': {'risk': 2, 'return': 4},
    }
    
    fig = go.Figure()
    colors = ['#4B56D2', '#82C3EC', '#47B5FF', '#256D85', '#06283D', '#1363DF']
    
    for i, (asset, data) in enumerate(risk_return_data.items()):
        # Calculate size - use allocation if exists, otherwise use minimum size
        size = max(allocations.get(asset, 0) * 1000, 200)  # Minimum size of 200 for visibility
        opacity = 1.0 if allocations.get(asset, 0) > 0 else 0.4  # Lower opacity for non-allocated assets
        
        fig.add_trace(go.Scatter(
            x=[data['risk']],
            y=[data['return']],
            mode='markers+text',
            name=asset,
            text=[asset],
            textposition="top center",
            textfont=dict(color='#ffffff'),
            marker=dict(
                size=[size],
                sizemode='area',
                sizeref=2.*max(max(allocations.values(), default=0.1)*1000, 200)/(40.**2),
                sizemin=10,
                color=colors[i],
                opacity=opacity,
                line=dict(color='#ffffff', width=1)
            )
        ))
    
    fig.update_layout(
        title={
            'text': 'Risk vs Return Profile',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#ffffff'}
        },
        xaxis=dict(
            title="Risk (%)",
            color='#ffffff',
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title="Expected Return (%)",
            color='#ffffff',
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.05,
            font=dict(color='#ffffff')
        ),
        width=800,
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def display_metrics_table(metrics: Dict[str, float]) -> None:
    """Display financial metrics in a formatted table with dynamic updates.
    
    Args:
        metrics: Dictionary of financial metrics
    """
    if not metrics:
        return
        
    # Initialize metrics in session state if not exists
    if 'current_metrics' not in st.session_state:
        st.session_state.current_metrics = metrics.copy()
    else:
        # Update metrics with smooth transitions
        for key in metrics:
            if key in st.session_state.current_metrics:
                current = st.session_state.current_metrics[key]
                target = metrics[key]
                st.session_state.current_metrics[key] = target
                
    display_metrics = st.session_state.current_metrics
    st.markdown("""
        <style>
        .metric-container {
            background: linear-gradient(45deg, rgba(75, 86, 210, 0.1), rgba(19, 99, 223, 0.1));
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .metric-title {
            color: #ffffff;
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }
        .stMetric {
            background: rgba(0,0,0,0.2) !important;
            border-radius: 10px !important;
            padding: 1rem !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
        }
        .stMetric > div {
            color: #ffffff !important;
        }
        </style>
        <div class="metric-container">
        <h3 class="metric-title">Your Financial Metrics</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            'Monthly Investment Capacity',
            format_currency(display_metrics.get('investment_capacity', 0)),
            delta=None,
            help="Amount you can invest monthly after expenses"
        )
        st.metric(
            'Debt-to-Income Ratio',
            format_percentage(display_metrics.get('debt_to_income', 0)),
            delta=None,
            help="Total monthly debt payments divided by monthly income"
        )
    
    with col2:
        st.metric(
            'Emergency Fund Status',
            format_currency(display_metrics.get('emergency_fund', 0)),
            delta=None,
            help="Recommended emergency fund based on your expenses"
        )
        st.metric(
            'Risk Score',
            f"{display_metrics.get('risk_score', 0)}/10",
            delta=None,
            help="Your risk tolerance score based on profile"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_allocation_table(table_data: List[Dict[str, str]]) -> None:
    """Display portfolio allocation in a table format.
    
    Args:
        table_data: List of dictionaries containing allocation details
    """
    st.markdown("""
        <style>
        .table-container {
            background: linear-gradient(45deg, rgba(75, 86, 210, 0.1), rgba(19, 99, 223, 0.1));
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .dataframe {
            width: 100% !important;
            color: #ffffff !important;
            background-color: transparent !important;
        }
        .dataframe th {
            background-color: rgba(0,0,0,0.2) !important;
            color: #ffffff !important;
            padding: 12px !important;
        }
        .dataframe td {
            background-color: rgba(0,0,0,0.1) !important;
            color: #ffffff !important;
            padding: 10px !important;
        }
        </style>
        <div class="table-container">
    """, unsafe_allow_html=True)
    st.table(table_data)
    st.markdown("</div>", unsafe_allow_html=True)

def display_recommendation_bullets(bullets: List[str]) -> None:
    """Display AI recommendations as bullet points.
    
    Args:
        bullets: List of recommendation strings
    """
    st.markdown("""
        <style>
        .recommendations-container {
            background: rgba(0,0,0,0.2);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .recommendation-bullet {
            color: #ffffff;
            margin-bottom: 1rem;
            padding: 1rem;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            transition: all 0.3s ease;
        }
        .recommendation-bullet:hover {
            transform: translateX(5px);
            border-color: rgba(255,255,255,0.2);
        }
        </style>
        <div class="recommendations-container">
    """, unsafe_allow_html=True)
    
    for i, bullet in enumerate(bullets, 1):
        st.markdown(f'<div class="recommendation-bullet">🎯 {i}. {bullet}</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def generate_report_pdf(user_input: Dict[str, Any], metrics: Dict[str, float],
                       allocations: Dict[str, float], bullets: List[str]) -> bytes:
    """Generate a PDF report of the financial analysis."""
    from fpdf import FPDF
    
    # Save charts as images
    plt.style.use('default')  # Use default style instead of dark_background for PDF
    
    # Portfolio Allocation Chart
    plt.figure(figsize=(10, 8))
    colors = ['#4B56D2', '#82C3EC', '#47B5FF', '#256D85', '#06283D', '#1363DF']
    plt.pie(allocations.values(), labels=allocations.keys(), autopct='%1.1f%%', colors=colors)
    plt.title('Portfolio Allocation', pad=20, size=16)
    
    # Save to BytesIO
    allocation_img = io.BytesIO()
    plt.savefig(allocation_img, format='png', bbox_inches='tight', dpi=300, 
                facecolor='white', edgecolor='none')
    plt.close()
    allocation_img.seek(0)
    
    # Risk vs Return Chart
    plt.figure(figsize=(10, 8))
    risk_return_data = {
        'Stocks': (20, 12),
        'Bonds': (5, 5),
        'Gold': (15, 8),
        'Real Estate': (12, 9),
        'Cash': (1, 3),
        'Fixed Deposits': (2, 4)
    }
    
    # Plot all assets with minimum size for non-allocated ones
    for i, (asset, (risk, ret)) in enumerate(risk_return_data.items()):
        size = max(allocations.get(asset, 0) * 1000, 200)  # Minimum size of 200 for visibility
        plt.scatter(risk, ret, s=size, label=asset, color=colors[i % len(colors)],
                   alpha=0.7 if asset in allocations else 0.4)
        plt.annotate(asset, (risk, ret), xytext=(5, 5), textcoords='offset points')
    
    plt.xlabel('Risk (%)')
    plt.ylabel('Expected Return (%)')
    plt.title('Risk vs Return Profile', pad=20, size=16)
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Save to BytesIO
    risk_return_img = io.BytesIO()
    plt.savefig(risk_return_img, format='png', bbox_inches='tight', dpi=300,
                facecolor='white', edgecolor='none')
    plt.close()
    risk_return_img.seek(0)
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Your Financial Analysis Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Personal Information Section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Personal Information', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(60, 8, 'Age:', 0, 0)
    pdf.cell(0, 8, str(user_input.get('age', 'N/A')), 0, 1)
    pdf.cell(60, 8, 'Monthly Income:', 0, 0)
    pdf.cell(0, 8, format_currency(user_input.get('salary', 0)), 0, 1)
    pdf.cell(60, 8, 'Monthly Expenses:', 0, 0)
    pdf.cell(0, 8, format_currency(user_input.get('expenses', 0)), 0, 1)
    pdf.cell(60, 8, 'Risk Tolerance:', 0, 0)
    pdf.cell(0, 8, str(user_input.get('risk_tolerance', 'N/A')), 0, 1)
    pdf.cell(60, 8, 'Time Horizon:', 0, 0)
    pdf.cell(0, 8, str(user_input.get('time_horizon', 'N/A')), 0, 1)
    pdf.ln(10)
    
    # Financial Metrics Section
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Financial Metrics', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(60, 8, 'Investment Capacity:', 0, 0)
    pdf.cell(0, 8, format_currency(metrics.get('investment_capacity', 0)), 0, 1)
    pdf.cell(60, 8, 'Emergency Fund:', 0, 0)
    pdf.cell(0, 8, format_currency(metrics.get('emergency_fund', 0)), 0, 1)
    pdf.cell(60, 8, 'Debt-to-Income:', 0, 0)
    pdf.cell(0, 8, format_percentage(metrics.get('debt_to_income', 0)), 0, 1)
    pdf.cell(60, 8, 'Risk Score:', 0, 0)
    pdf.cell(0, 8, f"{metrics.get('risk_score', 0)}/10", 0, 1)
    pdf.ln(10)
    
    # Portfolio Allocation Chart
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Portfolio Allocation', 0, 1, 'L')
    pdf.image(allocation_img, x=10, w=190)
    pdf.ln(10)
    
    # Risk vs Return Chart
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Risk vs Return Profile', 0, 1, 'L')
    pdf.image(risk_return_img, x=10, w=190)
    pdf.ln(10)
    
    # Investment Recommendations
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Investment Recommendations', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    for bullet in bullets:
        pdf.multi_cell(0, 8, f"• {bullet}", 0, 'L')
    
    try:
        return pdf.output(dest='S').encode('latin1')
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None