"""
宏观数据采集器 - CPI、汽柴油价格等
"""
from datetime import datetime, date
from typing import List, Dict
import akshare as ak

from app.database import SessionLocal, MacroData


def fetch_china_cpi() -> List[dict]:
    """
    获取中国 CPI 数据
    """
    data = []
    try:
        df = ak.macro_china_cpi_monthly()
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                # 解析日期（格式如 "2024年01月"）
                date_str = str(row.get('月份') or row.get('统计时间', ''))
                try:
                    if '年' in date_str and '月' in date_str:
                        year = int(date_str.split('年')[0])
                        month = int(date_str.split('年')[1].replace('月', ''))
                        record_date = date(year, month, 1)
                    else:
                        continue
                except:
                    continue
                
                data.append({
                    "date": record_date,
                    "indicator": "CPI_CN",
                    "value": float(row.get('全国当月', 0) or row.get('同比', 0)),
                    "yoy_change": float(row.get('全国当月', 0) or row.get('同比', 0)),
                    "mom_change": float(row.get('全国环比', 0) or row.get('环比', 0)) if '全国环比' in row or '环比' in row else None,
                })
    except Exception as e:
        print(f"获取中国CPI数据失败: {e}")
    
    return data


def fetch_us_cpi() -> List[dict]:
    """
    获取美国 CPI 数据
    """
    data = []
    try:
        df = ak.macro_usa_cpi_monthly()
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                # 解析日期
                date_val = row.get('日期') or row.get('date')
                if isinstance(date_val, str):
                    try:
                        record_date = datetime.strptime(date_val, "%Y-%m-%d").date()
                    except:
                        continue
                elif isinstance(date_val, date):
                    record_date = date_val
                else:
                    continue
                
                data.append({
                    "date": record_date,
                    "indicator": "CPI_US",
                    "value": float(row.get('今值', 0) or row.get('value', 0)),
                    "yoy_change": float(row.get('今值', 0) or row.get('value', 0)),
                    "mom_change": None,
                })
    except Exception as e:
        print(f"获取美国CPI数据失败: {e}")
    
    return data


def fetch_oil_retail_price() -> List[dict]:
    """
    获取国内汽柴油零售价
    """
    data = []
    try:
        df = ak.energy_oil_hist()
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                # 解析日期
                date_val = row.get('日期') or row.get('date')
                if isinstance(date_val, str):
                    try:
                        record_date = datetime.strptime(date_val, "%Y-%m-%d").date()
                    except:
                        continue
                elif isinstance(date_val, date):
                    record_date = date_val
                else:
                    continue
                
                # 汽油价格
                gasoline_price = row.get('汽油价格') or row.get('92号汽油')
                if gasoline_price:
                    data.append({
                        "date": record_date,
                        "indicator": "GASOLINE_CN",
                        "value": float(gasoline_price),
                        "yoy_change": None,
                        "mom_change": None,
                    })
                
                # 柴油价格
                diesel_price = row.get('柴油价格') or row.get('0号柴油')
                if diesel_price:
                    data.append({
                        "date": record_date,
                        "indicator": "DIESEL_CN",
                        "value": float(diesel_price),
                        "yoy_change": None,
                        "mom_change": None,
                    })
                    
    except Exception as e:
        print(f"获取汽柴油价格失败: {e}")
    
    return data


def save_macro_data(data: List[dict]):
    """
    保存宏观数据
    """
    if not data:
        return
    
    db = SessionLocal()
    try:
        for item in data:
            # 检查是否已存在
            existing = db.query(MacroData).filter(
                MacroData.indicator == item["indicator"],
                MacroData.date == item["date"]
            ).first()
            
            if existing:
                # 更新
                existing.value = item["value"]
                existing.yoy_change = item.get("yoy_change")
                existing.mom_change = item.get("mom_change")
            else:
                # 新增
                record = MacroData(
                    date=item["date"],
                    indicator=item["indicator"],
                    value=item["value"],
                    yoy_change=item.get("yoy_change"),
                    mom_change=item.get("mom_change")
                )
                db.add(record)
        
        db.commit()
        print(f"✅ 已保存 {len(data)} 条宏观数据")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 保存宏观数据失败: {e}")
    finally:
        db.close()


def update_macro_data():
    """
    更新所有宏观数据
    """
    # 中国 CPI
    cn_cpi = fetch_china_cpi()
    save_macro_data(cn_cpi)
    print(f"📊 中国CPI: {len(cn_cpi)} 条")
    
    # 美国 CPI
    us_cpi = fetch_us_cpi()
    save_macro_data(us_cpi)
    print(f"📊 美国CPI: {len(us_cpi)} 条")
    
    # 汽柴油价格
    oil_prices = fetch_oil_retail_price()
    save_macro_data(oil_prices)
    print(f"📊 汽柴油价格: {len(oil_prices)} 条")
    
    print("📊 宏观数据更新完成")
