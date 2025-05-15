import pandas as pd
import io
from typing import Dict, List, Any
from backend.utils.formatters import format_currency, format_percentage

def generate_financial_report(metrics: Dict[str, float], allocations: Dict[str, float], table_data: List[Dict[str, Any]], bullets: List[str]) -> io.BytesIO:
    """Generate an Excel report containing financial analysis and recommendations.
    
    Args:
        metrics: Dictionary of financial metrics
        allocations: Dictionary of portfolio allocations
        table_data: List of dictionaries containing allocation details
        bullets: List of recommendation bullets
        
    Returns:
        BytesIO object containing the Excel file
    """
    # Create Excel writer object
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#4B56D2',
            'font_color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'font_size': 11,
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'num_format': '₹#,##0.00'
        })
        
        percent_format = workbook.add_format({
            'font_size': 11,
            'border': 1,
            'num_format': '0.0%'
        })
        
        # Financial Metrics Sheet
        metrics_df = pd.DataFrame([
            ['Monthly Investment Capacity', metrics.get('investment_capacity', 0)],
            ['Debt-to-Income Ratio', metrics.get('debt_to_income', 0)],
            ['Current Emergency Fund', metrics.get('emergency_fund', 0)],
            ['Target Emergency Fund', metrics.get('target_emergency_fund', 0)],
            ['Monthly Emergency Fund Allocation', metrics.get('monthly_emergency_allocation', 0)]
        ], columns=['Metric', 'Value'])
        
        metrics_sheet = writer.book.add_worksheet('Financial Metrics')
        metrics_sheet.set_column('A:A', 30)
        metrics_sheet.set_column('B:B', 20)
        
        metrics_sheet.write_row(0, 0, metrics_df.columns, header_format)
        for idx, (metric, value) in enumerate(metrics_df.values, 1):
            metrics_sheet.write(idx, 0, metric, cell_format)
            if 'Ratio' in metric:
                metrics_sheet.write(idx, 1, value, percent_format)
            else:
                metrics_sheet.write(idx, 1, value, currency_format)
        
        # Portfolio Allocation Sheet
        allocation_df = pd.DataFrame(table_data)
        allocation_sheet = writer.book.add_worksheet('Portfolio Allocation')
        allocation_sheet.set_column('A:A', 20)
        allocation_sheet.set_column('B:B', 15)
        allocation_sheet.set_column('C:C', 20)
        
        allocation_sheet.write_row(0, 0, allocation_df.columns, header_format)
        for idx, row in enumerate(allocation_df.values, 1):
            allocation_sheet.write(idx, 0, row[0], cell_format)  # Asset Class
            allocation_sheet.write(idx, 1, float(row[1].strip('%')) / 100, percent_format)  # Percentage
            allocation_sheet.write(idx, 2, float(row[2].strip('₹').replace(',', '')), currency_format)  # Amount
        
        # Recommendations Sheet
        recommendations_sheet = writer.book.add_worksheet('Recommendations')
        recommendations_sheet.set_column('A:A', 100)
        
        recommendations_sheet.write(0, 0, 'Investment Recommendations', header_format)
        for idx, bullet in enumerate(bullets, 1):
            recommendations_sheet.write(idx, 0, bullet, cell_format)
    
    output.seek(0)
    return output