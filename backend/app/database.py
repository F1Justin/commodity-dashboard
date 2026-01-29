"""
数据库配置与初始化
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.config import DATABASE_URL, DATABASE_PATH

# 创建引擎
engine = create_engine(DATABASE_URL, echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


class RealtimePrice(Base):
    """实时/分钟级价格数据"""
    __tablename__ = "realtime_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    symbol = Column(String(20), nullable=False)  # 如 'SHFE.AU', 'LME.CU'
    name = Column(String(50))  # 如 '沪金主力'
    price = Column(Float, nullable=False)
    price_cny = Column(Float)  # 换算后的人民币价格
    unit = Column(String(20))  # 原始单位
    market = Column(String(10))  # 'CN', 'INTL', 'LME'
    
    __table_args__ = (
        UniqueConstraint('timestamp', 'symbol', name='uix_realtime_ts_symbol'),
    )


class DailyOHLC(Base):
    """日K线数据"""
    __tablename__ = "daily_ohlc"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    symbol = Column(String(20), nullable=False)
    name = Column(String(50))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint('date', 'symbol', name='uix_daily_date_symbol'),
    )


class MacroData(Base):
    """宏观/低频数据（CPI、汽柴油价格等）"""
    __tablename__ = "macro_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    indicator = Column(String(50), nullable=False)  # 'CPI_CN', 'CPI_US', 'GASOLINE_CN'
    value = Column(Float)
    yoy_change = Column(Float)  # 同比变化
    mom_change = Column(Float)  # 环比变化
    
    __table_args__ = (
        UniqueConstraint('date', 'indicator', name='uix_macro_date_indicator'),
    )


class SpreadData(Base):
    """溢价率数据"""
    __tablename__ = "spread_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    pair = Column(String(50), nullable=False)  # 'GOLD', 'COPPER' 等
    name = Column(String(50))  # '黄金溢价率'
    domestic_price = Column(Float)  # 国内价格
    foreign_price = Column(Float)  # 国际价格（已换算单位）
    theoretical_price = Column(Float)  # 理论国内价格
    exchange_rate = Column(Float)  # 使用的汇率
    spread_rate = Column(Float)  # 溢价率 %
    
    __table_args__ = (
        UniqueConstraint('timestamp', 'pair', name='uix_spread_ts_pair'),
    )


class ExchangeRate(Base):
    """汇率数据"""
    __tablename__ = "exchange_rate"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    currency_pair = Column(String(10), nullable=False, default='USD/CNY')
    rate = Column(Float, nullable=False)
    source = Column(String(20))  # 'BOC' 或 'PBOC'
    
    __table_args__ = (
        UniqueConstraint('timestamp', 'currency_pair', name='uix_fx_ts_pair'),
    )


class RatioData(Base):
    """比值指标数据（金银比、铜金比等）"""
    __tablename__ = "ratio_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    ratio_type = Column(String(20), nullable=False)  # 'GOLD_SILVER', 'COPPER_GOLD'
    name = Column(String(50))
    value = Column(Float, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('timestamp', 'ratio_type', name='uix_ratio_ts_type'),
    )


def init_db():
    """初始化数据库，创建所有表"""
    # 确保数据目录存在
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print(f"✅ 数据库初始化完成: {DATABASE_PATH}")


def get_db():
    """获取数据库会话（用于依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
