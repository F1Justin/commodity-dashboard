/**
 * 数据导出页面 - 包含简报生成功能
 */
import Head from 'next/head';
import { useState, useEffect } from 'react';
import { exportData, getSnapshot, getCalculatorData } from '@/lib/api';
import {
  Download,
  FileSpreadsheet,
  FileText,
  Clock,
  Database,
  TrendingUp,
  Globe2,
  Info,
  Check,
  Copy,
  FileCode,
  RefreshCw,
} from 'lucide-react';

const exportTypes = [
  { id: 'snapshot', name: '实时快照', description: '当前所有品种的最新价格', icon: Clock },
  { id: 'history', name: '历史数据', description: '指定品种、时间范围的日K线', icon: Database },
  { id: 'premium', name: '溢价率历史', description: '溢价率计算器的历史记录', icon: TrendingUp },
  { id: 'macro', name: '宏观数据', description: 'CPI、汽柴油价格等', icon: Globe2 },
];

const formats = [
  { id: 'csv', name: 'CSV', description: '逗号分隔文件', icon: FileText },
  { id: 'xlsx', name: 'Excel', description: 'Excel 工作簿', icon: FileSpreadsheet },
];

const symbolOptions = [
  { value: '', label: '全部品种' },
  { value: 'SHFE.AU,SHFE.AG', label: '贵金属（沪金、沪银）' },
  { value: 'SHFE.CU,SHFE.AL', label: '有色金属（沪铜、沪铝）' },
  { value: 'INE.SC,BRENT', label: '能源（原油）' },
  { value: 'DCE.M,DCE.C,DCE.LH', label: '农产品（豆粕、玉米、生猪）' },
];

