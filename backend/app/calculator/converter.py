"""
单位换算模块
将国际价格换算为人民币价格，统一单位
"""
from app.config import CONVERSION_CONSTANTS

# 品种换算配置
CONVERSION_CONFIG = {
    # 贵金属 - 国际市场 USD/oz，国内市场 CNY/g 或 CNY/kg
    "XAU": {
        "from_unit": "USD/oz",
        "to_unit": "CNY/g",
        "conversion": lambda price, rate: price * rate / CONVERSION_CONSTANTS["OZ_TO_GRAM"],
    },
    "XAG": {
        "from_unit": "USD/oz",
        "to_unit": "CNY/kg",
        "conversion": lambda price, rate: price * rate / CONVERSION_CONSTANTS["OZ_TO_GRAM"] * 1000,
    },
    
    # 有色金属 - 国际市场 USD/ton，国内市场 CNY/ton
    "LME.CU": {
        "from_unit": "USD/ton",
        "to_unit": "CNY/ton",
        "conversion": lambda price, rate: price * rate,
    },
    "LME.AL": {
        "from_unit": "USD/ton",
        "to_unit": "CNY/ton",
        "conversion": lambda price, rate: price * rate,
    },
    
    # 能源 - 原油 USD/barrel，天然气 USD/mmBtu
    "BRENT": {
        "from_unit": "USD/barrel",
        "to_unit": "CNY/barrel",
        "conversion": lambda price, rate: price * rate,
    },
    "NG": {
        "from_unit": "USD/mmBtu",
        "to_unit": "CNY/mmBtu",
        "conversion": lambda price, rate: price * rate,
    },
    
    # 农产品 - 美分/蒲式耳 或 USD/ton
    "CBOT.S": {
        "from_unit": "USD/bushel",
        "to_unit": "CNY/ton",
        # 大豆: 1蒲式耳 ≈ 27.2公斤 = 0.0272吨
        "conversion": lambda price, rate: price * rate / 0.0272,
    },
    "CBOT.C": {
        "from_unit": "USD/bushel",
        "to_unit": "CNY/ton",
        # 玉米: 1蒲式耳 ≈ 25.4公斤 = 0.0254吨
        "conversion": lambda price, rate: price * rate / 0.0254,
    },
}


def convert_to_cny(symbol: str, price: float, exchange_rate: float) -> float:
    """
    将国际价格换算为人民币价格
    
    Args:
        symbol: 品种代码
        price: 原始价格
        exchange_rate: 美元兑人民币汇率
    
    Returns:
        换算后的人民币价格
    """
    config = CONVERSION_CONFIG.get(symbol)
    
    if config and "conversion" in config:
        return config["conversion"](price, exchange_rate)
    
    # 国内品种或未配置的，直接返回原价
    return price


def get_theoretical_price(
    foreign_symbol: str,
    foreign_price: float,
    exchange_rate: float
) -> float:
    """
    计算理论国内价格
    
    Args:
        foreign_symbol: 国际品种代码 (如 XAU, LME.CU)
        foreign_price: 国际价格
        exchange_rate: 汇率
    
    Returns:
        理论国内价格（单位与国内品种一致）
    """
    return convert_to_cny(foreign_symbol, foreign_price, exchange_rate)


def calculate_premium_rate(
    domestic_price: float,
    theoretical_price: float
) -> float:
    """
    计算溢价率
    
    公式: (实际国内价 - 理论价) / 理论价 × 100%
    
    Args:
        domestic_price: 实际国内价格
        theoretical_price: 理论国内价格
    
    Returns:
        溢价率（百分比）
    """
    if theoretical_price == 0:
        return 0
    
    return round((domestic_price - theoretical_price) / theoretical_price * 100, 4)


def calculate_gold_silver_ratio(gold_price: float, silver_price: float) -> float:
    """
    计算金银比
    
    Args:
        gold_price: 黄金价格 (USD/oz)
        silver_price: 白银价格 (USD/oz)
    
    Returns:
        金银比
    """
    if silver_price == 0:
        return 0
    return round(gold_price / silver_price, 2)


def calculate_copper_gold_ratio(copper_price: float, gold_price: float) -> float:
    """
    计算铜金比（经济温度计）
    
    Args:
        copper_price: 铜价 (USD/ton)
        gold_price: 黄金价格 (USD/oz)
    
    Returns:
        铜金比
    """
    if gold_price == 0:
        return 0
    return round(copper_price / gold_price, 4)
