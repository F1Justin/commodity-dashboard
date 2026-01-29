"""
日K线数据采集器
"""
from datetime import datetime, date, timedelta
from typing import Dict, List
import akshare as ak

from app.database import SessionLocal, DailyOHLC
from app.config import SYMBOLS_CONFIG


def fetch_cn_daily_ohlc(symbol: str, ak_code: str, days: int = 30) -> List[dict]:
    """
    获取国内期货日K线数据
    """
    data = []
    try:
        df = ak.futures_zh_daily_sina(symbol=ak_code)
        if df is not None and not df.empty:
            # 取最近 N 天
            df = df.tail(days)
            for _, row in df.iterrows():
                data.append({
                    "date": row['date'] if isinstance(row['date'], date) else datetime.strptime(str(row['date']), "%Y-%m-%d").date(),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume']) if 'volume' in row else 0,
                })
    except Exception as e:
        print(f"获取 {symbol} 日K线失败: {e}")
    
    return data


def fetch_intl_daily_ohlc(symbol: str, name: str, days: int = 30) -> List[dict]:
    """
    获取国际期货日K线数据
    """
    data = []
    try:
        df = ak.futures_foreign_hist(symbol=name)
        if df is not None and not df.empty:
            df = df.tail(days)
            for _, row in df.iterrows():
                trade_date = row.get('日期') or row.get('date')
                if isinstance(trade_date, str):
                    trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
                
                data.append({
                    "date": trade_date,
                    "open": float(row.get('开盘价') or row.get('open', 0)),
                    "high": float(row.get('最高价') or row.get('high', 0)),
                    "low": float(row.get('最低价') or row.get('low', 0)),
                    "close": float(row.get('收盘价') or row.get('close', 0)),
                    "volume": int(row.get('成交量') or row.get('volume', 0)),
                })
    except Exception as e:
        print(f"获取 {symbol} ({name}) 日K线失败: {e}")
    
    return data


def save_daily_ohlc(symbol: str, name: str, data: List[dict]):
    """
    保存日K线数据
    """
    if not data:
        return
    
    db = SessionLocal()
    try:
        for item in data:
            # 检查是否已存在
            existing = db.query(DailyOHLC).filter(
                DailyOHLC.symbol == symbol,
                DailyOHLC.date == item["date"]
            ).first()
            
            if existing:
                # 更新
                existing.open = item["open"]
                existing.high = item["high"]
                existing.low = item["low"]
                existing.close = item["close"]
                existing.volume = item["volume"]
            else:
                # 新增
                record = DailyOHLC(
                    date=item["date"],
                    symbol=symbol,
                    name=name,
                    open=item["open"],
                    high=item["high"],
                    low=item["low"],
                    close=item["close"],
                    volume=item["volume"]
                )
                db.add(record)
        
        db.commit()
        print(f"✅ 已保存 {symbol} 的 {len(data)} 条日K线数据")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 保存 {symbol} 日K线失败: {e}")
    finally:
        db.close()


def update_daily_ohlc(days: int = 30):
    """
    更新所有品种的日K线数据
    """
    # 国内期货
    cn_map = {
        "SHFE.AU": "AU0",
        "SHFE.AG": "AG0",
        "SHFE.CU": "CU0",
        "SHFE.AL": "AL0",
        "INE.SC": "SC0",
        "CZCE.TA": "TA0",
        "CZCE.MA": "MA0",
        "DCE.M": "M0",
        "DCE.C": "C0",
        "DCE.LH": "LH0",
    }
    
    for symbol, ak_code in cn_map.items():
        config = SYMBOLS_CONFIG.get(symbol, {})
        data = fetch_cn_daily_ohlc(symbol, ak_code, days)
        save_daily_ohlc(symbol, config.get("name", symbol), data)
    
    # 国际期货
    intl_map = {
        "XAU": "伦敦金",
        "XAG": "伦敦银",
        "LME.CU": "LME铜",
        "LME.AL": "LME铝",
        "BRENT": "布伦特原油",
        "NG": "NYMEX天然气",
        "CBOT.S": "CBOT大豆",
        "CBOT.C": "CBOT玉米",
    }
    
    for symbol, name in intl_map.items():
        config = SYMBOLS_CONFIG.get(symbol, {})
        data = fetch_intl_daily_ohlc(symbol, name, days)
        save_daily_ohlc(symbol, config.get("name", symbol), data)
    
    print(f"📊 日K线数据更新完成")
