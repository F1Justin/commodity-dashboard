"""
定时任务调度器 - APScheduler
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

scheduler = BackgroundScheduler()


def fetch_cn_futures_job():
    """采集国内期货数据"""
    from app.fetchers.futures_fetcher import fetch_cn_futures
    print(f"[{datetime.now()}] 开始采集国内期货数据...")
    try:
        fetch_cn_futures()
        print(f"[{datetime.now()}] 国内期货数据采集完成")
    except Exception as e:
        print(f"[{datetime.now()}] 国内期货数据采集失败: {e}")


def fetch_intl_futures_job():
    """采集国际期货数据"""
    from app.fetchers.futures_fetcher import fetch_intl_futures
    print(f"[{datetime.now()}] 开始采集国际期货数据...")
    try:
        fetch_intl_futures()
        print(f"[{datetime.now()}] 国际期货数据采集完成")
    except Exception as e:
        print(f"[{datetime.now()}] 国际期货数据采集失败: {e}")


def update_exchange_rate_job():
    """更新汇率数据"""
    from app.fetchers.exchange_rate_fetcher import fetch_exchange_rate
    print(f"[{datetime.now()}] 开始更新汇率...")
    try:
        fetch_exchange_rate()
        print(f"[{datetime.now()}] 汇率更新完成")
    except Exception as e:
        print(f"[{datetime.now()}] 汇率更新失败: {e}")


def calculate_premium_job():
    """计算并保存溢价率"""
    from app.calculator.premium_calculator import calculate_and_save_premiums
    print(f"[{datetime.now()}] 开始计算溢价率...")
    try:
        calculate_and_save_premiums()
        print(f"[{datetime.now()}] 溢价率计算完成")
    except Exception as e:
        print(f"[{datetime.now()}] 溢价率计算失败: {e}")


def update_daily_ohlc_job():
    """更新日K线数据"""
    from app.fetchers.daily_fetcher import update_daily_ohlc
    print(f"[{datetime.now()}] 开始更新日K线...")
    try:
        update_daily_ohlc()
        print(f"[{datetime.now()}] 日K线更新完成")
    except Exception as e:
        print(f"[{datetime.now()}] 日K线更新失败: {e}")


def update_macro_data_job():
    """更新宏观数据（CPI、汽柴油价格等）"""
    from app.fetchers.macro_fetcher import update_macro_data
    print(f"[{datetime.now()}] 开始更新宏观数据...")
    try:
        update_macro_data()
        print(f"[{datetime.now()}] 宏观数据更新完成")
    except Exception as e:
        print(f"[{datetime.now()}] 宏观数据更新失败: {e}")


def send_daily_summary_job():
    """发送每日市场简报"""
    print(f"[{datetime.now()}] 发送每日市场简报...")
    try:
        from app.alert import send_daily_briefing
        from app.calculator.premium_calculator import calculate_current_premiums
        
        calculator_data = calculate_current_premiums(return_prices=True)
        prices = calculator_data.pop("_prices", {})
        send_daily_briefing(calculator_data, prices)
        print(f"[{datetime.now()}] 每日简报发送完成")
    except Exception as e:
        print(f"[{datetime.now()}] 每日简报发送失败: {e}")


def start_scheduler():
    """启动定时任务调度器"""
    
    # 国内期货日盘 - 每分钟采集 (9:00-11:30, 13:30-15:00)
    scheduler.add_job(
        fetch_cn_futures_job,
        CronTrigger(minute='*', hour='9-11,13-15', day_of_week='mon-fri'),
        id='fetch_cn_futures_day',
        replace_existing=True
    )
    
    # 国内期货夜盘 - 每分钟采集 (21:00-23:59, 00:00-02:30)
    scheduler.add_job(
        fetch_cn_futures_job,
        CronTrigger(minute='*', hour='21-23,0-2', day_of_week='mon-fri'),
        id='fetch_cn_futures_night',
        replace_existing=True
    )
    
    # 国际期货 - 每分钟采集（24小时交易）
    scheduler.add_job(
        fetch_intl_futures_job,
        CronTrigger(minute='*/2'),  # 每2分钟，避免过于频繁
        id='fetch_intl_futures',
        replace_existing=True
    )
    
    # 汇率 - 每5分钟更新一次（极端行情下汇率波动可能很大）
    scheduler.add_job(
        update_exchange_rate_job,
        CronTrigger(minute='*/5'),
        id='update_exchange_rate',
        replace_existing=True
    )
    
    # 溢价率计算 - 每分钟计算一次
    scheduler.add_job(
        calculate_premium_job,
        CronTrigger(minute='*'),
        id='calculate_premium',
        replace_existing=True
    )
    
    # 日K线 - 每天16:00更新
    scheduler.add_job(
        update_daily_ohlc_job,
        CronTrigger(hour='16', minute='0'),
        id='update_daily_ohlc',
        replace_existing=True
    )
    
    # 宏观数据 - 每月15日10:00更新
    scheduler.add_job(
        update_macro_data_job,
        CronTrigger(day='15', hour='10', minute='0'),
        id='update_macro_data',
        replace_existing=True
    )
    
    # 每日市场简报 - 每天 8:30 和 15:30 发送
    scheduler.add_job(
        send_daily_summary_job,
        CronTrigger(hour='8,15', minute='30'),
        id='send_daily_summary',
        replace_existing=True
    )
    
    scheduler.start()
    print("📅 定时任务调度器已启动")


def shutdown_scheduler():
    """关闭定时任务调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("📅 定时任务调度器已关闭")


def run_job_now(job_id: str):
    """立即执行指定任务"""
    job_map = {
        'fetch_cn_futures': fetch_cn_futures_job,
        'fetch_intl_futures': fetch_intl_futures_job,
        'update_exchange_rate': update_exchange_rate_job,
        'calculate_premium': calculate_premium_job,
        'update_daily_ohlc': update_daily_ohlc_job,
        'update_macro_data': update_macro_data_job,
        'send_daily_summary': send_daily_summary_job,
    }
    
    if job_id in job_map:
        job_map[job_id]()
        return True
    return False
