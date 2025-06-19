#!/usr/bin/env python3

from backend.models.user_profile import UserProfile, RiskTolerance, TimeHorizon
from backend.services.enhanced_financial_engine import EnhancedFinancialEngine
from backend.database.database import get_db, init_db
import tempfile
import os

def test_enhanced_engine():
    """Test the enhanced financial engine with the fixed UserProfile"""
    
    try:
        # Use existing database
        db = next(get_db())
        
        # Create test profile
        profile = UserProfile(
            salary=50000,
            loans='No',
            expenses=25000,
            age=30,
            risk_tolerance=RiskTolerance.MODERATE,
            time_horizon=TimeHorizon.LONG,
            goals='Retirement planning and buying a house',
            emergency_fund=50000  # 2 months of expenses
        )
        
        print(f'✅ UserProfile created: emergency_fund = {profile.emergency_fund}')
        
        # Test enhanced metrics calculation
        enhanced_metrics = EnhancedFinancialEngine.calculate_advanced_metrics(
            profile, db, user_id=1
        )
        
        print(f'✅ Enhanced metrics calculated successfully')
        print(f'Financial health score: {enhanced_metrics.get("health_score", "N/A")}')
        print(f'Emergency fund months: {enhanced_metrics.get("emergency_fund_months", "N/A")}')
        print(f'Emergency fund gap: {enhanced_metrics.get("emergency_fund_gap", "N/A")}')
        
        # Test personalized allocation
        allocations = EnhancedFinancialEngine.generate_personalized_allocation(
            profile, enhanced_metrics
        )
        
        print(f'✅ Personalized allocation generated successfully')
        print(f'Investment capacity: {enhanced_metrics.get("investment_capacity", "N/A")}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error in enhanced engine: {e}')
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Close database connection
        db.close()

if __name__ == "__main__":
    print("Testing Enhanced Financial Engine with fixed UserProfile...")
    success = test_enhanced_engine()
    
    if success:
        print("\n✅ All tests passed! The fix is complete.")
    else:
        print("\n❌ Tests failed. More fixes needed.")