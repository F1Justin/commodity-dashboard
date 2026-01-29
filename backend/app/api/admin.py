"""
管理 API - 手动触发任务
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.post("/admin/fetch-all")
def trigger_fetch_all():
    """
    手动触发采集所有数据
    """
    from app.fetchers.futures_fetcher import fetch_all_futures
    from app.fetchers.exchange_rate_fetcher import fetch_exchange_rate
    from app.calculator.premium_calculator import calculate_and_save_premiums
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tasks": []
    }
    
    # 1. 更新汇率
    try:
        rate = fetch_exchange_rate()
        results["tasks"].append({"name": "汇率更新", "status": "success", "rate": rate})
    except Exception as e:
        results["tasks"].append({"name": "汇率更新", "status": "error", "error": str(e)})
    
    # 2. 采集期货数据
    try:
        prices = fetch_all_futures()
        results["tasks"].append({
            "name": "期货数据采集", 
            "status": "success", 
            "count": len(prices),
            "symbols": list(prices.keys())
        })
    except Exception as e:
        results["tasks"].append({"name": "期货数据采集", "status": "error", "error": str(e)})
    
    # 3. 计算溢价率
    try:
        calculate_and_save_premiums()
        results["tasks"].append({"name": "溢价率计算", "status": "success"})
    except Exception as e:
        results["tasks"].append({"name": "溢价率计算", "status": "error", "error": str(e)})
    
    return results


@router.post("/admin/fetch-cn")
def trigger_fetch_cn():
    """手动触发采集国内期货数据"""
    from app.fetchers.futures_fetcher import fetch_cn_futures
    
    try:
        fetch_cn_futures()
        return {"status": "success", "message": "国内期货数据采集完成"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/admin/fetch-intl")
def trigger_fetch_intl():
    """手动触发采集国际期货数据"""
    from app.fetchers.futures_fetcher import fetch_intl_futures
    
    try:
        fetch_intl_futures()
        return {"status": "success", "message": "国际期货数据采集完成"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/admin/update-exchange-rate")
def trigger_update_exchange_rate():
    """手动更新汇率"""
    from app.fetchers.exchange_rate_fetcher import fetch_exchange_rate
    
    try:
        rate = fetch_exchange_rate()
        return {"status": "success", "rate": rate}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/admin/calculate-premium")
def trigger_calculate_premium():
    """手动计算溢价率"""
    from app.calculator.premium_calculator import calculate_and_save_premiums
    
    try:
        calculate_and_save_premiums()
        return {"status": "success", "message": "溢价率计算完成"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/admin/status")
def get_status():
    """获取系统状态"""
    from app.database import SessionLocal, RealtimePrice, ExchangeRate
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # 统计数据
        price_count = db.query(func.count(RealtimePrice.id)).scalar()
        latest_price = db.query(RealtimePrice).order_by(RealtimePrice.timestamp.desc()).first()
        latest_rate = db.query(ExchangeRate).order_by(ExchangeRate.timestamp.desc()).first()
        
        return {
            "price_records": price_count,
            "latest_price_time": latest_price.timestamp.isoformat() if latest_price else None,
            "exchange_rate": latest_rate.rate if latest_rate else None,
            "exchange_rate_time": latest_rate.timestamp.isoformat() if latest_rate else None,
            "exchange_rate_source": latest_rate.source if latest_rate else None,
        }
    finally:
        db.close()


@router.post("/admin/test-alert")
def test_alert():
    """测试告警发送"""
    from app.alert import send_test_alert
    
    success = send_test_alert()
    return {
        "status": "success" if success else "failed",
        "message": "告警测试消息已发送" if success else "告警发送失败，请检查配置"
    }


@router.post("/admin/send-summary")
def send_summary():
    """发送每日市场简报"""
    from app.alert import send_daily_briefing
    from app.calculator.premium_calculator import calculate_current_premiums
    
    try:
        calculator_data = calculate_current_premiums(return_prices=True)
        prices = calculator_data.pop("_prices", {})
        success = send_daily_briefing(calculator_data, prices)
        
        return {
            "status": "success" if success else "failed",
            "message": "每日简报已发送" if success else "简报发送失败"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
