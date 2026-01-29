"""
告警配置文件
修改此文件来控制告警行为，无需改动代码
敏感信息请配置在 .env 文件中
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（支持项目根目录和 backend 目录）
env_paths = [
    Path(__file__).parent.parent.parent.parent / ".env",  # 项目根目录
    Path(__file__).parent.parent.parent / ".env",         # backend 目录
    Path(".env"),                                          # 当前目录
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

# ==================== 告警开关 ====================
ALERT_ENABLED = {
    # 套利告警（溢价率异常）
    "arbitrage": False,          # 黄金/白银/铜溢价告警
    
    # 比值告警
    "ratio": False,              # 金银比、金油比告警
    
    # 崩盘告警（极端波动）
    "crash": True,               # 单日涨跌 > 4%
    "fx_crash": True,            # 汇率波动 > 1%
    
    # 系统告警
    "fetch_fail": True,          # 数据采集连续失败
    
    # 每日简报
    "daily_briefing": True,      # 8:30 / 15:30 简报
}

# ==================== QQ 机器人配置（从环境变量读取）====================
QQ_CONFIG = {
    "url": os.getenv("QQ_BOT_URL", "http://127.0.0.1:3000/send_group_msg"),
    "token": os.getenv("QQ_BOT_TOKEN", ""),
    "group_id": int(os.getenv("QQ_GROUP_ID", "0")),
    "at_user": os.getenv("QQ_AT_USER", ""),
}

# ==================== 告警阈值 ====================
THRESHOLDS = {
    # 套利告警阈值
    "gold_premium_high": 2.5,       # 黄金溢价 > 2.5%：国内抢金
    "gold_premium_low": -1.0,       # 黄金溢价 < -1%：买入机会
    "silver_premium_high": 10.0,    # 白银溢价 > 10%：国内白银疯了
    "copper_premium_low": -5.0,     # 铜溢价 < -5%：做多国内
    
    # 比值告警阈值
    "gold_silver_high": 85,         # 金银比 > 85：买银
    "gold_silver_low": 60,          # 金银比 < 60：银换金
    "gold_oil_high": 30,            # 金油比 > 30：买油
    "gold_oil_low": 15,             # 金油比 < 15：油太贵
    
    # 崩盘告警阈值
    "price_change_pct": 4.0,        # 单日涨跌 > 4%
    "fx_change_pct": 1.0,           # 汇率波动 > 1%（地震级）
    
    # 系统告警阈值
    "fetch_fail_count": 3,          # 连续失败次数
}

# ==================== 冷却时间（秒）====================
COOLDOWN = {
    "arbitrage": 4 * 3600,    # 套利告警：4小时
    "ratio": 8 * 3600,        # 比值告警：8小时
    "crash": 1 * 3600,        # 崩盘告警：1小时
    "default": 4 * 3600,
}

# ==================== 简报时间 ====================
BRIEFING_SCHEDULE = {
    "morning": "08:30",       # 早报
    # "afternoon": "15:30",     # 午后
    # "night": "23:30",       # 夜报（可选，取消注释启用）
}
