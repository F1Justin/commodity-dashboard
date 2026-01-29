"""
告警通知模块 - 通过 QQ 群消息通知
配置文件: alert_config.py
"""
import requests
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# 从配置文件导入
from app.alert_config import (
    ALERT_ENABLED,
    QQ_CONFIG,
    THRESHOLDS,
    COOLDOWN,
)


class AlertType(Enum):
    OPPORTUNITY = "💰"      # 套利机会
    ROTATION = "🔄"         # 换仓信号
    CRASH = "🚨"            # 崩盘预警
    INFO = "📊"             # 简报信息
    SYSTEM = "⚙️"           # 系统告警


@dataclass
class Alert:
    alert_type: AlertType
    title: str
    data_lines: List[str]
    suggestion: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


# 状态追踪
_alert_history: Dict[str, datetime] = {}
_fetch_fail_counts: Dict[str, int] = {}
_last_prices: Dict[str, float] = {}  # 用于计算涨跌幅


def _should_send(alert_key: str, cooldown_type: str = "default") -> bool:
    """检查冷却时间"""
    last = _alert_history.get(alert_key)
    if last is None:
        return True
    elapsed = (datetime.now() - last).total_seconds()
    return elapsed >= COOLDOWN.get(cooldown_type, COOLDOWN["default"])


def _record_sent(alert_key: str):
    """记录发送时间"""
    _alert_history[alert_key] = datetime.now()


def _format_message(alert: Alert) -> str:
    """格式化告警消息"""
    time_str = alert.timestamp.strftime("%H:%M")
    
    lines = [
        f"{alert.alert_type.value}【{alert.title}】",
        f"⏰ {time_str}",
        "----------------",
    ]
    lines.extend(alert.data_lines)
    
    if alert.suggestion:
        lines.append("----------------")
        lines.append(f"💡 {alert.suggestion}")
    
    return "\n".join(lines)


