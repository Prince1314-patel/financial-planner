import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import io
import base64
from typing import Dict, List, Any, Optional
import xlsxwriter
from backend.utils.formatters import format_currency, format_percentage

class AdvancedReportGenerator:
    
    @staticmethod
    def generate_comprehensive_report(metrics: Dict[str, Any], allocations: Dict[str, float], 
                                    ai_analysis: Dict[str, Any], user_profile: Dict[str, Any],
                                    market_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate comprehensive financial report with multiple sections"""
        
        report_data = {
            "executive_summary": AdvancedReportGenerator._generate_executive_summary(metrics, allocations),
            "financial_health": AdvancedReportGenerator._analyze_financial_health(metrics),
            "portfolio_analysis": AdvancedReportGenerator._analyze_portfolio(allocations, metrics),
            "goal_tracking": AdvancedReportGenerator._analyze_goals(metrics.get('goal_analysis', {})),
            "risk_analysis": AdvancedReportGenerator._analyze_risk_profile(metrics, allocations),
            "projections": AdvancedReportGenerator._generate_projections_analysis(metrics),
            "tax_optimization": AdvancedReportGenerator._generate_tax_analysis(metrics),
            "action_plan": AdvancedReportGenerator._generate_action_plan(metrics, allocations),
            "market_context": market_context or {},
            "benchmarking": AdvancedReportGenerator._generate_benchmarking(metrics),
            "generated_at": datetime.now().isoformat()
        }
        
        return report_data
    
    @staticmethod
    def _generate_executive_summary(metrics: Dict[str, Any], allocations: Dict[str, float]) -> Dict[str, Any]:
        """Generate executive summary section"""
        
        investment_capacity = metrics.get('investment_capacity', 0)
        financial_health = metrics.get('financial_health_score', 0)
        savings_rate = metrics.get('savings_rate', 0)
        
        # Determine overall financial status
        if financial_health >= 80:
            status = "Excellent"
            status_color = "green"
        elif financial_health >= 60:
            status = "Good"
            status_color = "blue"
        elif financial_health >= 40:
            status = "Fair"
            status_color = "orange"
        else:
            status = "Needs Improvement"
            status_color = "red"
        
        # Key insights
        insights = []
        
        if savings_rate >= 25:
            insights.append("🎯 Excellent savings rate - you're on track for financial independence")
        elif savings_rate >= 15:
            insights.append("👍 Good savings discipline - consider increasing investment allocation")
        else:
            insights.append("⚠️ Focus on increasing savings rate for better financial outcomes")
        
        if metrics.get('emergency_fund_months', 0) >= 6:
            insights.append("🛡️ Emergency fund adequately funded")
        else:
            insights.append("🚨 Priority: Build emergency fund to 6 months of expenses")
        
        # Top recommendations
        recommendations = []
        
        if investment_capacity > 0:
            recommendations.append(f"Invest ₹{investment_capacity:,.0f} monthly in recommended portfolio")
        
        emergency_gap = metrics.get('emergency_fund_gap', 0)
        if emergency_gap > 0:
            recommendations.append(f"Build emergency fund by ₹{emergency_gap:,.0f}")
        
        if metrics.get('lifestyle_allocation', 0) > 0:
            recommendations.append(f"Allocated ₹{metrics['lifestyle_allocation']:,.0f} for lifestyle expenses")
        
        return {
            "financial_status": status,
            "status_color": status_color,
            "health_score": financial_health,
            "monthly_investment_capacity": investment_capacity,
            "savings_rate": savings_rate,
            "key_insights": insights,
            "top_recommendations": recommendations,
            "portfolio_summary": {
                "total_asset_classes": len(allocations),
                "highest_allocation": max(allocations.items(), key=lambda x: x[1]) if allocations else ("None", 0),
                "risk_level": AdvancedReportGenerator._classify_portfolio_risk(allocations)
            }
        }
    
    @staticmethod
    def _analyze_financial_health(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial health with detailed breakdown"""
        
        health_score = metrics.get('financial_health_score', 0)
        
        # Component analysis
        components = {
            "Emergency Fund": {
                "score": min(25, metrics.get('emergency_fund_months', 0) * 4.2),
                "max_score": 25,
                "status": "Good" if metrics.get('emergency_fund_months', 0) >= 6 else "Needs Work",
                "details": f"{metrics.get('emergency_fund_months', 0):.1f} months of expenses covered"
            },
            "Savings Rate": {
                "score": min(30, metrics.get('savings_rate', 0)),
                "max_score": 30,
                "status": "Excellent" if metrics.get('savings_rate', 0) >= 25 else "Good" if metrics.get('savings_rate', 0) >= 15 else "Needs Work",
                "details": f"{metrics.get('savings_rate', 0):.1f}% of income saved"
            },
            "Debt Management": {
                "score": 20 if metrics.get('debt_to_income', 0) < 0.3 else 10,
                "max_score": 20,
                "status": "Good" if metrics.get('debt_to_income', 0) < 0.3 else "Monitor",
                "details": f"{metrics.get('debt_to_income', 0):.1%} debt-to-income ratio"
            },
            "Investment Discipline": {
                "score": 15 if metrics.get('investment_capacity', 0) > 0 else 5,
                "max_score": 15,
                "status": "Active" if metrics.get('investment_capacity', 0) > 0 else "Starting",
                "details": f"₹{metrics.get('investment_capacity', 0):,.0f} monthly investment capacity"
            }
        }
        
        # Improvement recommendations
        improvements = []
        
        for component, data in components.items():
            if data['score'] < data['max_score'] * 0.7:
                if component == "Emergency Fund":
                    improvements.append("Build emergency fund to 6+ months of expenses")
                elif component == "Savings Rate":
                    improvements.append("Increase savings rate by reducing unnecessary expenses")
                elif component == "Debt Management":
                    improvements.append("Focus on debt reduction to improve financial flexibility")
                elif component == "Investment Discipline":
                    improvements.append("Start systematic investment planning")
        
        return {
            "overall_score": health_score,
            "grade": AdvancedReportGenerator._score_to_grade(health_score),
            "components": components,
            "strengths": [comp for comp, data in components.items() if data['status'] in ['Good', 'Excellent']],
            "improvements": improvements,
            "benchmark": {
                "excellent": "80+",
                "good": "60-79",
                "fair": "40-59",
                "poor": "<40"
            }
        }
    
    @staticmethod
    def _analyze_portfolio(allocations: Dict[str, float], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed portfolio analysis"""
        
        if not allocations:
            return {"error": "No allocation data available"}
        
        # Categorize allocations
        equity_assets = ["Large Cap Stocks", "Mid Cap Stocks", "Small Cap Stocks", "International Stocks"]
        debt_assets = ["Government Bonds", "Corporate Bonds"]
        alternative_assets = ["Gold/Commodities", "Cash/FD", "Real Estate"]
        
        equity_percent = sum(allocations.get(asset, 0) for asset in equity_assets)
        debt_percent = sum(allocations.get(asset, 0) for asset in debt_assets)
        alternative_percent = sum(allocations.get(asset, 0) for asset in alternative_assets)
        
        # Risk assessment
        risk_level = AdvancedReportGenerator._classify_portfolio_risk(allocations)
        
        # Expected returns (historical approximations)
        expected_returns = {
            "Large Cap Stocks": 12.0,
            "Mid Cap Stocks": 14.0,
            "Small Cap Stocks": 16.0,
            "International Stocks": 10.0,
            "Government Bonds": 7.0,
            "Corporate Bonds": 8.5,
            "Gold/Commodities": 8.0,
            "Cash/FD": 6.0,
            "Real Estate": 11.0
        }
        
        # Calculate portfolio expected return
        portfolio_return = sum(
            allocations.get(asset, 0) * expected_returns.get(asset, 8.0) / 100 
            for asset in allocations.keys()
        )
        
        # Diversification analysis
        diversification_score = AdvancedReportGenerator._calculate_diversification_score(allocations)
        
        return {
            "allocation_summary": {
                "equity_percent": round(equity_percent, 1),
                "debt_percent": round(debt_percent, 1),
                "alternative_percent": round(alternative_percent, 1)
            },
            "risk_metrics": {
                "risk_level": risk_level,
                "expected_annual_return": round(portfolio_return, 1),
                "diversification_score": diversification_score
            },
            "asset_breakdown": allocations,
            "rebalancing_frequency": AdvancedReportGenerator._suggest_rebalancing_frequency(risk_level),
            "tax_efficiency": AdvancedReportGenerator._assess_tax_efficiency(allocations),
            "liquidity_analysis": AdvancedReportGenerator._analyze_liquidity(allocations)
        }
    
    @staticmethod
    def _analyze_goals(goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial goals and progress tracking"""
        
        if not goal_analysis:
            return {"message": "No specific goals analyzed"}
        
        detected_goals = goal_analysis.get('detected_goals', [])
        recommendations = goal_analysis.get('recommendations', [])
        
        # Goal prioritization
        goal_priority = {
            "emergency": 1,
            "retirement": 2,
            "home": 3,
            "education": 4,
            "business": 5,
            "travel": 6
        }
        
        prioritized_goals = sorted(detected_goals, key=lambda x: goal_priority.get(x, 10))
        
        # Goal-specific analysis
        goal_details = {}
        
        for goal in prioritized_goals:
            if goal == "retirement":
                goal_details[goal] = {
                    "priority": "High",
                    "time_sensitivity": "Long-term",
                    "strategy": "Systematic equity investment with gradual debt shift",
                    "tax_benefits": "Use 80C, NPS for maximum tax efficiency"
                }
            elif goal == "home":
                goal_details[goal] = {
                    "priority": "Medium",
                    "time_sensitivity": "Medium-term",
                    "strategy": "Balanced funds with liquid component for down payment",
                    "tax_benefits": "Home loan tax benefits available"
                }
            elif goal == "education":
                goal_details[goal] = {
                    "priority": "High",
                    "time_sensitivity": "Depends on timeline",
                    "strategy": "Education-specific funds or balanced approach",
                    "tax_benefits": "Education loan tax benefits if needed"
                }
        
        return {
            "detected_goals": detected_goals,
            "prioritized_goals": prioritized_goals,
            "goal_recommendations": recommendations,
            "goal_details": goal_details,
            "tracking_suggestions": AdvancedReportGenerator._suggest_goal_tracking(detected_goals)
        }
    
    @staticmethod
    def _analyze_risk_profile(metrics: Dict[str, Any], allocations: Dict[str, float]) -> Dict[str, Any]:
        """Comprehensive risk analysis"""
        
        risk_score = metrics.get('risk_score', 5.0)
        risk_capacity = metrics.get('risk_capacity', 'Medium')
        age = metrics.get('user_age', 30)
        
        # Risk tolerance vs capacity analysis
        portfolio_risk = AdvancedReportGenerator._classify_portfolio_risk(allocations)
        
        risk_alignment = "Aligned"
        if "High" in risk_capacity and portfolio_risk in ["Conservative", "Moderate"]:
            risk_alignment = "Under-utilizing risk capacity"
        elif "Low" in risk_capacity and portfolio_risk == "Aggressive":
            risk_alignment = "Excessive risk for capacity"
        
        # Volatility analysis
        volatility_estimate = AdvancedReportGenerator._estimate_portfolio_volatility(allocations)
        
        # Risk mitigation suggestions
        mitigation_strategies = []
        
        if volatility_estimate > 20:
            mitigation_strategies.append("Consider reducing small-cap allocation")
            mitigation_strategies.append("Increase debt component for stability")
        
        if age > 50 and portfolio_risk == "Aggressive":
            mitigation_strategies.append("Gradually shift to conservative allocation")
        
        mitigation_strategies.append("Regular portfolio rebalancing")
        mitigation_strategies.append("Systematic investment to reduce timing risk")
        
        return {
            "risk_score": risk_score,
            "risk_capacity": risk_capacity,
            "portfolio_risk": portfolio_risk,
            "risk_alignment": risk_alignment,
            "volatility_estimate": f"{volatility_estimate:.1f}%",
            "mitigation_strategies": mitigation_strategies,
            "stress_test": AdvancedReportGenerator._perform_stress_test(allocations, metrics)
        }
    
    @staticmethod
    def _generate_projections_analysis(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed projections with multiple scenarios"""
        
        projections = metrics.get('projections', {})
        
        if not projections:
            return {"error": "No projection data available"}
        
        scenarios = projections.get('scenarios', {})
        monthly_investment = projections.get('monthly_investment', 0)
        years = projections.get('time_horizon_years', 10)
        
        # Enhanced scenario analysis
        enhanced_scenarios = {}
        
        for scenario_name, scenario_data in scenarios.items():
            nominal_value = scenario_data.get('nominal_value', 0)
            total_invested = scenario_data.get('total_invested', 0)
            
            enhanced_scenarios[scenario_name] = {
                **scenario_data,
                "wealth_multiple": round(nominal_value / total_invested, 1) if total_invested > 0 else 0,
                "annualized_return": round(((nominal_value / total_invested) ** (1/years) - 1) * 100, 1) if total_invested > 0 else 0,
                "probability": AdvancedReportGenerator._scenario_probability(scenario_name)
            }
        
        # Goal achievement analysis
        goal_achievement = {}
        
        if 'retirement' in metrics.get('goal_analysis', {}).get('detected_goals', []):
            retirement_corpus_needed = monthly_investment * 12 * 25  # 25x annual investment
            
            for scenario_name, scenario_data in enhanced_scenarios.items():
                achievement_percentage = min(100, (scenario_data['nominal_value'] / retirement_corpus_needed) * 100)
                goal_achievement[scenario_name] = f"{achievement_percentage:.0f}% of retirement goal"
        
        return {
            "base_assumptions": {
                "monthly_investment": monthly_investment,
                "time_horizon": f"{years} years",
                "inflation_rate": "6% annually"
            },
            "scenarios": enhanced_scenarios,
            "goal_achievement": goal_achievement,
            "sensitivity_analysis": AdvancedReportGenerator._perform_sensitivity_analysis(monthly_investment, years),
            "recommendations": AdvancedReportGenerator._projection_recommendations(enhanced_scenarios)
        }
    
    @staticmethod
    def _generate_tax_analysis(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive tax optimization analysis"""
        
        tax_suggestions = metrics.get('tax_suggestions', [])
        investment_capacity = metrics.get('investment_capacity', 0)
        annual_investment = investment_capacity * 12
        
        # Tax-saving potential
        tax_savings_potential = 0
        tax_efficient_instruments = []
        
        for suggestion in tax_suggestions:
            if suggestion.get('type') == 'ELSS Investment':
                tax_savings_potential += 46800  # Max 80C benefit
                tax_efficient_instruments.append("ELSS Mutual Funds")
            elif suggestion.get('type') == 'PPF Investment':
                tax_efficient_instruments.append("Public Provident Fund")
            elif suggestion.get('type') == 'NPS Investment':
                tax_savings_potential += 15600  # Additional 80CCD(1B)
                tax_efficient_instruments.append("National Pension System")
        
        # Tax-loss harvesting opportunities
        tax_loss_strategies = [
            "Book losses in direct equity before year-end",
            "Use debt fund indexation benefits for long-term holdings",
            "Consider LTCG harvesting for equity funds",
            "Plan withdrawal timing for tax efficiency"
        ]
        
        # Asset location optimization
        asset_location = {
            "Taxable Accounts": ["Large Cap Equity", "International Funds", "Gold ETF"],
            "Tax-Deferred (ELSS)": ["Mid Cap Funds", "Small Cap Funds"],
            "Tax-Free (PPF/EPF)": ["Debt Funds", "Hybrid Funds"]
        }
        
        return {
            "tax_savings_potential": tax_savings_potential,
            "tax_efficient_instruments": tax_efficient_instruments,
            "detailed_suggestions": tax_suggestions,
            "tax_loss_strategies": tax_loss_strategies,
            "asset_location_strategy": asset_location,
            "annual_tax_planning": AdvancedReportGenerator._generate_annual_tax_calendar()
        }
    
    @staticmethod
    def _generate_action_plan(metrics: Dict[str, Any], allocations: Dict[str, float]) -> Dict[str, Any]:
        """Generate detailed action plan with timelines"""
        
        # Immediate actions (Next 30 days)
        immediate_actions = []
        
        emergency_gap = metrics.get('emergency_fund_gap', 0)
        if emergency_gap > 0:
            immediate_actions.append({
                "action": "Open high-yield savings account for emergency fund",
                "timeline": "This week",
                "priority": "High"
            })
        
        if metrics.get('investment_capacity', 0) > 0:
            immediate_actions.append({
                "action": "Open investment account with low-cost broker",
                "timeline": "Next 2 weeks",
                "priority": "High"
            })
        
        # Short-term actions (Next 3 months)
        short_term_actions = []
        
        if allocations:
            short_term_actions.append({
                "action": "Start systematic investment plan (SIP)",
                "details": f"Begin monthly investment of ₹{metrics.get('investment_capacity', 0):,.0f}",
                "timeline": "Month 1-2",
                "priority": "High"
            })
        
        short_term_actions.append({
            "action": "Set up automatic transfers and investments",
            "timeline": "Month 2",
            "priority": "Medium"
        })
        
        # Medium-term actions (3-12 months)
        medium_term_actions = []
        
        medium_term_actions.append({
            "action": "Review and rebalance portfolio",
            "timeline": "Quarterly",
            "priority": "Medium"
        })
        
        medium_term_actions.append({
            "action": "Optimize tax-saving investments",
            "timeline": "Before March 31st",
            "priority": "High"
        })
        
        # Long-term actions (1+ years)
        long_term_actions = []
        
        long_term_actions.append({
            "action": "Annual financial health checkup",
            "timeline": "Annually",
            "priority": "Medium"
        })
        
        long_term_actions.append({
            "action": "Review life insurance and health coverage",
            "timeline": "Every 2 years",
            "priority": "Medium"
        })
        
        # Monitoring and review schedule
        review_schedule = {
            "Monthly": ["Track expenses", "Monitor SIP investments"],
            "Quarterly": ["Portfolio rebalancing", "Goal progress review"],
            "Semi-annually": ["Insurance review", "Tax planning"],
            "Annually": ["Complete financial audit", "Goal adjustment"]
        }
        
        return {
            "immediate_actions": immediate_actions,
            "short_term_actions": short_term_actions,
            "medium_term_actions": medium_term_actions,
            "long_term_actions": long_term_actions,
            "review_schedule": review_schedule,
            "success_metrics": AdvancedReportGenerator._define_success_metrics(metrics)
        }
    
    @staticmethod
    def _generate_benchmarking(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate benchmarking against peer groups and standards"""
        
        age = metrics.get('user_age', 30)
        income = metrics.get('salary', 0)
        savings_rate = metrics.get('savings_rate', 0)
        
        # Age-based benchmarks
        age_benchmarks = {
            "20s": {"savings_rate": 20, "emergency_months": 3, "investment_focus": "Growth"},
            "30s": {"savings_rate": 25, "emergency_months": 6, "investment_focus": "Aggressive Growth"},
            "40s": {"savings_rate": 30, "emergency_months": 6, "investment_focus": "Balanced"},
            "50s": {"savings_rate": 35, "emergency_months": 9, "investment_focus": "Conservative"}
        }
        
        age_group = "20s" if age < 30 else "30s" if age < 40 else "40s" if age < 50 else "50s"
        benchmark = age_benchmarks.get(age_group, age_benchmarks["30s"])
        
        # Performance vs benchmarks
        performance = {
            "savings_rate": {
                "your_rate": savings_rate,
                "benchmark": benchmark["savings_rate"],
                "status": "Above" if savings_rate >= benchmark["savings_rate"] else "Below"
            },
            "emergency_fund": {
                "your_months": metrics.get('emergency_fund_months', 0),
                "benchmark": benchmark["emergency_months"],
                "status": "Adequate" if metrics.get('emergency_fund_months', 0) >= benchmark["emergency_months"] else "Insufficient"
            }
        }
        
        # Income percentile (rough estimation)
        income_percentile = AdvancedReportGenerator._estimate_income_percentile(income, age)
        
        return {
            "age_group": f"{age_group} (Age {age})",
            "benchmarks": benchmark,
            "your_performance": performance,
            "income_percentile": income_percentile,
            "improvement_areas": AdvancedReportGenerator._identify_improvement_areas(performance, benchmark)
        }
    
    # Helper methods for calculations and analysis
    
    @staticmethod
    def _classify_portfolio_risk(allocations: Dict[str, float]) -> str:
        """Classify portfolio risk level"""
        equity_assets = ["Large Cap Stocks", "Mid Cap Stocks", "Small Cap Stocks", "International Stocks"]
        equity_percent = sum(allocations.get(asset, 0) for asset in equity_assets)
        
        if equity_percent >= 70:
            return "Aggressive"
        elif equity_percent >= 50:
            return "Moderate"
        else:
            return "Conservative"
    
    @staticmethod
    def _score_to_grade(score: int) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        elif score >= 40:
            return "C"
        else:
            return "D"
    
    @staticmethod
    def _calculate_diversification_score(allocations: Dict[str, float]) -> int:
        """Calculate diversification score (0-100)"""
        if not allocations:
            return 0
        
        # Number of asset classes
        num_assets = len([v for v in allocations.values() if v > 0])
        
        # Concentration risk (Herfindahl index)
        herfindahl = sum((v/100)**2 for v in allocations.values())
        
        # Score based on number of assets and concentration
        asset_score = min(50, num_assets * 8)  # Max 50 points for 6+ assets
        concentration_score = max(0, 50 - (herfindahl - 0.2) * 100)  # Penalize concentration
        
        return int(asset_score + concentration_score)
    
    @staticmethod
    def _suggest_rebalancing_frequency(risk_level: str) -> str:
        """Suggest rebalancing frequency based on risk level"""
        frequencies = {
            "Conservative": "Semi-annually",
            "Moderate": "Quarterly", 
            "Aggressive": "Monthly review, quarterly rebalancing"
        }
        return frequencies.get(risk_level, "Quarterly")
    
    @staticmethod
    def _assess_tax_efficiency(allocations: Dict[str, float]) -> str:
        """Assess tax efficiency of portfolio"""
        tax_efficient_assets = ["Government Bonds", "ELSS", "PPF"]
        tax_efficient_percent = sum(allocations.get(asset, 0) for asset in tax_efficient_assets)
        
        if tax_efficient_percent >= 30:
            return "High - Good use of tax-efficient instruments"
        elif tax_efficient_percent >= 15:
            return "Medium - Consider more tax-efficient options"
        else:
            return "Low - Significant tax optimization opportunity"
    
    @staticmethod
    def _analyze_liquidity(allocations: Dict[str, float]) -> Dict[str, Any]:
        """Analyze portfolio liquidity"""
        liquid_assets = ["Cash/FD", "Large Cap Stocks", "Government Bonds"]
        illiquid_assets = ["Real Estate", "Small Cap Stocks"]
        
        liquid_percent = sum(allocations.get(asset, 0) for asset in liquid_assets)
        illiquid_percent = sum(allocations.get(asset, 0) for asset in illiquid_assets)
        
        return {
            "liquid_percentage": round(liquid_percent, 1),
            "illiquid_percentage": round(illiquid_percent, 1),
            "liquidity_score": "High" if liquid_percent >= 40 else "Medium" if liquid_percent >= 25 else "Low",
            "recommendation": "Maintain 20-30% in liquid assets for flexibility"
        }
    
    @staticmethod
    def _suggest_goal_tracking(detected_goals: List[str]) -> List[str]:
        """Suggest goal tracking methods"""
        suggestions = []
        
        if "retirement" in detected_goals:
            suggestions.append("Track retirement corpus monthly using compound interest calculators")
        
        if "home" in detected_goals:
            suggestions.append("Monitor property prices and down payment progress quarterly")
        
        if "education" in detected_goals:
            suggestions.append("Review education cost inflation and fund adequacy annually")
        
        suggestions.append("Set up automated progress reports and alerts")
        
        return suggestions
    
    @staticmethod
    def _estimate_portfolio_volatility(allocations: Dict[str, float]) -> float:
        """Estimate portfolio volatility based on asset class mix"""
        volatilities = {
            "Large Cap Stocks": 15,
            "Mid Cap Stocks": 20,
            "Small Cap Stocks": 25,
            "International Stocks": 18,
            "Government Bonds": 5,
            "Corporate Bonds": 7,
            "Gold/Commodities": 20,
            "Cash/FD": 1,
            "Real Estate": 12
        }
        
        portfolio_volatility = sum(
            allocations.get(asset, 0) * volatilities.get(asset, 15) / 100
            for asset in allocations.keys()
        )
        
        return portfolio_volatility
    
    @staticmethod
    def _perform_stress_test(allocations: Dict[str, float], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Perform stress test on portfolio"""
        
        # Simulate market crash scenarios
        crash_scenarios = {
            "2008_crisis": {"equity_drop": -40, "bond_gain": 10, "gold_gain": 20},
            "covid_crash": {"equity_drop": -25, "bond_gain": 5, "gold_gain": 15},
            "inflation_spike": {"equity_drop": -10, "bond_drop": -15, "gold_gain": 30}
        }
        
        investment_capacity = metrics.get('investment_capacity', 0)
        current_value = investment_capacity * 12  # Assume 1 year invested
        
        stress_results = {}
        
        for scenario, impacts in crash_scenarios.items():
            # Simplified calculation
            equity_impact = sum(allocations.get(asset, 0) for asset in ["Large Cap Stocks", "Mid Cap Stocks", "Small Cap Stocks"]) * impacts.get("equity_drop", 0) / 100
            bond_impact = sum(allocations.get(asset, 0) for asset in ["Government Bonds", "Corporate Bonds"]) * impacts.get("bond_gain", impacts.get("bond_drop", 0)) / 100
            gold_impact = allocations.get("Gold/Commodities", 0) * impacts.get("gold_gain", 0) / 100
            
            total_impact = equity_impact + bond_impact + gold_impact
            stressed_value = current_value * (1 + total_impact / 100)
            
            stress_results[scenario] = {
                "impact_percent": round(total_impact, 1),
                "portfolio_value": round(stressed_value, 0),
                "recovery_time_months": max(6, abs(total_impact) * 2)  # Rough estimate
            }
        
        return stress_results
    
    @staticmethod
    def _scenario_probability(scenario_name: str) -> str:
        """Assign probability to different scenarios"""
        probabilities = {
            "conservative": "80% - High probability",
            "moderate": "60% - Medium probability", 
            "aggressive": "30% - Lower probability, higher upside"
        }
        return probabilities.get(scenario_name, "Unknown")
    
    @staticmethod
    def _perform_sensitivity_analysis(monthly_investment: float, years: int) -> Dict[str, Any]:
        """Perform sensitivity analysis on key variables"""
        
        base_return = 0.12  # 12% base return
        
        sensitivity = {}
        
        # Return sensitivity
        return_scenarios = [0.08, 0.10, 0.12, 0.14, 0.16]
        for ret in return_scenarios:
            monthly_return = ret / 12
            months = years * 12
            fv = monthly_investment * (((1 + monthly_return) ** months - 1) / monthly_return) if monthly_return > 0 else monthly_investment * months
            sensitivity[f"{ret:.0%}_return"] = round(fv, 0)
        
        # Investment amount sensitivity
        investment_scenarios = [0.8, 0.9, 1.0, 1.1, 1.2]
        for mult in investment_scenarios:
            adjusted_investment = monthly_investment * mult
            monthly_return = base_return / 12
            months = years * 12
            fv = adjusted_investment * (((1 + monthly_return) ** months - 1) / monthly_return)
            sensitivity[f"{mult:.0%}_investment"] = round(fv, 0)
        
        return sensitivity
    
    @staticmethod
    def _projection_recommendations(scenarios: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on projections"""
        recommendations = []
        
        conservative_return = scenarios.get('conservative', {}).get('annualized_return', 0)
        aggressive_return = scenarios.get('aggressive', {}).get('annualized_return', 0)
        
        if conservative_return < 8:
            recommendations.append("Consider increasing equity allocation for better returns")
        
        if aggressive_return > 15:
            recommendations.append("Aggressive scenario shows high potential but comes with higher risk")
        
        recommendations.extend([
            "Consider increasing SIP amount annually with salary increments",
            "Review and rebalance portfolio regularly",
            "Stay invested for long-term wealth creation"
        ])
        
        return recommendations
    
    @staticmethod
    def _generate_annual_tax_calendar() -> Dict[str, List[str]]:
        """Generate annual tax planning calendar"""
        return {
            "April-June": ["Start tax-saving investments", "Review previous year's tax efficiency"],
            "July-September": ["Mid-year tax planning review", "Optimize ELSS investments"],
            "October-December": ["Final tax-saving push", "Plan for next year's investments"],
            "January-March": ["Complete tax-saving investments", "Prepare for tax filing"]
        }
    
    @staticmethod
    def _define_success_metrics(metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """Define success metrics for tracking"""
        return [
            {
                "metric": "Monthly Investment Amount",
                "current": f"₹{metrics.get('investment_capacity', 0):,.0f}",
                "target": f"₹{metrics.get('investment_capacity', 0) * 1.1:,.0f}",
                "timeline": "Next year"
            },
            {
                "metric": "Emergency Fund",
                "current": f"{metrics.get('emergency_fund_months', 0):.1f} months",
                "target": "6 months",
                "timeline": "Next 12 months"
            },
            {
                "metric": "Financial Health Score",
                "current": f"{metrics.get('financial_health_score', 0)}/100",
                "target": f"{min(100, metrics.get('financial_health_score', 0) + 10)}/100",
                "timeline": "Next 6 months"
            }
        ]
    
    @staticmethod
    def _estimate_income_percentile(income: float, age: int) -> str:
        """Rough estimation of income percentile"""
        # Simplified estimation - would need actual survey data for accuracy
        if income > 200000:
            return "Top 10% for your age group"
        elif income > 100000:
            return "Top 25% for your age group"
        elif income > 50000:
            return "Above median for your age group"
        else:
            return "Below median for your age group"
    
    @staticmethod
    def _identify_improvement_areas(performance: Dict[str, Any], benchmark: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement based on benchmarks"""
        improvements = []
        
        if performance["savings_rate"]["status"] == "Below":
            improvements.append("Increase savings rate through expense optimization")
        
        if performance["emergency_fund"]["status"] == "Insufficient":
            improvements.append("Build emergency fund to recommended level")
        
        return improvements if improvements else ["Maintain current good financial habits"]