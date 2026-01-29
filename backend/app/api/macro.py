"""
宏观数据 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db, MacroData

router = APIRouter()


@router.get("/macro/cpi")
def get_cpi_data(
    country: str = Query("CN", description="国家: CN, US"),
    months: int = Query(24, description="月数"),
    db: Session = Depends(get_db)
):
    """
    获取 CPI 数据
    """
    indicator = f"CPI_{country}"
    
    records = db.query(MacroData).filter(
        MacroData.indicator == indicator
    ).order_by(desc(MacroData.date)).limit(months).all()
    
    # 反转为时间正序
    records = list(reversed(records))
    
    data = []
    for r in records:
        data.append({
            "date": r.date.strftime("%Y-%m"),
            "value": r.value,
            "yoy_change": r.yoy_change,
            "mom_change": r.mom_change,
        })
    
    country_names = {"CN": "中国", "US": "美国"}
    
    return {
        "country": country,
        "country_name": country_names.get(country, country),
        "indicator": "CPI",
        "count": len(data),
        "data": data
    }


@router.get("/macro/cpi/compare")
def get_cpi_compare(
    months: int = Query(24, description="月数"),
    db: Session = Depends(get_db)
):
    """
    获取中美 CPI 对比数据
    """
    result = {
        "period": f"{months}个月",
        "series": []
    }
    
    for country in ["CN", "US"]:
        indicator = f"CPI_{country}"
        records = db.query(MacroData).filter(
            MacroData.indicator == indicator
        ).order_by(desc(MacroData.date)).limit(months).all()
        
        records = list(reversed(records))
        
        data = []
        for r in records:
            data.append([
                r.date.strftime("%Y-%m"),
                r.yoy_change  # 使用同比变化作为对比
            ])
        
        country_names = {"CN": "中国CPI同比", "US": "美国CPI同比"}
        
        result["series"].append({
            "name": country_names.get(country, country),
            "country": country,
            "data": data
        })
    
    return result


@router.get("/macro/oil_price")
def get_oil_price(
    months: int = Query(24, description="月数"),
    db: Session = Depends(get_db)
):
    """
    获取国内汽柴油调价历史
    """
    gasoline_records = db.query(MacroData).filter(
        MacroData.indicator == "GASOLINE_CN"
    ).order_by(desc(MacroData.date)).limit(months).all()
    
    diesel_records = db.query(MacroData).filter(
        MacroData.indicator == "DIESEL_CN"
    ).order_by(desc(MacroData.date)).limit(months).all()
    
    gasoline_data = [
        {"date": r.date.strftime("%Y-%m-%d"), "price": r.value}
        for r in reversed(gasoline_records)
    ]
    
    diesel_data = [
        {"date": r.date.strftime("%Y-%m-%d"), "price": r.value}
        for r in reversed(diesel_records)
    ]
    
    return {
        "gasoline": {
            "name": "92号汽油",
            "unit": "元/升",
            "data": gasoline_data
        },
        "diesel": {
            "name": "0号柴油",
            "unit": "元/升",
            "data": diesel_data
        }
    }


@router.get("/macro/indicators")
def get_macro_indicators():
    """
    获取所有支持的宏观指标
    """
    return {
        "indicators": [
            {"id": "CPI_CN", "name": "中国CPI", "frequency": "月度"},
            {"id": "CPI_US", "name": "美国CPI", "frequency": "月度"},
            {"id": "GASOLINE_CN", "name": "国内汽油价格", "frequency": "调价时"},
            {"id": "DIESEL_CN", "name": "国内柴油价格", "frequency": "调价时"},
        ]
    }
