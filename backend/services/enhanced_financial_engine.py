from backend.models.user_profile import UserProfile, RiskTolerance, TimeHorizon
from backend.database.models import FinancialProfile, Portfolio
from backend.services.market_service import MarketService
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import streamlit as st
import json
import numpy as np
from backend.utils.formatters import format_currency, format_percentage, format_number

class EnhancedFinancialEngine:
    
    @staticmethod
    def calculate_advanced_metrics(profile: UserProfile, db: Session, user_id: int) -> Dict[str, Any]:
        """Calculate comprehensive financial metrics with historical context"""
        
        # Basic calculations
        disposable_income = max(0, profile.salary - profile.expenses)
        
        # Get historical data for comparison
        historical_profiles = db.query(FinancialProfile).filter(
            FinancialProfile.user_id == user_id
        ).order_by(FinancialProfile.created_at.desc()).limit(5).all()
        
        # Calculate trends
        income_trend = EnhancedFinancialEngine._calculate_income_trend(historical_profiles, profile.salary)
        expense_trend = EnhancedFinancialEngine._calculate_expense_trend(historical_profiles, profile.expenses)
        
        # Lifecycle-based recommendations
        lifecycle_stage = EnhancedFinancialEngine._determine_lifecycle_stage(profile.age, profile.salary)
        
        # Goal-based allocation
        goal_analysis = EnhancedFinancialEngine._analyze_goals(profile.goals, profile.age, disposable_income)
        
        # Emergency fund analysis
        emergency_fund_months = profile.emergency_fund / profile.expenses if profile.expenses > 0 else 0
        emergency_fund_gap = max(0, (6 * profile.expenses) - profile.emergency_fund)
        
        # Investment capacity with lifestyle allocation
        lifestyle_allocation = 0
        if profile.age <= 30 and disposable_income > 10000:
            lifestyle_allocation = min(disposable_income * 0.2, 5000)
        
        investment_capacity = disposable_income - lifestyle_allocation
        
        # Risk-adjusted capacity
        risk_multiplier = {
            RiskTolerance.CONSERVATIVE: 0.7,
            RiskTolerance.MODERATE: 1.0,
            RiskTolerance.AGGRESSIVE: 1.3
        }.get(profile.risk_tolerance, 1.0)
        
        # Time horizon impact
        time_multiplier = {
            TimeHorizon.SHORT: 0.6,
            TimeHorizon.MEDIUM: 0.9,
            TimeHorizon.LONG: 1.1,
            TimeHorizon.VERY_LONG: 1.3
        }.get(profile.time_horizon, 1.0)
        
        adjusted_capacity = investment_capacity * risk_multiplier * time_multiplier
        
        # Calculate financial health score (0-100)
        financial_health_score = EnhancedFinancialEngine._calculate_financial_health_score(
            profile, emergency_fund_months, disposable_income
        )
        
        # Tax efficiency suggestions
        tax_suggestions = EnhancedFinancialEngine._generate_tax_suggestions(
            profile, investment_capacity
        )
        
        # Inflation-adjusted projections
        projections = EnhancedFinancialEngine._calculate_projections(
            investment_capacity, profile.age, profile.time_horizon
        )
        
        return {
            # Basic metrics
            "salary": profile.salary,
            "expenses": profile.expenses,
            "disposable_income": disposable_income,
            "investment_capacity": investment_capacity,
            "lifestyle_allocation": lifestyle_allocation,
            "adjusted_investment_capacity": adjusted_capacity,
            
            # Emergency fund analysis
            "emergency_fund_current": profile.emergency_fund,
            "emergency_fund_months": round(emergency_fund_months, 1),
            "emergency_fund_target": 6 * profile.expenses,
            "emergency_fund_gap": emergency_fund_gap,
            
            # Advanced metrics
            "financial_health_score": financial_health_score,
            "lifecycle_stage": lifecycle_stage,
            "income_trend": income_trend,
            "expense_trend": expense_trend,
            
            # Goal analysis
            "goal_analysis": goal_analysis,
            "tax_suggestions": tax_suggestions,
            "projections": projections,
            
            # Risk metrics
            "risk_score": EnhancedFinancialEngine._calculate_risk_score(profile),
            "risk_capacity": EnhancedFinancialEngine._assess_risk_capacity(profile, disposable_income),
            
            # Ratios
            "savings_rate": (disposable_income / profile.salary * 100) if profile.salary > 0 else 0,
            "expense_ratio": (profile.expenses / profile.salary * 100) if profile.salary > 0 else 0,
            "debt_to_income": EnhancedFinancialEngine._calculate_debt_ratio(profile.loans),
            
            # Timestamps
            "analysis_date": datetime.now().isoformat(),
            "user_age": profile.age,
            "time_horizon": profile.time_horizon,
            "risk_tolerance": profile.risk_tolerance
        }
    
    @staticmethod
    def _calculate_income_trend(historical_profiles: List[FinancialProfile], current_salary: float) -> Dict[str, Any]:
        """Calculate income trend from historical data"""
        if len(historical_profiles) < 2:
            return {"trend": "insufficient_data", "change_percent": 0, "recommendation": "Continue tracking"}
        
        # Get salary progression
        salaries = [p.salary for p in reversed(historical_profiles)]
        salaries.append(current_salary)
        
        # Calculate trend
        if len(salaries) >= 2:
            recent_change = ((salaries[-1] - salaries[-2]) / salaries[-2]) * 100
            
            if recent_change > 10:
                trend = "strong_growth"
                recommendation = "Consider increasing investment allocation due to income growth"
            elif recent_change > 0:
                trend = "moderate_growth"
                recommendation = "Maintain current investment strategy with slight increase"
            elif recent_change > -5:
                trend = "stable"
                recommendation = "Focus on consistency and expense optimization"
            else:
                trend = "declining"
                recommendation = "Consider expense reduction and emergency fund priority"
            
            return {
                "trend": trend,
                "change_percent": round(recent_change, 1),
                "recommendation": recommendation,
                "historical_salaries": salaries[-3:] if len(salaries) >= 3 else salaries
            }
        
        return {"trend": "insufficient_data", "change_percent": 0, "recommendation": "Continue tracking"}
    
    @staticmethod
    def _calculate_expense_trend(historical_profiles: List[FinancialProfile], current_expenses: float) -> Dict[str, Any]:
        """Calculate expense trend from historical data"""
        if len(historical_profiles) < 2:
            return {"trend": "insufficient_data", "change_percent": 0}
        
        expenses = [p.expenses for p in reversed(historical_profiles)]
        expenses.append(current_expenses)
        
        if len(expenses) >= 2:
            recent_change = ((expenses[-1] - expenses[-2]) / expenses[-2]) * 100
            
            if recent_change > 15:
                trend = "increasing_rapidly"
                alert = "Consider expense review and budgeting"
            elif recent_change > 5:
                trend = "increasing"
                alert = "Monitor expense growth"
            elif recent_change > -5:
                trend = "stable"
                alert = "Expenses under control"
            else:
                trend = "decreasing"
                alert = "Good expense management"
            
            return {
                "trend": trend,
                "change_percent": round(recent_change, 1),
                "alert": alert,
                "historical_expenses": expenses[-3:] if len(expenses) >= 3 else expenses
            }
        
        return {"trend": "insufficient_data", "change_percent": 0}
    
    @staticmethod
    def _determine_lifecycle_stage(age: int, salary: float) -> Dict[str, Any]:
        """Determine user's financial lifecycle stage"""
        if age < 25:
            stage = "early_career"
            focus = ["Emergency fund building", "Skill development", "Basic investing"]
            risk_capacity = "High"
        elif age < 35:
            stage = "wealth_building"
            focus = ["Aggressive investing", "Career advancement", "Major purchases"]
            risk_capacity = "High to Moderate"
        elif age < 45:
            stage = "wealth_accumulation"
            focus = ["Diversified portfolio", "Education planning", "Insurance review"]
            risk_capacity = "Moderate"
        elif age < 55:
            stage = "pre_retirement"
            focus = ["Retirement planning", "Risk reduction", "Estate planning"]
            risk_capacity = "Moderate to Low"
        else:
            stage = "retirement_planning"
            focus = ["Capital preservation", "Income generation", "Legacy planning"]
            risk_capacity = "Low"
        
        return {
            "stage": stage,
            "focus_areas": focus,
            "risk_capacity": risk_capacity,
            "recommended_equity_allocation": max(20, 100 - age)
        }
    
    @staticmethod
    def _analyze_goals(goals: str, age: int, disposable_income: float) -> Dict[str, Any]:
        """Analyze financial goals and provide timeline-based recommendations"""
        goals_lower = goals.lower() if goals else ""
        
        detected_goals = []
        recommendations = []
        
        # Goal detection patterns
        goal_patterns = {
            "retirement": ["retirement", "retire", "pension"],
            "home": ["home", "house", "property", "real estate"],
            "education": ["education", "study", "college", "university", "school"],
            "travel": ["travel", "trip", "vacation", "holiday"],
            "emergency": ["emergency", "fund", "safety"],
            "business": ["business", "startup", "entrepreneur"],
            "marriage": ["marriage", "wedding", "family"],
            "children": ["children", "kids", "child"]
        }
        
        for goal_type, keywords in goal_patterns.items():
            if any(keyword in goals_lower for keyword in keywords):
                detected_goals.append(goal_type)
        
        # Generate goal-specific recommendations
        for goal in detected_goals:
            if goal == "retirement":
                years_to_retirement = max(5, 60 - age)
                monthly_needed = EnhancedFinancialEngine._calculate_retirement_need(disposable_income, years_to_retirement)
                recommendations.append({
                    "goal": "Retirement Planning",
                    "timeline": f"{years_to_retirement} years",
                    "monthly_investment": monthly_needed,
                    "strategy": "Balanced growth portfolio with gradual shift to conservative"
                })
            
            elif goal == "home":
                home_timeline = 5 if age < 35 else 3
                recommendations.append({
                    "goal": "Home Purchase",
                    "timeline": f"{home_timeline} years",
                    "monthly_investment": disposable_income * 0.3,
                    "strategy": "Conservative growth with liquid funds"
                })
            
            elif goal == "education":
                edu_timeline = 10 if "children" in detected_goals else 2
                recommendations.append({
                    "goal": "Education Fund",
                    "timeline": f"{edu_timeline} years",
                    "monthly_investment": disposable_income * 0.25,
                    "strategy": "Moderate growth with education-specific funds"
                })
        
        return {
            "detected_goals": detected_goals,
            "recommendations": recommendations,
            "priority_goal": detected_goals[0] if detected_goals else "wealth_building"
        }
    
    @staticmethod
    def _calculate_retirement_need(monthly_income: float, years_to_retirement: int) -> float:
        """Calculate monthly investment needed for retirement"""
        # Assume 70% of current income needed in retirement
        retirement_income_need = monthly_income * 0.7
        # Assume 25x annual expenses rule
        corpus_needed = retirement_income_need * 12 * 25
        
        # Calculate monthly SIP needed (assuming 12% annual return)
        if years_to_retirement > 0:
            annual_return = 0.12
            months = years_to_retirement * 12
            monthly_return = annual_return / 12
            
            # SIP formula: FV = PMT * (((1 + r)^n - 1) / r)
            monthly_sip = corpus_needed / (((1 + monthly_return) ** months - 1) / monthly_return)
            return round(monthly_sip, 0)
        
        return 0
    
    @staticmethod
    def _calculate_financial_health_score(profile: UserProfile, emergency_months: float, disposable_income: float) -> int:
        """Calculate comprehensive financial health score (0-100)"""
        score = 0
        
        # Emergency fund (25 points)
        if emergency_months >= 6:
            score += 25
        elif emergency_months >= 3:
            score += 15
        elif emergency_months >= 1:
            score += 8
        
        # Savings rate (30 points)
        savings_rate = (disposable_income / profile.salary * 100) if profile.salary > 0 else 0
        if savings_rate >= 30:
            score += 30
        elif savings_rate >= 20:
            score += 25
        elif savings_rate >= 10:
            score += 15
        elif savings_rate >= 5:
            score += 8
        
        # Debt management (20 points)
        has_loans = "yes" in profile.loans.lower() if profile.loans else False
        if not has_loans:
            score += 20
        else:
            score += 10  # Partial credit for managing debt
        
        # Age-appropriate risk taking (15 points)
        age_appropriate_risk = EnhancedFinancialEngine._is_age_appropriate_risk(profile.age, profile.risk_tolerance)
        if age_appropriate_risk:
            score += 15
        else:
            score += 8
        
        # Goal clarity (10 points)
        if profile.goals and len(profile.goals.strip()) > 20:
            score += 10
        elif profile.goals and len(profile.goals.strip()) > 5:
            score += 5
        
        return min(100, score)
    
    @staticmethod
    def _is_age_appropriate_risk(age: int, risk_tolerance: RiskTolerance) -> bool:
        """Check if risk tolerance is appropriate for age"""
        if age < 30:
            return risk_tolerance in [RiskTolerance.MODERATE, RiskTolerance.AGGRESSIVE]
        elif age < 50:
            return risk_tolerance in [RiskTolerance.MODERATE, RiskTolerance.CONSERVATIVE]
        else:
            return risk_tolerance == RiskTolerance.CONSERVATIVE
    
    @staticmethod
    def _generate_tax_suggestions(profile: UserProfile, investment_capacity: float) -> List[Dict[str, str]]:
        """Generate tax optimization suggestions"""
        suggestions = []
        
        annual_investment = investment_capacity * 12
        
        # ELSS suggestions
        if annual_investment >= 50000:
            suggestions.append({
                "type": "ELSS Investment",
                "description": "Invest ₹1.5L in ELSS funds for 80C tax benefits",
                "tax_benefit": "Up to ₹46,800 tax savings",
                "allocation": "15-20% of equity allocation"
            })
        
        # PPF suggestions
        if profile.age < 45:
            suggestions.append({
                "type": "PPF Investment",
                "description": "Maximum ₹1.5L annual PPF investment",
                "tax_benefit": "Triple tax benefit (EEE status)",
                "allocation": "5-10% of total investment"
            })
        
        # NPS suggestions
        if profile.age < 50:
            suggestions.append({
                "type": "NPS Investment",
                "description": "Additional ₹50K in NPS for extra 80CCD(1B) benefit",
                "tax_benefit": "Additional ₹15,600 tax savings",
                "allocation": "10-15% for retirement corpus"
            })
        
        return suggestions
    
    @staticmethod
    def _calculate_projections(investment_capacity: float, age: int, time_horizon: TimeHorizon) -> Dict[str, Any]:
        """Calculate inflation-adjusted future value projections"""
        
        # Time horizon mapping
        years_map = {
            TimeHorizon.SHORT: 3,
            TimeHorizon.MEDIUM: 5,
            TimeHorizon.LONG: 10,
            TimeHorizon.VERY_LONG: 20
        }
        
        years = years_map.get(time_horizon, 10)
        monthly_investment = investment_capacity
        
        # Different return scenarios
        scenarios = {
            "conservative": 0.08,  # 8% annual return
            "moderate": 0.12,      # 12% annual return
            "aggressive": 0.15     # 15% annual return
        }
        
        projections = {}
        inflation_rate = 0.06  # 6% inflation
        
        for scenario, annual_return in scenarios.items():
            monthly_return = annual_return / 12
            months = years * 12
            
            # Future value calculation
            if monthly_return > 0:
                fv = monthly_investment * (((1 + monthly_return) ** months - 1) / monthly_return)
            else:
                fv = monthly_investment * months
            
            # Inflation-adjusted value
            real_value = fv / ((1 + inflation_rate) ** years)
            
            projections[scenario] = {
                "nominal_value": round(fv, 0),
                "real_value": round(real_value, 0),
                "total_invested": round(monthly_investment * months, 0),
                "gains": round(fv - (monthly_investment * months), 0)
            }
        
        return {
            "time_horizon_years": years,
            "monthly_investment": monthly_investment,
            "scenarios": projections,
            "inflation_assumed": "6% annually"
        }
    
    @staticmethod
    def _calculate_risk_score(profile: UserProfile) -> float:
        """Calculate comprehensive risk score"""
        base_score = {
            RiskTolerance.CONSERVATIVE: 2.0,
            RiskTolerance.MODERATE: 5.0,
            RiskTolerance.AGGRESSIVE: 8.0
        }.get(profile.risk_tolerance, 5.0)
        
        # Age adjustment
        age_factor = max(0.3, (80 - profile.age) / 80)
        
        # Time horizon adjustment
        time_factor = {
            TimeHorizon.SHORT: 0.5,
            TimeHorizon.MEDIUM: 0.8,
            TimeHorizon.LONG: 1.2,
            TimeHorizon.VERY_LONG: 1.5
        }.get(profile.time_horizon, 1.0)
        
        return round(base_score * age_factor * time_factor, 1)
    
    @staticmethod
    def _assess_risk_capacity(profile: UserProfile, disposable_income: float) -> str:
        """Assess user's financial capacity to take risks"""
        
        # Income stability (higher income = higher capacity)
        income_factor = "High" if profile.salary > 100000 else "Medium" if profile.salary > 50000 else "Low"
        
        # Age factor
        age_factor = "High" if profile.age < 35 else "Medium" if profile.age < 50 else "Low"
        
        # Expense ratio
        expense_ratio = profile.expenses / profile.salary if profile.salary > 0 else 1
        expense_factor = "High" if expense_ratio < 0.6 else "Medium" if expense_ratio < 0.8 else "Low"
        
        # Overall assessment
        factors = [income_factor, age_factor, expense_factor]
        high_count = factors.count("High")
        medium_count = factors.count("Medium")
        
        if high_count >= 2:
            return "High - Can take significant investment risks"
        elif high_count + medium_count >= 2:
            return "Medium - Moderate risk capacity"
        else:
            return "Low - Should focus on capital preservation"
    
    @staticmethod
    def _calculate_debt_ratio(loans: str) -> float:
        """Extract and calculate debt-to-income ratio from loans string"""
        # This is a simplified implementation
        # In practice, you'd parse the loan details more thoroughly
        if not loans or "no" in loans.lower():
            return 0.0
        
        # Placeholder - would need more sophisticated parsing
        return 0.3  # Assume 30% if loans exist
    
    @staticmethod
    def generate_personalized_allocation(profile: UserProfile, metrics: Dict[str, Any], 
                                      market_data: Dict[str, Any] = None) -> Dict[str, float]:
        """Generate personalized asset allocation based on comprehensive analysis"""
        
        age = profile.age
        risk_score = metrics.get('risk_score', 5.0)
        financial_health = metrics.get('financial_health_score', 50)
        lifecycle_stage = metrics.get('lifecycle_stage', {})
        
        # Base allocation using Rule of 100, adjusted for modern longevity
        base_equity_percent = min(90, max(20, 110 - age))
        
        # Risk tolerance adjustment
        risk_adjustment = {
            RiskTolerance.CONSERVATIVE: -15,
            RiskTolerance.MODERATE: 0,
            RiskTolerance.AGGRESSIVE: +15
        }.get(profile.risk_tolerance, 0)
        
        # Time horizon adjustment
        time_adjustment = {
            TimeHorizon.SHORT: -20,
            TimeHorizon.MEDIUM: -10,
            TimeHorizon.LONG: +5,
            TimeHorizon.VERY_LONG: +10
        }.get(profile.time_horizon, 0)
        
        # Financial health adjustment
        health_adjustment = 0
        if financial_health >= 80:
            health_adjustment = +10
        elif financial_health < 50:
            health_adjustment = -10
        
        # Calculate final equity percentage
        equity_percent = max(10, min(85, base_equity_percent + risk_adjustment + time_adjustment + health_adjustment))
        
        # Distribute equity allocation
        if equity_percent >= 60:
            # Aggressive allocation
            allocation = {
                "Large Cap Stocks": max(25, equity_percent * 0.4),
                "Mid Cap Stocks": max(15, equity_percent * 0.25),
                "Small Cap Stocks": max(10, equity_percent * 0.15),
                "International Stocks": max(10, equity_percent * 0.2),
                "Government Bonds": max(10, (100 - equity_percent) * 0.6),
                "Corporate Bonds": max(5, (100 - equity_percent) * 0.3),
                "Gold/Commodities": 5,
                "Cash/FD": max(5, (100 - equity_percent) * 0.1)
            }
        elif equity_percent >= 40:
            # Moderate allocation
            allocation = {
                "Large Cap Stocks": max(20, equity_percent * 0.5),
                "Mid Cap Stocks": max(10, equity_percent * 0.3),
                "International Stocks": max(10, equity_percent * 0.2),
                "Government Bonds": max(15, (100 - equity_percent) * 0.5),
                "Corporate Bonds": max(10, (100 - equity_percent) * 0.3),
                "Gold/Commodities": 10,
                "Cash/FD": max(10, (100 - equity_percent) * 0.2)
            }
        else:
            # Conservative allocation
            allocation = {
                "Large Cap Stocks": max(15, equity_percent * 0.6),
                "Mid Cap Stocks": max(5, equity_percent * 0.4),
                "Government Bonds": max(25, (100 - equity_percent) * 0.4),
                "Corporate Bonds": max(20, (100 - equity_percent) * 0.3),
                "Gold/Commodities": 15,
                "Cash/FD": max(15, (100 - equity_percent) * 0.3)
            }
        
        # Normalize to 100%
        total = sum(allocation.values())
        allocation = {k: round(v * 100 / total, 1) for k, v in allocation.items()}
        
        return allocation