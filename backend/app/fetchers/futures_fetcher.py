"""
期货数据采集器 - 带备份数据源和重试机制
主数据源: AkShare
备份数据源: yfinance (国际期货)
"""
from datetime import datetime
from typing import Dict, Optional, Callable
import time
import akshare as ak

# 尝试导入 yfinance 作为备份
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️ yfinance 未安装，国际数据将没有备份源")

from app.database import SessionLocal, RealtimePrice
from app.config import SYMBOLS_CONFIG
from app.fetchers.exchange_rate_fetcher import get_latest_exchange_rate
from app.calculator.converter import convert_to_cny


# 国内期货代码映射 - 使用 futures_main_sina
CN_FUTURES_CODES = {
    "SHFE.AU": "AU0",   # 沪金主力
    "SHFE.AG": "AG0",   # 沪银主力
    "SHFE.CU": "CU0",   # 沪铜主力
    "SHFE.AL": "AL0",   # 沪铝主力
    "INE.SC": "SC0",    # 原油主力
    "CZCE.TA": "TA0",   # PTA主力
    "CZCE.MA": "MA0",   # 甲醇主力
    "DCE.M": "M0",      # 豆粕主力
    "DCE.C": "C0",      # 玉米主力
    "DCE.LH": "LH0",    # 生猪主力
}

# 外盘期货代码映射 - AkShare (futures_foreign_hist)
INTL_FUTURES_CODES_AKSHARE = {
    "XAU": "GC",      # COMEX黄金
    "XAG": "SI",      # COMEX白银
    "NG": "NG",       # NYMEX天然气
    "CBOT.S": "S",    # CBOT大豆
    "CBOT.C": "C",    # CBOT玉米
}

# 外盘期货代码映射 - yfinance (备份)
INTL_FUTURES_CODES_YFINANCE = {
    "XAU": "GC=F",     # COMEX黄金
    "XAG": "SI=F",     # COMEX白银
    "LME.CU": "HG=F",  # COMEX铜 (作为LME铜的备份)
    "NG": "NG=F",      # NYMEX天然气
    "BRENT": "BZ=F",   # 布伦特原油
}


def retry_with_backoff(func: Callable, max_retries: int = 3, base_delay: float = 1.0):
    """
    带指数退避的重试装饰器
    """
    def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"  重试 {attempt + 1}/{max_retries}，等待 {delay}s: {e}")
                    time.sleep(delay)
        raise last_error
    return wrapper


def fetch_cn_futures_prices() -> Dict[str, float]:
    """
    获取国内期货实时价格
    使用 futures_main_sina 接口，带重试机制
    """
    prices = {}
    
    for symbol, code in CN_FUTURES_CODES.items():
        try:
            @retry_with_backoff
            def get_price():
                df = ak.futures_main_sina(symbol=code)
                if df is not None and not df.empty:
                    return float(df.iloc[-1]['收盘价'])
                return None
            
            price = get_price()
            if price:
                prices[symbol] = price
                print(f"  {symbol}: {price}")
        except Exception as e:
            print(f"  ❌ 获取 {symbol} ({code}) 失败: {e}")
    
    return prices


def fetch_intl_futures_prices_akshare() -> Dict[str, float]:
    """
    从 AkShare 获取国际期货价格 (主数据源)
    """
    prices = {}
    
    for symbol, code in INTL_FUTURES_CODES_AKSHARE.items():
        try:
            df = ak.futures_foreign_hist(symbol=code)
            if df is not None and not df.empty:
                price = float(df.iloc[-1]['close'])
                prices[symbol] = price
                print(f"  {symbol}: {price} (AkShare)")
        except Exception as e:
            print(f"  ⚠️ AkShare 获取 {symbol} ({code}) 失败: {e}")
    
    return prices


def fetch_intl_futures_prices_yfinance() -> Dict[str, float]:
    """
    从 yfinance 获取国际期货价格 (备份数据源)
    Yahoo Finance API 非常稳定
    """
    if not YFINANCE_AVAILABLE:
        return {}
    
    prices = {}
    
    for symbol, ticker in INTL_FUTURES_CODES_YFINANCE.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="1d")
            if hist is not None and not hist.empty:
                price = float(hist['Close'].iloc[-1])
                prices[symbol] = price
                print(f"  {symbol}: {price} (yfinance 备份)")
        except Exception as e:
            print(f"  ⚠️ yfinance 获取 {symbol} ({ticker}) 失败: {e}")
    
    return prices


