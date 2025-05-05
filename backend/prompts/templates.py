def build_prompt(profile, metrics):
    rules = '''
Essential Financial Rules for Investing & Diversification:
1. The Rule of 100: Subtract your age from 100 to estimate the % of your portfolio in equities; the rest in bonds/fixed income.
2. Emergency Fund: Always keep 3–6 months of expenses in an emergency fund before investing.
3. Diversify: Mix asset classes—equities, bonds, real estate, gold, etc.
4. Align With Risk Tolerance: Match your portfolio to your risk comfort.
5. Time Horizon: Invest conservatively if you need money soon; take more risk if investing for the long term.
6. Rebalance: Regularly review and adjust your portfolio.
7. Avoid Market Timing: Invest regularly instead of trying to time the market.
8. Minimize Costs: Prefer low-cost index funds/ETFs.
9. Tax Efficiency: Consider tax impacts (long/short-term gains).
10. Set Clear Goals: Know your investment objectives and match your strategy.
'''
    return f"""
User Profile:
- Salary: {profile.salary} (INR)
- Expenses: {profile.expenses} (INR)
- Loans: {profile.loans} (INR)
- Age: {profile.age}
- Risk Tolerance: {profile.risk_tolerance}
- Time Horizon: {profile.time_horizon}
- Existing Investments: {profile.existing_investments}
- Goals: {profile.goals}

Financial Metrics:
- Investment Capacity: {metrics.get('investment_capacity', 'N/A')} (INR)
- Risk Score: {metrics.get('risk_score', 'N/A')}

All monetary values are in INR (Indian Rupees).

{rules}

Please:
- Reference the most relevant rules above for this user's profile and situation.
- Provide personalized tips based on their age, risk tolerance, goals, and time horizon.
- Give a recommended portfolio allocation (percentages by asset class and sector), a short narrative explanation, and 2-3 next steps for the user. Ensure all currency references are in INR.
"""
