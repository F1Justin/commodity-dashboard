"""
数据导出 API
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd
import io

from app.database import get_db, RealtimePrice, DailyOHLC, SpreadData, MacroData

router = APIRouter()


def create_csv_response(df: pd.DataFrame, filename: str) -> StreamingResponse:
    """创建 CSV 下载响应"""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


def create_excel_response(df: pd.DataFrame, filename: str) -> StreamingResponse:
    """创建 Excel 下载响应"""
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/export")
def export_data(
    type: str = Query(..., description="导出类型: snapshot, history, premium, macro"),
    format: str = Query("csv", description="格式: csv, xlsx"),
    symbols: Optional[str] = Query(None, description="品种代码，逗号分隔"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    导出数据为 CSV 或 Excel
    """
    # 解析日期
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=30)  # 默认30天
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "开始日期格式错误"}
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "结束日期格式错误"}
    
    # 解析品种列表
    symbol_list = symbols.split(",") if symbols else None
    
    df = pd.DataFrame()
    filename_prefix = ""
    
    if type == "snapshot":
        # 导出最新快照
        query = db.query(RealtimePrice)
        if symbol_list:
            query = query.filter(RealtimePrice.symbol.in_(symbol_list))
        
        # 获取每个品种的最新数据
        from sqlalchemy import func
        subquery = db.query(
            RealtimePrice.symbol,
            func.max(RealtimePrice.timestamp).label('max_ts')
        ).group_by(RealtimePrice.symbol).subquery()
        
        records = db.query(RealtimePrice).join(
            subquery,
            (RealtimePrice.symbol == subquery.c.symbol) & 
            (RealtimePrice.timestamp == subquery.c.max_ts)
        ).all()
        
        data = [{
            "品种代码": r.symbol,
            "品种名称": r.name,
            "价格": r.price,
            "人民币价格": r.price_cny,
            "单位": r.unit,
            "市场": r.market,
            "更新时间": r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else None
        } for r in records]
        
        df = pd.DataFrame(data)
        filename_prefix = "snapshot"
        
    elif type == "history":
        # 导出日K线历史
        query = db.query(DailyOHLC).filter(
            DailyOHLC.date >= start_dt.date(),
            DailyOHLC.date <= end_dt.date()
        )
        if symbol_list:
            query = query.filter(DailyOHLC.symbol.in_(symbol_list))
        
        records = query.order_by(DailyOHLC.date, DailyOHLC.symbol).all()
        
        data = [{
            "日期": r.date.strftime("%Y-%m-%d"),
            "品种代码": r.symbol,
            "品种名称": r.name,
            "开盘价": r.open,
            "最高价": r.high,
            "最低价": r.low,
            "收盘价": r.close,
            "成交量": r.volume
        } for r in records]
        
        df = pd.DataFrame(data)
        filename_prefix = "history"
        
    elif type == "premium":
        # 导出溢价率数据
        query = db.query(SpreadData).filter(
            SpreadData.timestamp >= start_dt,
            SpreadData.timestamp <= end_dt
        )
        
        records = query.order_by(SpreadData.timestamp, SpreadData.pair).all()
        
        data = [{
            "时间": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "品种对": r.pair,
            "名称": r.name,
            "国内价格": r.domestic_price,
            "国际价格": r.foreign_price,
            "理论价格": r.theoretical_price,
            "汇率": r.exchange_rate,
            "溢价率(%)": r.spread_rate
        } for r in records]
        
        df = pd.DataFrame(data)
        filename_prefix = "premium"
        
    elif type == "macro":
        # 导出宏观数据
        query = db.query(MacroData).filter(
            MacroData.date >= start_dt.date(),
            MacroData.date <= end_dt.date()
        )
        
        records = query.order_by(MacroData.date, MacroData.indicator).all()
        
        data = [{
            "日期": r.date.strftime("%Y-%m-%d"),
            "指标": r.indicator,
            "数值": r.value,
            "同比(%)": r.yoy_change,
            "环比(%)": r.mom_change
        } for r in records]
        
        df = pd.DataFrame(data)
        filename_prefix = "macro"
        
    else:
        return {"error": f"未知导出类型: {type}"}
    
    if df.empty:
        return {"error": "没有数据可导出"}
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "xlsx":
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        return create_excel_response(df, filename)
    else:
        filename = f"{filename_prefix}_{timestamp}.csv"
        return create_csv_response(df, filename)


@router.get("/export/types")
def get_export_types():
    """
    获取可导出的数据类型
    """
    return {
        "types": [
            {"id": "snapshot", "name": "实时快照", "description": "当前所有品种的最新价格"},
            {"id": "history", "name": "历史数据", "description": "指定品种、时间范围的日K线"},
            {"id": "premium", "name": "溢价率历史", "description": "溢价率计算器的历史记录"},
            {"id": "macro", "name": "宏观数据", "description": "CPI、汽柴油价格等"},
        ],
        "formats": [
            {"id": "csv", "name": "CSV", "description": "逗号分隔文件"},
            {"id": "xlsx", "name": "Excel", "description": "Excel 工作簿"},
        ]
    }