def fetch_intl_futures_prices() -> Dict[str, float]:
    """
    获取国际期货价格 - 主备切换
    优先使用 AkShare，失败时切换到 yfinance
    """
    # 先尝试 AkShare
    print("  尝试 AkShare...")
    prices = fetch_intl_futures_prices_akshare()
    
    # 检查缺失的品种，用 yfinance 补充
    missing_symbols = set(INTL_FUTURES_CODES_YFINANCE.keys()) - set(prices.keys())
    
    if missing_symbols and YFINANCE_AVAILABLE:
        print(f"  缺失品种 {missing_symbols}，尝试 yfinance 备份...")
        backup_prices = fetch_intl_futures_prices_yfinance()
        
        for symbol in missing_symbols:
            if symbol in backup_prices:
                prices[symbol] = backup_prices[symbol]
    
    return prices


def fetch_global_spot_prices() -> Dict[str, float]:
    """
    获取全球期货现货价格
    使用 futures_global_spot_em 接口 (东方财富网-国际期货-实时行情)
    获取 LME 金属和布伦特原油
    """
    prices = {}
    
    try:
        @retry_with_backoff
        def get_global_data():
            return ak.futures_global_spot_em()
        
        df = get_global_data()
        if df is not None and not df.empty:
            # 查找综合铜03 (LME铜)
            cu = df[df['名称'] == '综合铜03']
            if not cu.empty:
                price = cu.iloc[0]['最新价']
                if price and str(price) != 'nan':
                    prices['LME.CU'] = float(price)
                    print(f"  LME.CU: {price}")
            
            # 查找综合铝03 (LME铝)
            al = df[df['名称'] == '综合铝03']
            if not al.empty:
                price = al.iloc[0]['最新价']
                if price and str(price) != 'nan':
                    prices['LME.AL'] = float(price)
                    print(f"  LME.AL: {price}")
            
            # 查找布伦特原油 (当月连续或最近合约)
            brent = df[df['名称'].str.contains('布伦特原油', na=False)]
            if not brent.empty:
                for _, row in brent.iterrows():
                    price = row['最新价']
                    if price and str(price) != 'nan':
                        prices['BRENT'] = float(price)
                        print(f"  BRENT ({row['名称']}): {price}")
                        break
                    
    except Exception as e:
        print(f"  ❌ 获取全球期货数据失败: {e}")
    
    return prices


def save_prices(prices: Dict[str, float], exchange_rate: float):
    """
    保存价格数据到数据库
    """
    if not prices:
        return
        
    db = SessionLocal()
    timestamp = datetime.now()
    
    try:
        for symbol, price in prices.items():
            if symbol not in SYMBOLS_CONFIG:
                continue
                
            config = SYMBOLS_CONFIG[symbol]
            
            # 计算人民币价格
            price_cny = convert_to_cny(symbol, price, exchange_rate)
            
            record = RealtimePrice(
                timestamp=timestamp,
                symbol=symbol,
                name=config["name"],
                price=price,
                price_cny=price_cny,
                unit=config["unit"],
                market=config["market"]
            )
            
            db.add(record)
        
        db.commit()
        print(f"✅ 已保存 {len(prices)} 条价格数据")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 保存价格数据失败: {e}")
    finally:
        db.close()


def fetch_cn_futures():
    """
    采集并保存国内期货数据
    """
    print(f"[{datetime.now()}] 开始采集国内期货数据...")
    exchange_rate = get_latest_exchange_rate()
    prices = fetch_cn_futures_prices()
    
    if prices:
        save_prices(prices, exchange_rate)
    else:
        print("⚠️ 未获取到国内期货数据")
    print(f"[{datetime.now()}] 国内期货数据采集完成")


def fetch_intl_futures():
    """
    采集并保存国际期货数据
    """
    print(f"[{datetime.now()}] 开始采集国际期货数据...")
    exchange_rate = get_latest_exchange_rate()
    
    # 国际期货 (COMEX/CBOT) - 带主备切换
    intl_prices = fetch_intl_futures_prices()
    
    # 全球期货 (LME + 布伦特原油)
    global_prices = fetch_global_spot_prices()
    
    all_prices = {**intl_prices, **global_prices}
    
    if all_prices:
        save_prices(all_prices, exchange_rate)
    else:
        print("⚠️ 未获取到国际期货数据")
    print(f"[{datetime.now()}] 国际期货数据采集完成")


def fetch_all_futures():
    """
    采集所有期货数据
    """
    print(f"[{datetime.now()}] 采集所有期货数据...")
    exchange_rate = get_latest_exchange_rate()
    print(f"当前汇率: {exchange_rate}")
    
    # 国内期货
    print("\n国内期货:")
    cn_prices = fetch_cn_futures_prices()
    
    # 国际期货 - 带主备切换
    print("\n国际期货:")
    intl_prices = fetch_intl_futures_prices()
    
    # 全球期货 (LME + 布伦特原油)
    print("\n全球期货 (LME+布伦特):")
    global_prices = fetch_global_spot_prices()
    
    all_prices = {**cn_prices, **intl_prices, **global_prices}
    
    if all_prices:
        save_prices(all_prices, exchange_rate)
    
    print(f"[{datetime.now()}] 所有期货数据采集完成")
    return all_prices
