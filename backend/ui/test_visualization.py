import pytest
import pandas as pd
import numpy as np
from backend.ui.visualization import (
    display_metrics_table,
    generate_excel_report,
    create_allocation_chart,
    create_risk_return_chart
)

@pytest.fixture
def sample_metrics():
    return {
        'investment_capacity': 5000.0,
        'emergency_fund': 15000.0,
        'debt_to_income': 0.25,
        'risk_score': 7,
        'target_emergency_fund': 90000.0  # 6 months of expenses
    }

@pytest.fixture
def sample_allocations():
    return {
        'Stocks': 0.4,
        'Bonds': 0.2,
        'Gold': 0.15,
        'Real Estate': 0.15,
        'Cash': 0.05,
        'Fixed Deposits': 0.05
    }

@pytest.fixture
def sample_user_input():
    return {
        'age': 35,
        'salary': 100000,
        'expenses': 15000,
        'risk_tolerance': 'Moderate',
        'time_horizon': '10-15 years'
    }

@pytest.fixture
def sample_bullets():
    return [
        'Consider increasing emergency fund contributions',
        'Maintain diversified portfolio allocation',
        'Review investment strategy quarterly'
    ]

def test_excel_report_generation(sample_user_input, sample_metrics, sample_allocations, sample_bullets):
    # Generate Excel report
    excel_data = generate_excel_report(sample_user_input, sample_metrics, sample_allocations, sample_bullets)
    
    # Read the Excel file using pandas
    excel_buffer = pd.ExcelFile(excel_data)
    
    # Test if all expected sheets are present
    expected_sheets = ['Personal Information', 'Financial Metrics', 'Portfolio Allocation', 
                      'Risk-Return Profile', 'Recommendations']
    assert all(sheet in excel_buffer.sheet_names for sheet in expected_sheets)
    
    # Test Personal Information sheet
    personal_info = pd.read_excel(excel_buffer, 'Personal Information')
    assert personal_info['Value'].iloc[0] == 35  # Age
    assert '$100,000.00' in personal_info['Value'].iloc[1]  # Monthly Income
    
    # Test Financial Metrics sheet
    financial_metrics = pd.read_excel(excel_buffer, 'Financial Metrics')
    assert '$5,000.00' in financial_metrics['Value'].iloc[0]  # Investment Capacity
    assert '$15,000.00' in financial_metrics['Value'].iloc[1]  # Emergency Fund
    
    # Test Portfolio Allocation sheet
    portfolio = pd.read_excel(excel_buffer, 'Portfolio Allocation')
    assert '40.0%' in portfolio['Allocation (%)'].iloc[0]  # Stocks allocation
    assert '20.0%' in portfolio['Allocation (%)'].iloc[1]  # Bonds allocation

def test_allocation_chart(sample_allocations):
    fig = create_allocation_chart(sample_allocations)
    
    # Test chart properties
    assert fig.layout.title.text == 'Recommended Portfolio Allocation'
    assert fig.layout.width == 800
    assert fig.layout.height == 600
    
    # Test data properties
    pie_data = fig.data[0]
    assert pie_data.type == 'pie'
    assert len(pie_data.labels) == len(sample_allocations)
    assert all(label in sample_allocations.keys() for label in pie_data.labels)

def test_risk_return_chart(sample_allocations):
    fig = create_risk_return_chart(sample_allocations)
    
    # Test chart properties
    assert fig.layout.title.text == 'Risk vs Return Profile'
    assert fig.layout.xaxis.title.text == 'Risk (%)'
    assert fig.layout.yaxis.title.text == 'Expected Return (%)'
    
    # Test data properties
    assert len(fig.data) == len(sample_allocations)
    for trace in fig.data:
        assert trace.type == 'scatter'
        assert trace.mode == 'markers+text'

def test_emergency_fund_calculation(sample_metrics):
    current_fund = sample_metrics['emergency_fund']
    target_fund = sample_metrics['target_emergency_fund']
    monthly_allocation = (target_fund - current_fund) * 0.1  # 10% monthly contribution
    
    # Test emergency fund calculations
    assert target_fund == 90000.0  # 6 months of expenses
    assert monthly_allocation == 7500.0  # 10% of the gap
    
    # Test that target is 6 times the monthly expenses
    monthly_expenses = target_fund / 6
    assert monthly_expenses == 15000.0