// 生成简报文本
function generateBriefing(snapshot: any, calculator: any): string {
  const now = new Date().toLocaleString('zh-CN', { 
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false
  });
  
  let text = `# 大宗商品战情室 - 当前状况简报\n`;
  text += `生成时间: ${now}\n\n`;
  
  // 汇率
  if (calculator?.exchange_rate) {
    text += `## 汇率\n`;
    text += `USD/CNY: ${calculator.exchange_rate.toFixed(4)}\n\n`;
  }
  
  // 贵金属
  text += `## 贵金属\n`;
  if (calculator?.gold) {
    text += `黄金:\n`;
    text += `  - 伦敦金: ${calculator.gold.london_usd_oz?.toFixed(2)} USD/oz\n`;
    text += `  - 沪金: ${calculator.gold.shfe_cny_g?.toFixed(2)} CNY/g\n`;
    text += `  - 理论价: ${calculator.gold.theoretical_cny_g?.toFixed(2)} CNY/g\n`;
    text += `  - 溢价率: ${calculator.gold.premium_rate?.toFixed(2)}%\n`;
  }
  if (calculator?.silver) {
    text += `白银:\n`;
    text += `  - 伦敦银: ${calculator.silver.london_usd_oz?.toFixed(2)} USD/oz\n`;
    text += `  - 沪银: ${calculator.silver.shfe_cny_kg?.toFixed(0)} CNY/kg\n`;
    text += `  - 理论价: ${calculator.silver.theoretical_cny_kg?.toFixed(0)} CNY/kg\n`;
    text += `  - 溢价率: ${calculator.silver.premium_rate?.toFixed(2)}%\n`;
  }
  text += `\n`;
  
  // 有色金属
  text += `## 有色金属\n`;
  if (calculator?.copper) {
    text += `铜:\n`;
    text += `  - LME铜: ${calculator.copper.lme_usd_ton?.toFixed(2)} USD/ton\n`;
    text += `  - 沪铜: ${calculator.copper.shfe_cny_ton?.toFixed(0)} CNY/ton\n`;
    text += `  - 理论价: ${calculator.copper.theoretical_cny_ton?.toFixed(0)} CNY/ton\n`;
    text += `  - 溢价率: ${calculator.copper.premium_rate?.toFixed(2)}%\n`;
  }
  if (calculator?.aluminum) {
    text += `铝:\n`;
    text += `  - LME铝: ${calculator.aluminum.lme_usd_ton?.toFixed(2)} USD/ton\n`;
    text += `  - 沪铝: ${calculator.aluminum.shfe_cny_ton?.toFixed(0)} CNY/ton\n`;
    text += `  - 理论价: ${calculator.aluminum.theoretical_cny_ton?.toFixed(0)} CNY/ton\n`;
    text += `  - 溢价率: ${calculator.aluminum.premium_rate?.toFixed(2)}%\n`;
  }
  text += `\n`;
  
  // 能源
  text += `## 能源\n`;
  const data = snapshot?.data || {};
  if (data['INE.SC']) {
    text += `INE原油: ${data['INE.SC'].price?.toFixed(2)} CNY/桶\n`;
  }
  if (data['BRENT']) {
    text += `布伦特原油: ${data['BRENT'].price?.toFixed(2)} USD/桶\n`;
  }
  if (data['NG']) {
    text += `天然气: ${data['NG'].price?.toFixed(3)} USD/mmBtu\n`;
  }
  text += `\n`;
  
  // 农产品
  text += `## 农产品\n`;
  if (data['DCE.M']) {
    text += `豆粕: ${data['DCE.M'].price?.toFixed(0)} CNY/ton\n`;
  }
  if (data['DCE.C']) {
    text += `玉米: ${data['DCE.C'].price?.toFixed(0)} CNY/ton\n`;
  }
  if (data['DCE.LH']) {
    text += `生猪: ${data['DCE.LH'].price?.toFixed(0)} CNY/ton\n`;
  }
  if (data['CBOT.S']) {
    text += `CBOT大豆: ${data['CBOT.S'].price?.toFixed(2)} USD/蒲式耳\n`;
  }
  if (data['CBOT.C']) {
    text += `CBOT玉米: ${data['CBOT.C'].price?.toFixed(2)} USD/蒲式耳\n`;
  }
  text += `\n`;
  
  // 比值指标
  text += `## 比值指标\n`;
  if (calculator?.ratios) {
    text += `金银比: ${calculator.ratios.gold_silver?.toFixed(2)}\n`;
    text += `铜金比: ${calculator.ratios.copper_gold?.toFixed(4)}\n`;
  }
  text += `\n`;
  
  // 交易信号
  text += `## 交易信号\n`;
  if (calculator?.signals) {
    const s = calculator.signals;
    text += `黄金溢价: ${s.gold_premium === 'normal' ? '正常' : s.gold_premium === 'high' ? '偏高' : s.gold_premium === 'low' ? '偏低' : s.gold_premium} - ${s.gold_premium_message || ''}\n`;
    text += `铜溢价: ${s.copper_premium === 'normal' ? '正常' : s.copper_premium === 'high' ? '偏高' : s.copper_premium === 'low' ? '偏低' : s.copper_premium} - ${s.copper_premium_message || ''}\n`;
    text += `金银比: ${s.gold_silver_ratio === 'normal' ? '正常' : s.gold_silver_ratio} - ${s.gold_silver_message || ''}\n`;
    text += `经济情绪: ${s.economic_sentiment === 'neutral' ? '中性' : s.economic_sentiment} - ${s.economic_message || ''}\n`;
  }
  text += `\n`;
  
  // 完整价格表
  text += `## 完整价格表\n`;
  text += `| 品种 | 价格 | 单位 | 市场 |\n`;
  text += `|------|------|------|------|\n`;
  Object.values(data).forEach((item: any) => {
    if (item?.price) {
      text += `| ${item.name} | ${typeof item.price === 'number' ? item.price.toFixed(2) : item.price} | ${item.unit} | ${item.market} |\n`;
    }
  });
  
  return text;
}

