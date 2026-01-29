"""
实时数据快照 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from app.database import get_db, RealtimePrice
from app.config import SYMBOLS_CONFIG

router = APIRouter()


@router.get("/snapshot")
def get_snapshot(
    market: Optional[str] = Query(None, description="市场筛选: CN, INTL, LME"),
    db: Session = Depends(get_db)
):
    """
    获取所有品种的最新价格快照
    """
    # 获取每个品种的最新价格
    latest_prices = {}
    
    for symbol, config in SYMBOLS_CONFIG.items():
        if market and config.get("market") != market:
            continue
            
        price = db.query(RealtimePrice).filter(
            RealtimePrice.symbol == symbol
        ).order_by(desc(RealtimePrice.timestamp)).first()
        
        if price:
            latest_prices[symbol] = {
                "symbol": symbol,
                "name": config["name"],
                "price": price.price,
                "price_cny": price.price_cny,
                "unit": config["unit"],
                "market": config["market"],
                "timestamp": price.timestamp.isoformat() if price.timestamp else None,
            }
        else:
            # 没有数据时返回配置信息
            latest_prices[symbol] = {
                "symbol": symbol,
                "name": config["name"],
                "price": None,
                "price_cny": None,
                "unit": config["unit"],
                "market": config["market"],
                "timestamp": None,
            }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "data": latest_prices
    }


@router.get("/snapshot/{symbol}")
def get_symbol_snapshot(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    获取指定品种的最新价格
    """
    if symbol not in SYMBOLS_CONFIG:
        return {"error": f"未知品种: {symbol}"}
    
    config = SYMBOLS_CONFIG[symbol]
    price = db.query(RealtimePrice).filter(
        RealtimePrice.symbol == symbol
    ).order_by(desc(RealtimePrice.timestamp)).first()
    
    if price:
        return {
            "symbol": symbol,
            "name": config["name"],
            "price": price.price,
            "price_cny": price.price_cny,
            "unit": config["unit"],
            "market": config["market"],
            "timestamp": price.timestamp.isoformat() if price.timestamp else None,
        }
    else:
        return {
            "symbol": symbol,
            "name": config["name"],
            "price": None,
            "message": "暂无数据"
        }


@router.get("/symbols")
def get_symbols():
    """
    获取所有支持的品种列表
    """
    symbols_list = []
    for symbol, config in SYMBOLS_CONFIG.items():
        symbols_list.append({
            "symbol": symbol,
            "name": config["name"],
            "market": config["market"],
            "unit": config["unit"],
        })
    
    return {
        "count": len(symbols_list),
        "symbols": symbols_list
    }
