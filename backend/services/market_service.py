import yfinance as yf
import requests
from sqlalchemy.orm import Session
from backend.database.models import MarketData
from typing import Dict, List, Optional, Any
import streamlit as st
from datetime import datetime, timedelta
import json

class MarketService:
    # Popular ETFs and indices for portfolio tracking
    DEFAULT_SYMBOLS = {
        'stocks': ['SPY', 'VTI', 'VXUS', 'VEA', 'VWO'],  # US & International stocks
        'bonds': ['BND', 'VGIT', 'VGLT', 'VTEB'],        # Bonds
        'commodities': ['GLD', 'SLV', 'VNQ'],            # Gold, Silver, REITs
        'crypto': ['BTC-USD', 'ETH-USD'],                # Major crypto
        'indian_etfs': ['INFY', 'TCS.NS', 'RELIANCE.NS'] # Indian stocks
    }
    
    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_market_data(symbols: List[str]) -> Dict[str, Any]:
        """Fetch current market data for given symbols"""
        try:
            market_data = {}
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="2d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                        change_percent = ((current_price - previous_close) / previous_close) * 100
                        
                        market_data[symbol] = {
                            'symbol': symbol,
                            'current_price': round(current_price, 2),
                            'previous_close': round(previous_close, 2),
                            'change_percent': round(change_percent, 2),
                            'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                            'market_cap': info.get('marketCap', 0),
                            'sector': info.get('sector', 'Unknown'),
                            'industry': info.get('industry', 'Unknown'),
                            'last_updated': datetime.now().isoformat()
                        }
                except Exception as e:
                    st.warning(f"Could not fetch data for {symbol}: {str(e)}")
                    continue
            
            return market_data
            
        except Exception as e:
            st.error(f"Error fetching market data: {str(e)}")
            return {}
    
    @staticmethod
    def save_market_data(db: Session, market_data: Dict[str, Any]):
        """Save market data to database"""
        try:
            for symbol, data in market_data.items():
                # Check if data exists for today
                existing = db.query(MarketData).filter(
                    MarketData.symbol == symbol,
                    MarketData.last_updated >= datetime.now().date()
                ).first()
                
                if existing:
                    # Update existing data
                    existing.current_price = data.get('current_price')
                    existing.previous_close = data.get('previous_close')
                    existing.change_percent = data.get('change_percent')
                    existing.volume = data.get('volume')
                    existing.market_cap = data.get('market_cap')
                    existing.additional_data = {
                        'sector': data.get('sector'),
                        'industry': data.get('industry')
                    }
                    existing.last_updated = datetime.now()
                else:
                    # Create new record
                    market_record = MarketData(
                        symbol=symbol,
                        asset_class=MarketService._classify_asset(symbol),
                        current_price=data.get('current_price'),
                        previous_close=data.get('previous_close'),
                        change_percent=data.get('change_percent'),
                        volume=data.get('volume'),
                        market_cap=data.get('market_cap'),
                        additional_data={
                            'sector': data.get('sector'),
                            'industry': data.get('industry')
                        }
                    )
                    db.add(market_record)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            st.error(f"Error saving market data: {str(e)}")
    
    @staticmethod
    def _classify_asset(symbol: str) -> str:
        """Classify asset type based on symbol"""
        if symbol in MarketService.DEFAULT_SYMBOLS['stocks']:
            return 'stocks'
        elif symbol in MarketService.DEFAULT_SYMBOLS['bonds']:
            return 'bonds'
        elif symbol in MarketService.DEFAULT_SYMBOLS['commodities']:
            return 'commodities'
        elif symbol in MarketService.DEFAULT_SYMBOLS['crypto']:
            return 'crypto'
        elif symbol in MarketService.DEFAULT_SYMBOLS['indian_etfs']:
            return 'indian_stocks'
        else:
            return 'unknown'
    
    @staticmethod
    def get_market_summary(db: Session) -> Dict[str, Any]:
        """Get market summary for dashboard"""
        try:
            # Get recent market data
            recent_data = db.query(MarketData).filter(
                MarketData.last_updated >= datetime.now() - timedelta(days=1)
            ).all()
            
            summary = {
                'total_symbols': len(recent_data),
                'by_asset_class': {},
                'top_gainers': [],
                'top_losers': [],
                'last_updated': datetime.now().isoformat()
            }
            
            # Group by asset class
            for data in recent_data:
                asset_class = data.asset_class
                if asset_class not in summary['by_asset_class']:
                    summary['by_asset_class'][asset_class] = {
                        'count': 0,
                        'avg_change': 0,
                        'total_change': 0
                    }
                
                summary['by_asset_class'][asset_class]['count'] += 1
                summary['by_asset_class'][asset_class]['total_change'] += data.change_percent or 0
            
            # Calculate averages
            for asset_class in summary['by_asset_class']:
                count = summary['by_asset_class'][asset_class]['count']
                total = summary['by_asset_class'][asset_class]['total_change']
                summary['by_asset_class'][asset_class]['avg_change'] = round(total / count, 2) if count > 0 else 0
            
            # Get top gainers and losers
            sorted_data = sorted(recent_data, key=lambda x: x.change_percent or 0, reverse=True)
            
            summary['top_gainers'] = [
                {
                    'symbol': d.symbol,
                    'change_percent': d.change_percent,
                    'current_price': d.current_price
                }
                for d in sorted_data[:5] if d.change_percent and d.change_percent > 0
            ]
            
            summary['top_losers'] = [
                {
                    'symbol': d.symbol,
                    'change_percent': d.change_percent,
                    'current_price': d.current_price
                }
                for d in sorted_data[-5:] if d.change_percent and d.change_percent < 0
            ]
            
            return summary
            
        except Exception as e:
            st.error(f"Error getting market summary: {str(e)}")
            return {}
    
    @staticmethod
    def get_asset_performance(db: Session, days: int = 30) -> Dict[str, Any]:
        """Get asset class performance over time"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            data = db.query(MarketData).filter(
                MarketData.last_updated >= cutoff_date
            ).all()
            
            performance = {}
            for record in data:
                asset_class = record.asset_class
                if asset_class not in performance:
                    performance[asset_class] = []
                
                performance[asset_class].append({
                    'date': record.last_updated.date().isoformat(),
                    'symbol': record.symbol,
                    'change_percent': record.change_percent or 0,
                    'price': record.current_price or 0
                })
            
            return performance
            
        except Exception as e:
            st.error(f"Error getting asset performance: {str(e)}")
            return {}