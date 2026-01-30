"""
溢价率计算器 API
"""
import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, Any
from datetime import datetime, timedelta

from app.database import get_db, SpreadData, RatioData, ExchangeRate
from app.config import PREMIUM_PAIRS
from app.calculator.premium_calculator import calculate_current_premiums

router = APIRouter()


def clean_float(value: Any) -> Any:
    """清理无效的浮点数值（NaN, Infinity）"""
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


def clean_dict(d: dict) -> dict:
    """递归清理字典中的无效浮点数"""
    if not isinstance(d, dict):
        return d
    
    cleaned = {}
    for key, value in d.items():
        if isinstance(value, dict):
            cleaned[key] = clean_dict(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_dict(v) if isinstance(v, dict) else clean_float(v) for v in value]
        else:
            cleaned[key] = clean_float(value)
    return cleaned


def get_signal(value: float, thresholds: dict) -> str:
    """根据阈值判断信号"""
    if value > thresholds.get("high", float('inf')):
        return "high"
    elif value < thresholds.get("low", float('-inf')):
        return "low"
    return "normal"


@router.get("/calculator")
def get_calculator_data(db: Session = Depends(get_db)):
    """
    获取溢价率计算器的完整数据
    返回实时计算的溢价率、比值指标和信号
    """
    # 实时计算当前数据
    result = calculate_current_premiums(db)
    
    if not result:
        return {
            "timestamp": datetime.now().isoformat(),
            "message": "暂无足够数据进行计算",
            "data": None
        }
    
    # 添加信号判断
    signals = {}
    
    # 黄金溢价率信号
    if result.get("gold") and result["gold"].get("premium_rate") is not None:
        gold_premium = result["gold"]["premium_rate"]
        if gold_premium > 2:
            signals["gold_premium"] = "high"
            signals["gold_premium_message"] = "国内抢金，恐慌情绪浓厚"
        elif gold_premium < -2:
            signals["gold_premium"] = "low"
            signals["gold_premium_message"] = "国内金价偏低，可能有机会"
        else:
            signals["gold_premium"] = "normal"
            signals["gold_premium_message"] = "溢价率正常"
    
    # 铜溢价率信号
    if result.get("copper") and result["copper"].get("premium_rate") is not None:
        copper_premium = result["copper"]["premium_rate"]
        if copper_premium < -5:
            signals["copper_premium"] = "low"
            signals["copper_premium_message"] = "国内铜便宜，做多机会"
        elif copper_premium > 5:
            signals["copper_premium"] = "high"
            signals["copper_premium_message"] = "国内铜溢价过高"
        else:
            signals["copper_premium"] = "normal"
            signals["copper_premium_message"] = "溢价率正常"
    
    # 金银比信号
    if result.get("ratios") and result["ratios"].get("gold_silver") is not None:
        gs_ratio = result["ratios"]["gold_silver"]
        if gs_ratio > 80:
            signals["gold_silver_ratio"] = "high_alert"
            signals["gold_silver_message"] = "避险情绪高涨，白银被低估"
        elif gs_ratio < 60:
            signals["gold_silver_ratio"] = "low_alert"
            signals["gold_silver_message"] = "白银可能被高估"
        else:
            signals["gold_silver_ratio"] = "normal"
            signals["gold_silver_message"] = "金银比正常"
    
    # 铜金比（经济温度计）
    if result.get("ratios") and result["ratios"].get("copper_gold") is not None:
        signals["economic_sentiment"] = "neutral"
        signals["economic_message"] = "需要结合趋势判断"
    
    result["signals"] = signals
    
    # 清理无效浮点数，防止 JSON 序列化错误
    return clean_dict(result)


@router.get("/calculator/history")
def get_premium_history(
    pair: str = Query("GOLD", description="品种对: GOLD, SILVER, COPPER, ALUMINUM"),
    days: int = Query(30, description="天数"),
    db: Session = Depends(get_db)
):
    """
    获取溢价率历史数据
    """
    start_date = datetime.now() - timedelta(days=days)
    
    records = db.query(SpreadData).filter(
        SpreadData.pair == pair,
        SpreadData.timestamp >= start_date
    ).order_by(SpreadData.timestamp).all()
    
    data = []
    for r in records:
        data.append({
            "timestamp": r.timestamp.isoformat(),
            "domestic_price": r.domestic_price,
            "foreign_price": r.foreign_price,
            "theoretical_price": r.theoretical_price,
            "spread_rate": r.spread_rate,
            "exchange_rate": r.exchange_rate,
        })
    
    pair_config = PREMIUM_PAIRS.get(pair, {})
    
    return clean_dict({
        "pair": pair,
        "name": pair_config.get("name", pair),
        "period": f"{days}天",
        "count": len(data),
        "data": data
    })


@router.get("/calculator/ratios")
def get_ratio_history(
    ratio_type: str = Query("GOLD_SILVER", description="比值类型: GOLD_SILVER, COPPER_GOLD"),
    days: int = Query(30, description="天数"),
    db: Session = Depends(get_db)
):
    """
    获取比值指标历史数据
    """
    start_date = datetime.now() - timedelta(days=days)
    
    records = db.query(RatioData).filter(
        RatioData.ratio_type == ratio_type,
        RatioData.timestamp >= start_date
    ).order_by(RatioData.timestamp).all()
    
    data = []
    for r in records:
        data.append({
            "timestamp": r.timestamp.isoformat(),
            "value": r.value,
        })
    
    name_map = {
        "GOLD_SILVER": "金银比",
        "COPPER_GOLD": "铜金比"
    }
    
    return clean_dict({
        "ratio_type": ratio_type,
        "name": name_map.get(ratio_type, ratio_type),
        "period": f"{days}天",
        "count": len(data),
        "data": data
    })