def send_qq_message(text: str, at_user: bool = True) -> bool:
    """发送 QQ 群消息"""
    try:
        if at_user:
            # at 放在消息最后
            message = [
                {"type": "text", "data": {"text": text + "\n\n"}},
                {"type": "at", "data": {"qq": QQ_CONFIG["at_user"]}}
            ]
        else:
            message = text
        
        response = requests.post(
            QQ_CONFIG["url"],
            headers={
                "Authorization": f"Bearer {QQ_CONFIG['token']}",
                "Content-Type": "application/json"
            },
            json={"group_id": QQ_CONFIG["group_id"], "message": message},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False


def send_alert(alert: Alert) -> bool:
    """发送告警"""
    text = _format_message(alert)
    return send_qq_message(text)


# ==================== 告警检查函数 ====================

def check_arbitrage_alerts(calc_data: dict) -> List[Alert]:
    """
    检查套利告警
    - 黄金溢价
    - 白银溢价
    - 铜溢价
    """
    # 检查开关
    if not ALERT_ENABLED.get("arbitrage", False):
        return []
    
    alerts = []
    
    # 黄金溢价
    gold = calc_data.get("gold", {})
    gold_prem = gold.get("premium_rate")
    if gold_prem is not None:
        if gold_prem > THRESHOLDS["gold_premium_high"]:
            key = "gold_prem_high"
            if _should_send(key, "arbitrage"):
                alerts.append(Alert(
                    alert_type=AlertType.OPPORTUNITY,
                    title="黄金溢价过高",
                    data_lines=[
                        f"⚠️ 沪金溢价率: +{gold_prem:.1f}%",
                        f"📊 沪金: {gold.get('shfe_cny_g', 0):.2f} 元/克",
                        f"🌍 伦敦金: ${gold.get('london_usd_oz', 0):.0f}/oz",
                    ],
                    suggestion="国内在抢金，持有者别急着卖！"
                ))
                _record_sent(key)
        
        elif gold_prem < THRESHOLDS["gold_premium_low"]:
            key = "gold_prem_low"
            if _should_send(key, "arbitrage"):
                alerts.append(Alert(
                    alert_type=AlertType.OPPORTUNITY,
                    title="黄金折价，买入机会",
                    data_lines=[
                        f"✅ 沪金溢价率: {gold_prem:.1f}%",
                        f"📊 沪金: {gold.get('shfe_cny_g', 0):.2f} 元/克",
                        f"🌍 伦敦金: ${gold.get('london_usd_oz', 0):.0f}/oz",
                    ],
                    suggestion="国内金价便宜，可考虑买入！"
                ))
                _record_sent(key)
    
    # 白银溢价
    silver = calc_data.get("silver", {})
    silver_prem = silver.get("premium_rate")
    if silver_prem is not None:
        if silver_prem > THRESHOLDS["silver_premium_high"]:
            key = "silver_prem_high"
            if _should_send(key, "arbitrage"):
                alerts.append(Alert(
                    alert_type=AlertType.OPPORTUNITY,
                    title="白银溢价过高！",
                    data_lines=[
                        f"⚠️ 沪银溢价率: +{silver_prem:.1f}% (异常)",
                        f"📊 沪银: {silver.get('shfe_cny_kg', 0):.0f} 元/kg",
                        f"🌍 伦敦银: ${silver.get('london_usd_oz', 0):.2f}/oz",
                    ],
                    suggestion="国内价格虚高，切勿追涨！持有者可考虑止盈。"
                ))
                _record_sent(key)
    
    # 铜溢价
    copper = calc_data.get("copper", {})
    copper_prem = copper.get("premium_rate")
    if copper_prem is not None:
        if copper_prem < THRESHOLDS["copper_premium_low"]:
            key = "copper_prem_low"
            if _should_send(key, "arbitrage"):
                alerts.append(Alert(
                    alert_type=AlertType.OPPORTUNITY,
                    title="铜折价，做多机会",
                    data_lines=[
                        f"✅ 沪铜溢价率: {copper_prem:.1f}%",
                        f"📊 沪铜: {copper.get('shfe_cny_ton', 0):.0f} 元/吨",
                        f"🌍 LME铜: ${copper.get('lme_usd_ton', 0):.0f}/ton",
                    ],
                    suggestion="国内铜价太便宜，早晚补涨，可做多！"
                ))
                _record_sent(key)
    
    return alerts


def check_ratio_alerts(calc_data: dict, prices: dict) -> List[Alert]:
    """
    检查比值告警
    - 金银比
    - 金油比
    """
    # 检查开关
    if not ALERT_ENABLED.get("ratio", False):
        return []
    
    alerts = []
    ratios = calc_data.get("ratios", {})
    
    # 金银比
    gs_ratio = ratios.get("gold_silver")
    if gs_ratio is not None:
        if gs_ratio > THRESHOLDS["gold_silver_high"]:
            key = "gs_ratio_high"
            if _should_send(key, "ratio"):
                alerts.append(Alert(
                    alert_type=AlertType.ROTATION,
                    title="金银比过高",
                    data_lines=[
                        f"⚖️ 当前金银比: {gs_ratio:.1f}",
                        f"(触及{THRESHOLDS['gold_silver_high']}上方警戒线)",
                    ],
                    suggestion="白银相对黄金太便宜，可买银！"
                ))
                _record_sent(key)
        
        elif gs_ratio < THRESHOLDS["gold_silver_low"]:
            key = "gs_ratio_low"
            if _should_send(key, "ratio"):
                alerts.append(Alert(
                    alert_type=AlertType.ROTATION,
                    title="金银比触底",
                    data_lines=[
                        f"⚖️ 当前金银比: {gs_ratio:.1f}",
                        f"(触及{THRESHOLDS['gold_silver_low']}下方警戒线)",
                    ],
                    suggestion="白银相对黄金过热，卖银买金(防御)！"
                ))
                _record_sent(key)
    
    # 金油比（需要油价）
    gold_price = prices.get("XAU")
    oil_price = prices.get("BRENT") or prices.get("INE.SC")
    if gold_price and oil_price:
        go_ratio = gold_price / oil_price
        
        if go_ratio > THRESHOLDS["gold_oil_high"]:
            key = "go_ratio_high"
            if _should_send(key, "ratio"):
                alerts.append(Alert(
                    alert_type=AlertType.ROTATION,
                    title="金油比过高",
                    data_lines=[
                        f"⚖️ 当前金油比: {go_ratio:.1f}",
                        f"📊 伦敦金: ${gold_price:.0f}",
                        f"🛢 布伦特: ${oil_price:.1f}",
                    ],
                    suggestion="油价相对金价太便宜，可买油/能源ETF！"
                ))
                _record_sent(key)
        
        elif go_ratio < THRESHOLDS["gold_oil_low"]:
            key = "go_ratio_low"
            if _should_send(key, "ratio"):
                alerts.append(Alert(
                    alert_type=AlertType.ROTATION,
                    title="金油比过低",
                    data_lines=[
                        f"⚖️ 当前金油比: {go_ratio:.1f}",
                        f"📊 伦敦金: ${gold_price:.0f}",
                        f"🛢 布伦特: ${oil_price:.1f}",
                    ],
                    suggestion="油价太贵，可能有战争溢价，警惕回调！"
                ))
                _record_sent(key)
    
    return alerts


def check_crash_alerts(prices: dict, changes: dict) -> List[Alert]:
    """
    检查极端波动告警
    - 单日暴涨/暴跌 > 4%
    """
    # 检查开关
    if not ALERT_ENABLED.get("crash", False):
        return []
    
    alerts = []
    
    # 品种名称映射
    name_map = {
        "XAU": "伦敦金", "XAG": "伦敦银",
        "SHFE.AU": "沪金", "SHFE.AG": "沪银",
        "SHFE.CU": "沪铜", "LME.CU": "LME铜",
        "BRENT": "布伦特", "INE.SC": "INE原油",
        "DCE.M": "豆粕", "DCE.C": "玉米",
    }
    
    for symbol, change in changes.items():
        if abs(change) >= THRESHOLDS["price_change_pct"]:
            key = f"crash_{symbol}"
            if _should_send(key, "crash"):
                price = prices.get(symbol, 0)
                name = name_map.get(symbol, symbol)
                direction = "暴涨" if change > 0 else "暴跌"
                emoji = "📈" if change > 0 else "📉"
                
                alerts.append(Alert(
                    alert_type=AlertType.CRASH,
                    title=f"{name}{direction}",
                    data_lines=[
                        f"{emoji} {name}: {price:.2f} ({change:+.1f}%)",
                    ],
                    suggestion="极端波动，注意风险！"
                ))
                _record_sent(key)
    
    return alerts


def check_fx_alert(fx_rate: float, prev_fx_rate: float) -> Optional[Alert]:
    """检查汇率波动告警"""
    # 检查开关
    if not ALERT_ENABLED.get("fx_crash", False):
        return None
    
    if prev_fx_rate is None or prev_fx_rate == 0:
        return None
    
    change = (fx_rate - prev_fx_rate) / prev_fx_rate * 100
    
    if abs(change) >= THRESHOLDS["fx_change_pct"]:
        key = "fx_crash"
        if _should_send(key, "crash"):
            direction = "大涨" if change > 0 else "大跌"
            _record_sent(key)
            return Alert(
                alert_type=AlertType.CRASH,
                title=f"汇率{direction}！",
                data_lines=[
                    f"💵 USD/CNY: {fx_rate:.4f} ({change:+.2f}%)",
                    "(汇率1%波动=地震级别)",
                ],
                suggestion="汇率剧烈波动，检查所有溢价率！"
            )
    return None


# ==================== 综合检查入口 ====================

def check_all_alerts(calc_data: dict, prices: dict = None, changes: dict = None):
    """
    综合检查所有告警条件
    在每次溢价率计算后调用
    """
    all_alerts = []
    
    # 1. 套利告警
    all_alerts.extend(check_arbitrage_alerts(calc_data))
    
    # 2. 比值告警
    if prices:
        all_alerts.extend(check_ratio_alerts(calc_data, prices))
    
    # 3. 极端波动告警
    if prices and changes:
        all_alerts.extend(check_crash_alerts(prices, changes))
    
    # 发送所有告警
    for alert in all_alerts:
        send_alert(alert)
    
    return all_alerts


# ==================== 每日简报 ====================

def generate_daily_briefing(calc_data: dict, prices: dict = None) -> str:
    """
    生成每日战情简报
    """
    today = date.today().strftime("%Y/%m/%d")
    
    gold = calc_data.get("gold", {})
    silver = calc_data.get("silver", {})
    copper = calc_data.get("copper", {})
    ratios = calc_data.get("ratios", {})
    fx = calc_data.get("exchange_rate", 0)
    
    # 获取价格
    gold_price = gold.get("london_usd_oz", 0)
    silver_price = silver.get("london_usd_oz", 0)
    oil_price = prices.get("BRENT", 0) if prices else 0
    
    # 溢价率状态
    def prem_status(prem, high_th, low_th=None):
        if prem is None:
            return "N/A", "❓"
        if prem > high_th:
            return f"+{prem:.1f}%", "⚠️"
        elif low_th and prem < low_th:
            return f"{prem:.1f}%", "✅"
        return f"{prem:+.1f}%", "✅"
    
    gold_prem_str, gold_icon = prem_status(gold.get("premium_rate"), 2.5, -1.0)
    silver_prem_str, silver_icon = prem_status(silver.get("premium_rate"), 10.0)
    copper_prem_str, copper_icon = prem_status(copper.get("premium_rate"), 5.0, -5.0)
    
    # 金银比状态
    gs = ratios.get("gold_silver", 0)
    if gs > 85:
        gs_comment = "买银"
    elif gs < 60:
        gs_comment = "银换金"
    else:
        gs_comment = "正常"
    
    # 金油比
    go_ratio = gold_price / oil_price if oil_price > 0 else 0
    
    # 构建简报
    lines = [
        f"📅【战情简报】{today}",
        "",
        "1️⃣ 核心指标",
        f"💵 汇率: {fx:.4f}",
        f"🏆 伦敦金: ${gold_price:.0f}",
        f"🪙 伦敦银: ${silver_price:.2f}",
        f"🛢 布伦特: ${oil_price:.1f}" if oil_price else "🛢 布伦特: N/A",
        "",
        "2️⃣ 溢价率监控",
        f"{gold_icon} 沪金: {gold_prem_str}",
        f"{silver_icon} 沪银: {silver_prem_str}",
        f"{copper_icon} 沪铜: {copper_prem_str}",
        "",
        "3️⃣ 比值指标",
        f"⚖️ 金银比: {gs:.1f} ({gs_comment})",
        f"⚖️ 金油比: {go_ratio:.1f}" if go_ratio else "⚖️ 金油比: N/A",
        "",
        "4️⃣ 策略提示",
    ]
    
    # 生成策略建议
    tips = []
    if gold.get("premium_rate", 0) > 2.5:
        tips.append("🔴 黄金溢价高，国内持有者别急卖")
    if silver.get("premium_rate", 0) > 10:
        tips.append("🔴 白银溢价极高，切勿追涨")
    if copper.get("premium_rate", 0) < -5:
        tips.append("🟢 铜折价明显，可做多国内铜")
    if gs > 85:
        tips.append("🟢 金银比高，白银被低估，可买银")
    if go_ratio > 30:
        tips.append("🟢 金油比高，油价便宜，可定投能源ETF")
    
    if not tips:
        tips.append("✅ 各指标正常，无明显机会")
    
    lines.extend(tips)
    lines.append("")
    lines.append("自动生成 by 忠实的莉莉白")
    
    return "\n".join(lines)


def send_daily_briefing(calc_data: dict, prices: dict = None):
    """发送每日简报"""
    # 检查开关
    if not ALERT_ENABLED.get("daily_briefing", False):
        print("📊 每日简报已关闭")
        return False
    
    text = generate_daily_briefing(calc_data, prices)
    return send_qq_message(text)


# ==================== 系统告警 ====================

def record_fetch_failure(source: str):
    """记录采集失败"""
    _fetch_fail_counts[source] = _fetch_fail_counts.get(source, 0) + 1
    
    # 检查开关
    if not ALERT_ENABLED.get("fetch_fail", False):
        return
    
    if _fetch_fail_counts[source] >= THRESHOLDS.get("fetch_fail_count", 3):
        key = f"fetch_fail_{source}"
        if _should_send(key, "default"):
            alert = Alert(
                alert_type=AlertType.SYSTEM,
                title="数据采集故障",
                data_lines=[
                    f"❌ 数据源: {source}",
                    f"❌ 连续失败: {_fetch_fail_counts[source]}次",
                ],
                suggestion="系统可能无法获取行情，请检查！"
            )
            send_alert(alert)
            _record_sent(key)


def record_fetch_success(source: str):
    """记录采集成功"""
    _fetch_fail_counts[source] = 0


def send_test_alert() -> bool:
    """测试告警"""
    alert = Alert(
        alert_type=AlertType.INFO,
        title="告警系统测试",
        data_lines=["✅ 系统连接正常"],
        suggestion="这是一条测试消息"
    )
    return send_alert(alert)
