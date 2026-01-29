"""
归一化图表 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db, DailyOHLC, RealtimePrice

router = APIRouter()

# 品种分组配置
CHART_GROUPS = {
    "precious_metals": {
        "name": "贵金属",
        "symbols": ["SHFE.AU", "SHFE.AG", "XAU", "XAG"],
    },
    "base_metals": {
        "name": "有色金属",
        "symbols": ["SHFE.CU", "SHFE.AL", "LME.CU", "LME.AL"],
    },
    "energy": {
        "name": "能源",
        "symbols": ["INE.SC", "BRENT", "NG"],
    },
    "agriculture": {
        "name": "农产品",
        "symbols": ["DCE.M", "DCE.C", "DCE.LH", "CBOT.S", "CBOT.C"],
    },
    "all": {
        "name": "全部品种",
        "symbols": [
            "SHFE.AU", "SHFE.AG", "XAU", "XAG",
            "SHFE.CU", "SHFE.AL", "LME.CU", "LME.AL",
            "INE.SC", "BRENT", "NG",
            "DCE.M", "DCE.C", "DCE.LH", "CBOT.S", "CBOT.C"
        ],
    },
}

# 品种名称映射
SYMBOL_NAMES = {
    "SHFE.AU": "沪金",
    "SHFE.AG": "沪银",
    "XAU": "伦敦金",
    "XAG": "伦敦银",
    "SHFE.CU": "沪铜",
    "SHFE.AL": "沪铝",
    "LME.CU": "LME铜",
    "LME.AL": "LME铝",
    "INE.SC": "INE原油",
    "BRENT": "布伦特原油",
    "NG": "天然气",
    "DCE.M": "豆粕",
    "DCE.C": "玉米",
    "DCE.LH": "生猪",
    "CBOT.S": "CBOT大豆",
    "CBOT.C": "CBOT玉米",
    "CZCE.TA": "PTA",
    "CZCE.MA": "甲醇",
}


def get_period_days(period: str) -> int:
    """将周期字符串转换为天数"""
    period_map = {
        "1d": 1,       # 1天
        "3d": 3,       # 3天
        "7d": 7,       # 1周
        "14d": 14,     # 2周
        "30d": 30,     # 1个月
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365,
        "3y": 1095,
        "all": 3650,   # 10年
    }
    return period_map.get(period, 7)


@router.get("/normalized")
def get_normalized_data(
    group: str = Query("precious_metals", description="分组: precious_metals, base_metals, energy, agriculture, all"),
    period: str = Query("7d", description="周期: 1d, 3d, 7d, 14d, 30d, 1m, 3m, 6m, 1y, 3y, all"),
    base_date: Optional[str] = Query(None, description="基准日期 YYYY-MM-DD，默认为周期起点"),
    db: Session = Depends(get_db)
):
    """
    获取归一化后的多品种数据，用于对比走势
    """
    if group not in CHART_GROUPS:
        return {"error": f"未知分组: {group}，可选: {list(CHART_GROUPS.keys())}"}
    
    group_config = CHART_GROUPS[group]
    symbols = group_config["symbols"]
    
    # 计算日期范围
    days = get_period_days(period)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # 如果指定了基准日期
    if base_date:
        try:
            base_date_obj = datetime.strptime(base_date, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "日期格式错误，请使用 YYYY-MM-DD"}
    else:
        base_date_obj = start_date
    
    series = []
    
    for symbol in symbols:
        # 获取该品种的日K线数据
        records = db.query(DailyOHLC).filter(
            DailyOHLC.symbol == symbol,
            DailyOHLC.date >= start_date,
            DailyOHLC.date <= end_date
        ).order_by(DailyOHLC.date).all()
        
        # 如果没有日K数据，尝试从实时数据获取
        if not records:
            realtime_records = db.query(RealtimePrice).filter(
                RealtimePrice.symbol == symbol,
                RealtimePrice.timestamp >= datetime.combine(start_date, datetime.min.time()),
            ).order_by(RealtimePrice.timestamp).all()
            
            if not realtime_records:
                continue
            
            # 使用第一条数据的价格作为基准
            base_price = realtime_records[0].price if realtime_records[0].price else 100
            
            # 按时间分组，取每个时间点的数据
            data = []
            for r in realtime_records:
                if r.price and base_price:
                    normalized_value = round(r.price / base_price * 100, 2)
                    data.append([
                        r.timestamp.isoformat(),
                        normalized_value
                    ])
            
            if data:
                series.append({
                    "symbol": symbol,
                    "name": SYMBOL_NAMES.get(symbol, symbol),
                    "data": data
                })
            continue
        
        # 获取基准价格（基准日期的收盘价）
        base_record = db.query(DailyOHLC).filter(
            DailyOHLC.symbol == symbol,
            DailyOHLC.date <= base_date_obj
        ).order_by(desc(DailyOHLC.date)).first()
        
        if not base_record or not base_record.close:
            # 使用第一条数据作为基准
            base_price = records[0].close if records[0].close else 100
        else:
            base_price = base_record.close
        
        # 归一化处理
        data = []
        for r in records:
            if r.close and base_price:
                normalized_value = round(r.close / base_price * 100, 2)
                data.append([
                    r.date.isoformat(),
                    normalized_value
                ])
        
        if data:
            series.append({
                "symbol": symbol,
                "name": SYMBOL_NAMES.get(symbol, symbol),
                "data": data
            })
    
    return {
        "group": group,
        "group_name": group_config["name"],
        "period": period,
        "base_date": base_date_obj.isoformat(),
        "base_value": 100,
        "series": series
    }


@router.get("/normalized/groups")
def get_chart_groups():
    """
    获取所有归一化图表分组
    """
    groups = []
    for key, config in CHART_GROUPS.items():
        groups.append({
            "id": key,
            "name": config["name"],
            "symbols": [
                {"symbol": s, "name": SYMBOL_NAMES.get(s, s)}
                for s in config["symbols"]
            ]
        })
    
    return {"groups": groups}
