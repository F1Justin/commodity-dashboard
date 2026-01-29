"""
溢价率计算器核心模块
"""
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import SessionLocal, RealtimePrice, SpreadData, RatioData
from app.config import PREMIUM_PAIRS, SYMBOLS_CONFIG
from app.fetchers.exchange_rate_fetcher import get_latest_exchange_rate
from app.calculator.converter import (
    get_theoretical_price,
    calculate_premium_rate,
    calculate_gold_silver_ratio,
    calculate_copper_gold_ratio,
)


def get_latest_price(db: Session, symbol: str) -> Optional[float]:
    """获取某品种的最新价格"""
    record = db.query(RealtimePrice).filter(
        RealtimePrice.symbol == symbol
    ).order_by(desc(RealtimePrice.timestamp)).first()
    
    return record.price if record else None


def calculate_current_premiums(db: Session = None, return_prices: bool = False) -> Dict:
    """
    计算当前所有品种的溢价率
    
    Args:
        db: 数据库会话
        return_prices: 是否在返回结果中包含原始价格字典
    
    Returns:
        包含所有溢价率和比值指标的字典
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    try:
        # 获取汇率
        exchange_rate = get_latest_exchange_rate()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "exchange_rate": exchange_rate,
        }
        
        # 获取所有需要的价格
        prices = {}
        for symbol in SYMBOLS_CONFIG.keys():
            price = get_latest_price(db, symbol)
            if price:
                prices[symbol] = price
        
        # 计算各品种溢价率
        # 黄金
        if "SHFE.AU" in prices and "XAU" in prices:
            theoretical = get_theoretical_price("XAU", prices["XAU"], exchange_rate)
            premium = calculate_premium_rate(prices["SHFE.AU"], theoretical)
            result["gold"] = {
                "london_usd_oz": prices["XAU"],
                "shfe_cny_g": prices["SHFE.AU"],
                "theoretical_cny_g": round(theoretical, 2),
                "premium_rate": premium,
            }
        
        # 白银
        if "SHFE.AG" in prices and "XAG" in prices:
            theoretical = get_theoretical_price("XAG", prices["XAG"], exchange_rate)
            premium = calculate_premium_rate(prices["SHFE.AG"], theoretical)
            result["silver"] = {
                "london_usd_oz": prices["XAG"],
                "shfe_cny_kg": prices["SHFE.AG"],
                "theoretical_cny_kg": round(theoretical, 2),
                "premium_rate": premium,
            }
        
        # 铜
        if "SHFE.CU" in prices and "LME.CU" in prices:
            theoretical = get_theoretical_price("LME.CU", prices["LME.CU"], exchange_rate)
            premium = calculate_premium_rate(prices["SHFE.CU"], theoretical)
            result["copper"] = {
                "lme_usd_ton": prices["LME.CU"],
                "shfe_cny_ton": prices["SHFE.CU"],
                "theoretical_cny_ton": round(theoretical, 2),
                "premium_rate": premium,
            }
        
        # 铝
        if "SHFE.AL" in prices and "LME.AL" in prices:
            theoretical = get_theoretical_price("LME.AL", prices["LME.AL"], exchange_rate)
            premium = calculate_premium_rate(prices["SHFE.AL"], theoretical)
            result["aluminum"] = {
                "lme_usd_ton": prices["LME.AL"],
                "shfe_cny_ton": prices["SHFE.AL"],
                "theoretical_cny_ton": round(theoretical, 2),
                "premium_rate": premium,
            }
        
        # 计算比值指标
        ratios = {}
        
        # 金银比
        if "XAU" in prices and "XAG" in prices:
            ratios["gold_silver"] = calculate_gold_silver_ratio(
                prices["XAU"], prices["XAG"]
            )
        
        # 铜金比
        if "LME.CU" in prices and "XAU" in prices:
            ratios["copper_gold"] = calculate_copper_gold_ratio(
                prices["LME.CU"], prices["XAU"]
            )
        
        if ratios:
            result["ratios"] = ratios
        
        # 返回原始价格用于告警计算（金油比等）
        if return_prices:
            result["_prices"] = prices
        
        return result
        
    finally:
        if close_db:
            db.close()


def calculate_and_save_premiums():
    """
    计算并保存溢价率数据到数据库
    """
    db = SessionLocal()
    
    try:
        result = calculate_current_premiums(db, return_prices=True)
        
        # 提取价格用于告警
        prices = result.pop("_prices", {})
        
        if not result:
            return
        
        timestamp = datetime.now()
        exchange_rate = result.get("exchange_rate", 7.25)
        
        # 保存黄金溢价率
        if "gold" in result:
            gold = result["gold"]
            record = SpreadData(
                timestamp=timestamp,
                pair="GOLD",
                name="黄金溢价率",
                domestic_price=gold["shfe_cny_g"],
                foreign_price=gold["london_usd_oz"],
                theoretical_price=gold["theoretical_cny_g"],
                exchange_rate=exchange_rate,
                spread_rate=gold["premium_rate"]
            )
            db.add(record)
        
        # 保存白银溢价率
        if "silver" in result:
            silver = result["silver"]
            record = SpreadData(
                timestamp=timestamp,
                pair="SILVER",
                name="白银溢价率",
                domestic_price=silver["shfe_cny_kg"],
                foreign_price=silver["london_usd_oz"],
                theoretical_price=silver["theoretical_cny_kg"],
                exchange_rate=exchange_rate,
                spread_rate=silver["premium_rate"]
            )
            db.add(record)
        
        # 保存铜溢价率
        if "copper" in result:
            copper = result["copper"]
            record = SpreadData(
                timestamp=timestamp,
                pair="COPPER",
                name="铜溢价率",
                domestic_price=copper["shfe_cny_ton"],
                foreign_price=copper["lme_usd_ton"],
                theoretical_price=copper["theoretical_cny_ton"],
                exchange_rate=exchange_rate,
                spread_rate=copper["premium_rate"]
            )
            db.add(record)
        
        # 保存铝溢价率
        if "aluminum" in result:
            aluminum = result["aluminum"]
            record = SpreadData(
                timestamp=timestamp,
                pair="ALUMINUM",
                name="铝溢价率",
                domestic_price=aluminum["shfe_cny_ton"],
                foreign_price=aluminum["lme_usd_ton"],
                theoretical_price=aluminum["theoretical_cny_ton"],
                exchange_rate=exchange_rate,
                spread_rate=aluminum["premium_rate"]
            )
            db.add(record)
        
        # 保存比值指标
        if "ratios" in result:
            ratios = result["ratios"]
            
            if "gold_silver" in ratios:
                record = RatioData(
                    timestamp=timestamp,
                    ratio_type="GOLD_SILVER",
                    name="金银比",
                    value=ratios["gold_silver"]
                )
                db.add(record)
            
            if "copper_gold" in ratios:
                record = RatioData(
                    timestamp=timestamp,
                    ratio_type="COPPER_GOLD",
                    name="铜金比",
                    value=ratios["copper_gold"]
                )
                db.add(record)
        
        db.commit()
        print(f"✅ 溢价率数据已保存")
        
        # 检查告警条件
        try:
            from app.alert import check_all_alerts
            check_all_alerts(result, prices=prices)
        except Exception as alert_error:
            print(f"⚠️ 告警检查失败（不影响主流程）: {alert_error}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 保存溢价率数据失败: {e}")
    finally:
        db.close()
