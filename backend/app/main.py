"""
大宗商品战情室 - FastAPI 主入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_PREFIX
from app.scheduler import start_scheduler, shutdown_scheduler
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("🚀 大宗商品战情室启动中...")
    init_db()
    start_scheduler()
    print("✅ 服务启动完成")
    
    yield
    
    # 关闭时
    print("🛑 正在关闭服务...")
    shutdown_scheduler()
    print("👋 服务已关闭")


app = FastAPI(
    title="大宗商品战情室",
    description="全球大宗商品价格追踪与溢价率分析系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置 - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.api import snapshot, calculator, normalized, export, macro, admin

app.include_router(snapshot.router, prefix=API_PREFIX, tags=["实时数据"])
app.include_router(calculator.router, prefix=API_PREFIX, tags=["溢价率计算器"])
app.include_router(normalized.router, prefix=API_PREFIX, tags=["归一化图表"])
app.include_router(export.router, prefix=API_PREFIX, tags=["数据导出"])
app.include_router(macro.router, prefix=API_PREFIX, tags=["宏观数据"])
app.include_router(admin.router, prefix=API_PREFIX, tags=["管理"])


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "running",
        "name": "大宗商品战情室",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """API 健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
