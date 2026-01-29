"""
汇率数据采集器 - 使用多个数据源确保可靠性
根据 接口.md 使用:
- fx_spot_quote: 人民币外汇即期报价
- forex_spot_em: 东方财富网-外汇市场-所有汇率-实时行情数据
"""
from datetime import datetime
from typing import Optional, Tuple
import akshare as ak

from app.database import SessionLocal, ExchangeRate


def get_exchange_rate_fx_spot() -> Optional[float]:
    """
    从人民币外汇即期报价获取汇率
    使用 fx_spot_quote 接口
    """
    try:
        df = ak.fx_spot_quote()
        if df is not None and not df.empty:
            usd_row = df[df['货币对'] == 'USD/CNY']
            if not usd_row.empty:
                rate = float(usd_row.iloc[0]['买报价'])
                return rate
    except Exception as e:
        print(f"fx_spot_quote 获取汇率失败: {e}")
    return None


def get_exchange_rate_forex_em() -> Optional[float]:
    """
    从东方财富外汇行情获取汇率
    使用 forex_spot_em 接口
    """
    try:
        df = ak.forex_spot_em()
        if df is not None and not df.empty:
            # 尝试找美元人民币中间价
            usd_row = df[df['名称'] == '美元人民币中间价']
            if not usd_row.empty:
                rate = float(usd_row.iloc[0]['最新价'])
                return rate
            
            # 备选: 美元兑离岸人民币
            usd_row = df[df['名称'] == '美元兑离岸人民币']
            if not usd_row.empty:
                rate = float(usd_row.iloc[0]['最新价'])
                return rate
    except Exception as e:
        print(f"forex_spot_em 获取汇率失败: {e}")
    return None


def get_current_exchange_rate() -> Tuple[float, str]:
    """
    获取当前美元兑人民币汇率
    优先使用 fx_spot_quote，失败则用 forex_spot_em
    """
    # 方法1: fx_spot_quote (人民币外汇即期报价)
    rate = get_exchange_rate_fx_spot()
    if rate:
        return rate, "FX_SPOT_QUOTE"
    
    # 方法2: forex_spot_em (东方财富外汇行情)
    rate = get_exchange_rate_forex_em()
    if rate:
        return rate, "FOREX_EM"
    
    # 兜底: 使用默认值
    print("⚠️ 无法获取实时汇率，使用默认值 7.25")
    return 7.25, "DEFAULT"


def fetch_exchange_rate():
    """
    采集并保存汇率数据
    """
    rate, source = get_current_exchange_rate()
    
    db = SessionLocal()
    try:
        record = ExchangeRate(
            timestamp=datetime.now(),
            currency_pair="USD/CNY",
            rate=rate,
            source=source
        )
        
        db.add(record)
        db.commit()
        print(f"✅ 汇率已更新: {rate} (来源: {source})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 保存汇率失败: {e}")
    finally:
        db.close()
    
    return rate


def get_latest_exchange_rate() -> float:
    """
    获取最新汇率，优先从数据库获取，否则实时获取
    """
    db = SessionLocal()
    try:
        record = db.query(ExchangeRate).filter(
            ExchangeRate.currency_pair == "USD/CNY"
        ).order_by(ExchangeRate.timestamp.desc()).first()
        
        if record:
            # 如果数据库有记录，检查是否过期（超过1小时）
            age = (datetime.now() - record.timestamp).total_seconds()
            if age < 3600:  # 1小时内的数据有效
                return record.rate
        
        # 实时获取
        rate, _ = get_current_exchange_rate()
        return rate
    finally:
        db.close()
