"""
Formatting utilities for consistent data presentation across the financial advisor app.
"""

import locale
locale.setlocale(locale.LC_ALL, '')

def format_currency(amount, currency_symbol='₹', decimals=0):
    """Format a number as currency with thousands separator and currency symbol."""
    try:
        amount = float(amount)
        formatted = f"{currency_symbol}{amount:,.{decimals}f}"
        return formatted
    except (ValueError, TypeError):
        return f"{currency_symbol}0"

def format_percentage(value, decimals=1):
    """Format a number as a percentage string."""
    try:
        value = float(value)
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"

def format_number(number, decimals=0):
    """Format a number with thousands separator."""
    try:
        number = float(number)
        return f"{number:,.{decimals}f}"
    except (ValueError, TypeError):
        return "0"

def format_table_row(row_dict, columns):
    """Format a dictionary as a table row string for reports."""
    return ' | '.join(str(row_dict.get(col, '')) for col in columns)

def format_investment_allocation(allocation_dict, investment_capacity, currency_symbol='₹'):
    """Return a list of dicts with asset class, percentage, and formatted amount."""
    result = []
    for asset, pct in allocation_dict.items():
        try:
            pct_val = float(pct)
        except (ValueError, TypeError):
            pct_val = 0
        amount = round((pct_val / 100) * investment_capacity)
        result.append({
            "Asset Class": asset,
            "Percentage": format_percentage(pct_val),
            "Amount (INR)": format_currency(amount, currency_symbol)
        })
    return result