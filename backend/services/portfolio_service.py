from sqlalchemy.orm import Session
from backend.database.models import Portfolio, FinancialProfile, User
from backend.services.auth_service import AuthService
from typing import List, Dict, Any, Optional
import streamlit as st
from datetime import datetime
import json

class PortfolioService:
    @staticmethod
    def save_financial_profile(db: Session, profile_data: Dict[str, Any]) -> Optional[FinancialProfile]:
        """Save or update user's financial profile"""
        try:
            current_user = AuthService.get_current_user()
            if not current_user:
                return None
            
            user_id = current_user['id']
            
            # Check if profile exists
            existing_profile = db.query(FinancialProfile).filter(
                FinancialProfile.user_id == user_id
            ).order_by(FinancialProfile.created_at.desc()).first()
            
            # Create new profile
            financial_profile = FinancialProfile(
                user_id=user_id,
                salary=profile_data.get('salary', 0),
                expenses=profile_data.get('expenses', 0),
                emergency_fund=profile_data.get('emergency_fund', 0),
                emergency_months=profile_data.get('emergency_months', 6),
                age=profile_data.get('age', 25),
                risk_tolerance=profile_data.get('risk_tolerance', 'Moderate'),
                time_horizon=profile_data.get('time_horizon', '5-10 years'),
                existing_investments=profile_data.get('existing_investments', ''),
                goals=profile_data.get('goals', ''),
                loans=profile_data.get('loans', [])
            )
            
            db.add(financial_profile)
            db.commit()
            db.refresh(financial_profile)
            return financial_profile
            
        except Exception as e:
            db.rollback()
            st.error(f"Error saving financial profile: {str(e)}")
            return None
    
    @staticmethod
    def save_portfolio(db: Session, financial_profile_id: int, allocations: Dict[str, float], 
                      metrics: Dict[str, Any], ai_narrative: str, ai_recommendations: str, 
                      risk_level: str) -> Optional[Portfolio]:
        """Save portfolio recommendation"""
        try:
            current_user = AuthService.get_current_user()
            if not current_user:
                return None
            
            user_id = current_user['id']
            
            # Deactivate previous portfolios for this profile
            db.query(Portfolio).filter(
                Portfolio.user_id == user_id,
                Portfolio.financial_profile_id == financial_profile_id,
                Portfolio.is_active == True
            ).update({Portfolio.is_active: False})
            
            # Create new portfolio
            portfolio = Portfolio(
                user_id=user_id,
                financial_profile_id=financial_profile_id,
                allocations=allocations,
                metrics=metrics,
                ai_narrative=ai_narrative,
                ai_recommendations=ai_recommendations,
                risk_level=risk_level
            )
            
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            return portfolio
            
        except Exception as e:
            db.rollback()
            st.error(f"Error saving portfolio: {str(e)}")
            return None
    
    @staticmethod
    def get_user_portfolios(db: Session, limit: int = 10) -> List[Portfolio]:
        """Get user's portfolio history"""
        try:
            current_user = AuthService.get_current_user()
            if not current_user:
                return []
            
            user_id = current_user['id']
            
            portfolios = db.query(Portfolio).filter(
                Portfolio.user_id == user_id
            ).order_by(Portfolio.created_at.desc()).limit(limit).all()
            
            return portfolios
            
        except Exception as e:
            st.error(f"Error fetching portfolios: {str(e)}")
            return []
    
    @staticmethod
    def get_latest_financial_profile(db: Session) -> Optional[FinancialProfile]:
        """Get user's latest financial profile"""
        try:
            current_user = AuthService.get_current_user()
            if not current_user:
                return None
            
            user_id = current_user['id']
            
            profile = db.query(FinancialProfile).filter(
                FinancialProfile.user_id == user_id
            ).order_by(FinancialProfile.created_at.desc()).first()
            
            return profile
            
        except Exception as e:
            st.error(f"Error fetching financial profile: {str(e)}")
            return None
    
    @staticmethod
    def get_portfolio_comparison(db: Session, portfolio_ids: List[int]) -> List[Dict[str, Any]]:
        """Compare multiple portfolios"""
        try:
            current_user = AuthService.get_current_user()
            if not current_user:
                return []
            
            user_id = current_user['id']
            
            portfolios = db.query(Portfolio).filter(
                Portfolio.user_id == user_id,
                Portfolio.id.in_(portfolio_ids)
            ).all()
            
            comparison_data = []
            for portfolio in portfolios:
                comparison_data.append({
                    'id': portfolio.id,
                    'created_at': portfolio.created_at,
                    'allocations': portfolio.allocations,
                    'metrics': portfolio.metrics,
                    'risk_level': portfolio.risk_level
                })
            
            return comparison_data
            
        except Exception as e:
            st.error(f"Error comparing portfolios: {str(e)}")
            return []
    
    @staticmethod
    def delete_portfolio(db: Session, portfolio_id: int) -> bool:
        """Delete a portfolio"""
        try:
            current_user = AuthService.get_current_user()
            if not current_user:
                return False
            
            user_id = current_user['id']
            
            portfolio = db.query(Portfolio).filter(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id
            ).first()
            
            if portfolio:
                db.delete(portfolio)
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            st.error(f"Error deleting portfolio: {str(e)}")
            return False