"""
应用配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库路径
DATABASE_PATH = BASE_DIR / "data" / "commodities.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 确保数据目录存在
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# API 配置
API_PREFIX = "/api"

# 定时任务配置
SCHEDULER_CONFIG = {
    # 国内期货交易时段（包含夜盘）
    "cn_futures": {
        "day_hours": "9-11,13-15",  # 日盘
        "night_hours": "21-23,0-2",  # 夜盘
        "interval_minutes": 1,
    },
    # 日K线更新时间
    "daily_update_hour": 16,
    # 宏观数据更新（每月15日）
    "macro_update_day": 15,
}

# 品种配置
SYMBOLS_CONFIG = {
    # 贵金属
    "SHFE.AU": {"name": "沪金主力", "akshare_code": "AU0", "market": "CN", "unit": "CNY/g"},
    "SHFE.AG": {"name": "沪银主力", "akshare_code": "AG0", "market": "CN", "unit": "CNY/kg"},
    "XAU": {"name": "伦敦金", "market": "INTL", "unit": "USD/oz"},
    "XAG": {"name": "伦敦银", "market": "INTL", "unit": "USD/oz"},
    
    # 有色金属
    "SHFE.CU": {"name": "沪铜主力", "akshare_code": "CU0", "market": "CN", "unit": "CNY/ton"},
    "SHFE.AL": {"name": "沪铝主力", "akshare_code": "AL0", "market": "CN", "unit": "CNY/ton"},
    "LME.CU": {"name": "LME铜", "market": "LME", "unit": "USD/ton"},
    "LME.AL": {"name": "LME铝", "market": "LME", "unit": "USD/ton"},
    
    # 能源
    "INE.SC": {"name": "INE原油主力", "akshare_code": "SC0", "market": "CN", "unit": "CNY/barrel"},
    "BRENT": {"name": "布伦特原油", "market": "INTL", "unit": "USD/barrel"},
    "NG": {"name": "天然气", "market": "INTL", "unit": "USD/mmBtu"},
    
    # 化工
    "CZCE.TA": {"name": "PTA主力", "akshare_code": "TA0", "market": "CN", "unit": "CNY/ton"},
    "CZCE.MA": {"name": "甲醇主力", "akshare_code": "MA0", "market": "CN", "unit": "CNY/ton"},
    
    # 农产品
    "CBOT.S": {"name": "CBOT大豆", "market": "INTL", "unit": "USD/bushel"},
    "CBOT.C": {"name": "CBOT玉米", "market": "INTL", "unit": "USD/bushel"},
    "DCE.M": {"name": "豆粕主力", "akshare_code": "M0", "market": "CN", "unit": "CNY/ton"},
    "DCE.C": {"name": "玉米主力", "akshare_code": "C0", "market": "CN", "unit": "CNY/ton"},
    "DCE.LH": {"name": "生猪主力", "akshare_code": "LH0", "market": "CN", "unit": "CNY/ton"},
}

# 溢价率计算配对
PREMIUM_PAIRS = {
    "GOLD": {"domestic": "SHFE.AU", "foreign": "XAU", "name": "黄金溢价率"},
    "SILVER": {"domestic": "SHFE.AG", "foreign": "XAG", "name": "白银溢价率"},
    "COPPER": {"domestic": "SHFE.CU", "foreign": "LME.CU", "name": "铜溢价率"},
    "ALUMINUM": {"domestic": "SHFE.AL", "foreign": "LME.AL", "name": "铝溢价率"},
}

# 单位换算常量
CONVERSION_CONSTANTS = {
    "OZ_TO_GRAM": 31.1035,  # 1金衡盎司 = 31.1035克
    "OZ_TO_KG": 0.0311035,  # 1金衡盎司 = 0.0311035千克
}
