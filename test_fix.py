#!/usr/bin/env python3

from backend.models.user_profile import UserProfile
from backend.models.user_profile import RiskTolerance, TimeHorizon

def test_user_profile_with_emergency_fund():
    """Test creating a UserProfile with emergency_fund field"""
    try:
        profile = UserProfile(
            salary=50000,
            loans='No',
            expenses=25000,
            age=30,
            risk_tolerance=RiskTolerance.MODERATE,
            time_horizon=TimeHorizon.LONG,
            goals='Retirement planning',
            emergency_fund=100000
        )
        
        print(f'✅ UserProfile created successfully')
        print(f'Emergency fund: {profile.emergency_fund}')
        print(f'All fields: {profile.dict()}')
        return True
        
    except Exception as e:
        print(f'❌ Error creating UserProfile: {e}')
        return False

if __name__ == "__main__":
    print("Testing UserProfile with emergency_fund field...")
    success = test_user_profile_with_emergency_fund()
    
    if success:
        print("\n✅ Fix appears to be working correctly!")
    else:
        print("\n❌ Fix needs more work")