export default function Export() {
  const [selectedType, setSelectedType] = useState('snapshot');
  const [selectedFormat, setSelectedFormat] = useState('csv');
  const [selectedSymbols, setSelectedSymbols] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  
  // 简报相关状态
  const [briefing, setBriefing] = useState<string>('');
  const [briefingLoading, setBriefingLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // 加载简报数据
  const loadBriefing = async () => {
    setBriefingLoading(true);
    try {
      const [snapshotRes, calculatorRes] = await Promise.all([
        getSnapshot(),
        getCalculatorData(),
      ]);
      const text = generateBriefing(snapshotRes, calculatorRes);
      setBriefing(text);
    } catch (e) {
      console.error('Failed to load briefing:', e);
      setBriefing('加载失败，请检查后端服务是否运行');
    } finally {
      setBriefingLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadBriefing();
  }, []);

  // 复制简报
  const copyBriefing = async () => {
    try {
      await navigator.clipboard.writeText(briefing);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Failed to copy:', e);
    }
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      exportData(
        selectedType,
        selectedFormat,
        selectedSymbols || undefined,
        startDate || undefined,
        endDate || undefined
      );
    } finally {
      setTimeout(() => setIsExporting(false), 1000);
    }
  };

  const needsDateRange = ['history', 'premium', 'macro'].includes(selectedType);
  const needsSymbols = ['history'].includes(selectedType);

  return (
    <>
      <Head>
        <title>数据导出 - 大宗商品战情室</title>
      </Head>

      <div className="space-y-6">
        {/* 页面标题 */}
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Download className="w-7 h-7 text-primary-400" />
            数据导出
          </h1>
          <p className="text-gray-500 mt-1">导出数据或生成简报</p>
        </div>

        {/* 当前状况简报 */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileCode className="w-5 h-5 text-primary-400" />
              <h3 className="font-semibold text-white">当前状况简报</h3>
              <span className="text-xs text-gray-500">（文字版，可直接复制给 LLM）</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={loadBriefing}
                disabled={briefingLoading}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-[#1a1f2e] text-gray-300 rounded-lg hover:bg-[#242d3a] border border-[#2a3441] transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${briefingLoading ? 'animate-spin' : ''}`} />
                刷新
              </button>
              <button
                onClick={copyBriefing}
                disabled={!briefing || briefingLoading}
                className={`flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg transition-colors ${
                  copied
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'bg-primary-500 text-white hover:bg-primary-600'
                }`}
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4" />
                    已复制
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    复制全部
                  </>
                )}
              </button>
            </div>
          </div>
          
          {/* 简报内容 */}
          <div className="relative">
            <textarea
              readOnly
              value={briefingLoading ? '加载中...' : briefing}
              className="w-full h-[400px] p-4 bg-[#0d1117] border border-[#2a3441] rounded-lg text-gray-300 text-sm font-mono resize-none focus:outline-none focus:border-primary-500"
              style={{ lineHeight: '1.6' }}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 导出配置 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 选择导出类型 */}
            <div className="card">
              <h3 className="font-semibold text-white mb-4">1. 选择导出类型</h3>
              <div className="grid grid-cols-2 gap-3">
                {exportTypes.map((type) => {
                  const Icon = type.icon;
                  return (
                    <button
                      key={type.id}
                      onClick={() => setSelectedType(type.id)}
                      className={`p-4 rounded-lg border text-left transition-all ${
                        selectedType === type.id
                          ? 'border-primary-500 bg-primary-500/10'
                          : 'border-[#2a3441] hover:border-[#3a4451] bg-[#151a24]'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Icon className={`w-4 h-4 ${selectedType === type.id ? 'text-primary-400' : 'text-gray-500'}`} />
                        <span className="font-medium text-white">{type.name}</span>
                      </div>
                      <div className="text-sm text-gray-500">{type.description}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 选择格式 */}
            <div className="card">
              <h3 className="font-semibold text-white mb-4">2. 选择文件格式</h3>
              <div className="flex space-x-4">
                {formats.map((format) => {
                  const Icon = format.icon;
                  return (
                    <button
                      key={format.id}
                      onClick={() => setSelectedFormat(format.id)}
                      className={`flex-1 p-4 rounded-lg border text-center transition-all ${
                        selectedFormat === format.id
                          ? 'border-primary-500 bg-primary-500/10'
                          : 'border-[#2a3441] hover:border-[#3a4451] bg-[#151a24]'
                      }`}
                    >
                      <Icon className={`w-6 h-6 mx-auto mb-2 ${selectedFormat === format.id ? 'text-primary-400' : 'text-gray-500'}`} />
                      <div className="font-medium text-white">{format.name}</div>
                      <div className="text-sm text-gray-500">{format.description}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 筛选条件 */}
            {(needsDateRange || needsSymbols) && (
              <div className="card">
                <h3 className="font-semibold text-white mb-4">3. 筛选条件</h3>
                <div className="space-y-4">
                  {needsSymbols && (
                    <div>
                      <label className="block text-sm font-medium text-gray-400 mb-2">
                        品种筛选
                      </label>
                      <select
                        value={selectedSymbols}
                        onChange={(e) => setSelectedSymbols(e.target.value)}
                        className="w-full border border-[#2a3441] rounded-lg px-4 py-2 bg-[#151a24] text-gray-200"
                      >
                        {symbolOptions.map((opt) => (
                          <option key={opt.value} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  {needsDateRange && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          开始日期
                        </label>
                        <input
                          type="date"
                          value={startDate}
                          onChange={(e) => setStartDate(e.target.value)}
                          className="w-full border border-[#2a3441] rounded-lg px-4 py-2 bg-[#151a24] text-gray-200"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                          结束日期
                        </label>
                        <input
                          type="date"
                          value={endDate}
                          onChange={(e) => setEndDate(e.target.value)}
                          className="w-full border border-[#2a3441] rounded-lg px-4 py-2 bg-[#151a24] text-gray-200"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* 导出预览和按钮 */}
          <div className="space-y-6">
            {/* 导出预览 */}
            <div className="card">
              <h3 className="font-semibold text-white mb-4">导出预览</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between py-2 border-b border-[#2a3441]">
                  <span className="text-gray-500">数据类型</span>
                  <span className="font-medium text-white">
                    {exportTypes.find((t) => t.id === selectedType)?.name}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-[#2a3441]">
                  <span className="text-gray-500">文件格式</span>
                  <span className="font-medium text-white">
                    {formats.find((f) => f.id === selectedFormat)?.name}
                  </span>
                </div>
                {selectedSymbols && (
                  <div className="flex justify-between py-2 border-b border-[#2a3441]">
                    <span className="text-gray-500">品种筛选</span>
                    <span className="font-medium text-white text-right">
                      {symbolOptions.find((o) => o.value === selectedSymbols)?.label}
                    </span>
                  </div>
                )}
                {startDate && (
                  <div className="flex justify-between py-2 border-b border-[#2a3441]">
                    <span className="text-gray-500">开始日期</span>
                    <span className="font-medium text-white">{startDate}</span>
                  </div>
                )}
                {endDate && (
                  <div className="flex justify-between py-2">
                    <span className="text-gray-500">结束日期</span>
                    <span className="font-medium text-white">{endDate}</span>
                  </div>
                )}
              </div>
            </div>

            {/* 导出按钮 */}
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="w-full bg-primary-500 text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {isExporting ? (
                <>
                  <Check className="w-5 h-5" />
                  导出中...
                </>
              ) : (
                <>
                  <Download className="w-5 h-5" />
                  立即导出
                </>
              )}
            </button>

            {/* 使用提示 */}
            <div className="card bg-[#151a24] text-sm">
              <div className="flex items-start gap-2">
                <Info className="w-4 h-4 text-gray-500 mt-0.5" />
                <div>
                  <h4 className="font-medium text-gray-300 mb-2">导出说明</h4>
                  <ul className="text-gray-500 space-y-1">
                    <li>• CSV 格式使用 UTF-8 编码</li>
                    <li>• Excel 格式为 .xlsx 文件</li>
                    <li>• 不指定日期默认导出最近 30 天</li>
                    <li>• 文件名包含时间戳</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
