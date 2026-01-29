# 大宗商品战情室

全球大宗商品价格追踪与溢价率分析系统。

## 功能特性

- **实时价格追踪**: 国内期货(上期所、大商所、郑商所、上海能源)、国际期货(LME、COMEX、NYMEX、CBOT)
- **溢价率计算器**: 自动计算黄金、白银、铜、铝的内外价差溢价率
- **比值指标**: 金银比、铜金比(经济温度计)
- **归一化图表**: 贵金属、有色金属、能源、农产品分组对比
- **宏观数据**: 中美CPI对比、国内汽柴油零售价
- **数据导出**: 支持 CSV 和 Excel 格式

## 技术栈

- **后端**: Python FastAPI + APScheduler + SQLite
- **前端**: Next.js + React + TypeScript + TailwindCSS + ECharts
- **数据源**: AkShare

## 快速开始

### 方式一: Docker 部署 (推荐)

```bash
# 克隆项目
cd 大宗战情室

# 一键启动
docker-compose up -d

# 访问
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000
```

### 方式二: 本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目结构

```
大宗战情室/
├── backend/                    # 后端 FastAPI
│   ├── app/
│   │   ├── main.py            # 应用入口
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库模型
│   │   ├── scheduler.py       # 定时任务
│   │   ├── api/               # API 路由
│   │   ├── fetchers/          # 数据采集器
│   │   └── calculator/        # 溢价率计算
│   ├── data/                  # SQLite 数据库
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端 Next.js
│   ├── src/
│   │   ├── pages/             # 页面
│   │   ├── components/        # 组件
│   │   └── lib/               # 工具函数
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## API 接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/snapshot` | GET | 获取所有品种最新价格 |
| `/api/calculator` | GET | 获取溢价率计算结果 |
| `/api/normalized` | GET | 获取归一化图表数据 |
| `/api/macro/cpi` | GET | 获取 CPI 数据 |
| `/api/export` | GET | 导出数据 |

## 追踪品种

### 贵金属
- 沪金主力 (SHFE.AU)
- 沪银主力 (SHFE.AG)
- 伦敦金 (XAU)
- 伦敦银 (XAG)

### 有色金属
- 沪铜主力 (SHFE.CU)
- 沪铝主力 (SHFE.AL)
- LME铜
- LME铝

### 能源
- INE原油主力 (INE.SC)
- 布伦特原油 (BRENT)
- 天然气 (NG)
- PTA (CZCE.TA)
- 甲醇 (CZCE.MA)

### 农产品
- 豆粕主力 (DCE.M)
- 玉米主力 (DCE.C)
- 生猪主力 (DCE.LH)
- CBOT大豆
- CBOT玉米

### 宏观数据
- 中国 CPI
- 美国 CPI
- 国内汽柴油零售价

## 溢价率计算公式

```
理论沪金价 = 伦敦金(USD/oz) ÷ 31.1035 × 汇率
溢价率 = (实际沪金 - 理论沪金) ÷ 理论沪金 × 100%
```

### 信号解读

| 指标 | 阈值 | 信号 | 解读 |
|------|------|------|------|
| 黄金溢价率 | > +2% | 红灯 | 国内抢金，恐慌情绪 |
| 黄金溢价率 | < -2% | 绿灯 | 国内金价偏低 |
| 铜溢价率 | < -5% | 绿灯 | 国内铜便宜，做多机会 |
| 金银比 | > 80 | 警示 | 避险情绪高，白银被低估 |
| 金银比 | < 60 | 警示 | 白银可能被高估 |
| 铜金比 | ↑ | - | 经济预期改善 |
| 铜金比 | ↓ | - | 避险情绪升温 |

## 数据更新频率

- **实时价格**: 交易时段每分钟
- **日K线**: 每天 16:00
- **汇率**: 每小时
- **宏观数据**: 每月 15 日

## 许可证

MIT License
