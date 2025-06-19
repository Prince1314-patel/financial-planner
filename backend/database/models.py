from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="owner")
    financial_profiles = relationship("FinancialProfile", back_populates="user")

class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic financial info
    salary = Column(Float, nullable=False)
    expenses = Column(Float, nullable=False)
    emergency_fund = Column(Float, default=0.0)
    emergency_months = Column(Integer, default=6)
    
    # Personal info
    age = Column(Integer, nullable=False)
    risk_tolerance = Column(String(20), nullable=False)  # Conservative, Moderate, Aggressive
    time_horizon = Column(String(20), nullable=False)    # <3 years, 3-5 years, etc.
    
    # Additional info
    existing_investments = Column(Text)
    goals = Column(Text)
    loans = Column(JSON)  # Store loan details as JSON
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="financial_profiles")
    portfolios = relationship("Portfolio", back_populates="financial_profile")

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    financial_profile_id = Column(Integer, ForeignKey("financial_profiles.id"), nullable=False)
    
    # Portfolio data
    allocations = Column(JSON, nullable=False)  # Asset allocation percentages
    metrics = Column(JSON, nullable=False)      # Calculated financial metrics
    ai_narrative = Column(Text)                 # AI explanation
    ai_recommendations = Column(Text)           # AI next steps
    risk_level = Column(String(20))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    owner = relationship("User", back_populates="portfolios")
    financial_profile = relationship("FinancialProfile", back_populates="portfolios")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_class = Column(String(50), nullable=False)  # stocks, bonds, commodities, etc.
    current_price = Column(Float)
    previous_close = Column(Float)
    change_percent = Column(Float)
    volume = Column(Integer)
    market_cap = Column(Float)
    
    # Additional data as JSON for flexibility
    additional_data = Column(JSON)
    
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'asset_class': self.asset_class,
            'current_price': self.current_price,
            'previous_close': self.previous_close,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'additional_data': self.additional_data,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }