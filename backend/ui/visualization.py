import streamlit as st
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import pdfkit
import base64
import pandas as pd
from typing import Dict, List, Any
from backend.utils.formatters import format_currency, format_percentage
import tempfile

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
        current_emergency_fund = display_metrics.get('emergency_fund', 0)
        target_emergency_fund = display_metrics.get('target_emergency_fund', current_emergency_fund * 6)  # 6 months of expenses
        monthly_allocation = (target_emergency_fund - current_emergency_fund) * 0.1  # 10% monthly contribution
        
        st.metric(
            'Emergency Fund Status',
            format_currency(current_emergency_fund),
            delta=f"Target: {format_currency(target_emergency_fund)}",
            help="Current emergency fund vs target (6 months of expenses)"
        )
        st.metric(
            'Monthly Emergency Fund Allocation',
            format_currency(monthly_allocation),
            delta=None,
            help="Recommended monthly contribution to emergency fund"
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

def display_download_buttons(user_input: Dict[str, Any], metrics: Dict[str, float],
                           allocations: Dict[str, float], bullets: List[str]) -> None:
    """Display download button for Excel report."""
    try:
        # Generate Excel report
        excel_report = generate_excel_report(user_input, metrics, allocations, bullets)
        
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_report,
            file_name="financial_analysis_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download a detailed Excel spreadsheet of your financial analysis"
        )
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")

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

def generate_excel_report(user_input: Dict[str, Any], metrics: Dict[str, float],
                         allocations: Dict[str, float], bullets: List[str]) -> bytes:
    """Generate an Excel report with all numerical data from the financial analysis."""
    # Create a BytesIO object to store the Excel file
    excel_buffer = io.BytesIO()
    
    # Create an Excel writer object
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        # Personal Information
        personal_info = pd.DataFrame({
            'Metric': ['Age', 'Monthly Income', 'Monthly Expenses', 'Risk Tolerance', 'Time Horizon'],
            'Value': [
                user_input.get('age', 'N/A'),
                format_currency(user_input.get('salary', 0)),
                format_currency(user_input.get('expenses', 0)),
                user_input.get('risk_tolerance', 'N/A'),
                user_input.get('time_horizon', 'N/A')
            ]
        })
        personal_info.to_excel(writer, sheet_name='Personal Information', index=False)
        
        # Financial Metrics
        financial_metrics = pd.DataFrame({
            'Metric': ['Investment Capacity', 'Emergency Fund', 'Target Emergency Fund',
                      'Monthly Emergency Fund Allocation', 'Debt-to-Income Ratio', 'Risk Score'],
            'Value': [
                format_currency(metrics.get('investment_capacity', 0)),
                format_currency(metrics.get('emergency_fund', 0)),
                format_currency(metrics.get('target_emergency_fund', metrics.get('emergency_fund', 0) * 6)),
                format_currency((metrics.get('target_emergency_fund', metrics.get('emergency_fund', 0) * 6) - 
                               metrics.get('emergency_fund', 0)) * 0.1),
                format_percentage(metrics.get('debt_to_income', 0)),
                f"{metrics.get('risk_score', 0)}/10"
            ]
        })
        financial_metrics.to_excel(writer, sheet_name='Financial Metrics', index=False)
        
        # Portfolio Allocation
        portfolio_data = pd.DataFrame({
            'Asset Class': list(allocations.keys()),
            'Allocation (%)': [f"{value * 100:.1f}%" for value in allocations.values()]
        })
        portfolio_data.to_excel(writer, sheet_name='Portfolio Allocation', index=False)
        
        # Risk-Return Data
        risk_return_data = {
            'Stocks': {'risk': 20, 'return': 12},
            'Bonds': {'risk': 5, 'return': 5},
            'Gold': {'risk': 15, 'return': 8},
            'Real Estate': {'risk': 12, 'return': 9},
            'Cash': {'risk': 1, 'return': 3},
            'Fixed Deposits': {'risk': 2, 'return': 4},
        }
        risk_return_df = pd.DataFrame([
            {'Asset': asset, 'Risk (%)': data['risk'], 'Return (%)': data['return']}
            for asset, data in risk_return_data.items()
        ])
        risk_return_df.to_excel(writer, sheet_name='Risk-Return Profile', index=False)
        
        # Recommendations
        recommendations = pd.DataFrame({
            'Recommendation': bullets
        })
        recommendations.to_excel(writer, sheet_name='Recommendations', index=False)
        
        # Auto-adjust columns width
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(worksheet.get_cols()):
                max_length = max(len(str(cell.value)) for cell in col)
                worksheet.set_column(idx, idx, max_length + 2)
    
    # Get the value of the BytesIO buffer
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def generate_report_pdf(user_input: Dict[str, Any], metrics: Dict[str, float],
                       allocations: Dict[str, float], bullets: List[str]) -> bytes:
    """Generate a PDF report of the financial analysis."""
    from fpdf import FPDF
    try:
        # Create temporary files for charts
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as allocation_file, \
             tempfile.NamedTemporaryFile(suffix='.png', delete=False) as risk_return_file:
            
            # Save allocation chart
            allocation_fig = create_allocation_chart(allocations)
            allocation_fig.write_image(allocation_file.name)
            allocation_img_path = allocation_file.name
            
            # Save risk-return chart
            risk_return_fig = create_risk_return_chart(allocations)
            risk_return_fig.write_image(risk_return_file.name)
            risk_return_img_path = risk_return_file.name
            
            # Get font path
            font_path = 'backend/ui/NotoSans-Regular.ttf'
            # Create PDF document
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('NotoSans', '', font_path, uni=True)
            
            # Set default text color to black
            pdf.set_text_color(0, 0, 0)
            
            # Header
            pdf.set_font('NotoSans', '', 20)
            pdf.cell(0, 15, 'Your Financial Analysis Report', 0, 1, 'C')
            pdf.ln(5)
            
            # Personal Information Section
            pdf.set_font('NotoSans', '', 16)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, 'Personal Information', 0, 1, 'L', fill=True)
            pdf.ln(5)
            
            pdf.set_font('NotoSans', '', 12)
            # Create a function for consistent formatting
            def add_info_row(label, value):
                pdf.set_font('NotoSans', '', 12)
                pdf.cell(60, 8, label, 0, 0)
                pdf.cell(0, 8, str(value), 0, 1)
            
            add_info_row('Age:', user_input.get('age', 'N/A'))
            add_info_row('Monthly Income:', format_currency(user_input.get('salary', 0)))
            add_info_row('Monthly Expenses:', format_currency(user_input.get('expenses', 0)))
            add_info_row('Risk Tolerance:', user_input.get('risk_tolerance', 'N/A'))
            add_info_row('Time Horizon:', user_input.get('time_horizon', 'N/A'))
            pdf.ln(5)
            
            # Financial Metrics Section
            pdf.set_font('NotoSans', '', 16)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, 'Financial Metrics', 0, 1, 'L', fill=True)
            pdf.ln(5)
            
            add_info_row('Investment Capacity:', format_currency(metrics.get('investment_capacity', 0)))
            add_info_row('Emergency Fund:', format_currency(metrics.get('emergency_fund', 0)))
            add_info_row('Debt-to-Income:', format_percentage(metrics.get('debt_to_income', 0)))
            add_info_row('Risk Score:', f"{metrics.get('risk_score', 0)}/10")
            pdf.ln(5)
            
            # Portfolio Allocation Section
            pdf.set_font('NotoSans', '', 16)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, 'Portfolio Allocation', 0, 1, 'L', fill=True)
            pdf.ln(5)
            pdf.image(allocation_img_path, x=10, w=190)
            pdf.ln(10)
            
            # Risk vs Return Profile Section
            pdf.add_page()
            pdf.set_font('NotoSans', '', 16)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, 'Risk vs Return Profile', 0, 1, 'L', fill=True)
            pdf.ln(5)
            pdf.image(risk_return_img_path, x=10, w=190)
            pdf.ln(10)
            
            # Investment Recommendations Section
            pdf.set_font('NotoSans', '', 16)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, 'Investment Recommendations', 0, 1, 'L', fill=True)
            pdf.ln(5)
            
            pdf.set_font('NotoSans', '', 12)
            for bullet in bullets:
                pdf.multi_cell(0, 8, f"• {bullet}", 0, 'L')
            
            return pdf.output(dest='S').encode('utf-8')
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return b""