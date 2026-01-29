/**
 * 溢价率计算器页面 - 深色主题
 */
import Head from 'next/head';
import { useState } from 'react';
import { useCalculator, usePremiumHistory } from '@/lib/hooks';
import PremiumTable from '@/components/PremiumTable';
import LineChart from '@/components/charts/LineChart';
import {
  Calculator,
  Info,
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';

export default function CalculatorPage() {
  const { data: calcData, error } = useCalculator();
  const [selectedPair, setSelectedPair] = useState('GOLD');
  const [historyDays, setHistoryDays] = useState(30);
  const { data: historyData } = usePremiumHistory(selectedPair, historyDays);

  // 转换数据格式用于表格
  const tableData = [
    calcData?.gold && {
      name: '黄金',
      domesticPrice: calcData.gold.shfe_cny_g,
      foreignPrice: calcData.gold.london_usd_oz,
      theoreticalPrice: calcData.gold.theoretical_cny_g,
      premiumRate: calcData.gold.premium_rate,
      signal: calcData.signals?.gold_premium || 'normal',
      message: calcData.signals?.gold_premium_message,
    },
    calcData?.silver && {
      name: '白银',
      domesticPrice: calcData.silver.shfe_cny_kg,
      foreignPrice: calcData.silver.london_usd_oz,
      theoreticalPrice: calcData.silver.theoretical_cny_kg,
      premiumRate: calcData.silver.premium_rate,
      signal: calcData.signals?.silver_premium || 'normal',
    },
    calcData?.copper && {
      name: '铜',
      domesticPrice: calcData.copper.shfe_cny_ton,
      foreignPrice: calcData.copper.lme_usd_ton,
      theoreticalPrice: calcData.copper.theoretical_cny_ton,
      premiumRate: calcData.copper.premium_rate,
      signal: calcData.signals?.copper_premium || 'normal',
      message: calcData.signals?.copper_premium_message,
    },
    calcData?.aluminum && {
      name: '铝',
      domesticPrice: calcData.aluminum.shfe_cny_ton,
      foreignPrice: calcData.aluminum.lme_usd_ton,
      theoreticalPrice: calcData.aluminum.theoretical_cny_ton,
      premiumRate: calcData.aluminum.premium_rate,
      signal: calcData.signals?.aluminum_premium || 'normal',
    },
  ].filter(Boolean) as any[];

  // 转换历史数据用于图表
  const chartSeries = historyData?.data
    ? [
        {
          name: '溢价率',
          data: historyData.data.map((d: any) => [d.timestamp, d.spread_rate]),
        },
      ]
    : [];

  const pairs = [
    { value: 'GOLD', label: '黄金' },
    { value: 'SILVER', label: '白银' },
    { value: 'COPPER', label: '铜' },
    { value: 'ALUMINUM', label: '铝' },
  ];

  return (
    <>
      <Head>
        <title>溢价率计算器 - 大宗商品战情室</title>
      </Head>

      <div className="space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <Calculator className="w-7 h-7 text-primary-400" />
              溢价率计算器
            </h1>
            <p className="text-gray-500 text-sm mt-1">自动计算国内外价差，发现套利机会</p>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-500">汇率:</span>
            <span className="text-primary-400 font-semibold">{calcData?.exchange_rate?.toFixed(4) ?? '--'}</span>
            <span className="text-gray-500">USD/CNY</span>
          </div>
        </div>

        {/* 计算公式说明 */}
        <div className="card bg-primary-500/10 border-primary-500/20">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-primary-400 mt-0.5" />
            <div>
              <h3 className="font-medium text-primary-400 mb-2">计算公式</h3>
              <div className="text-sm text-gray-300 space-y-1">
                <p><span className="text-gray-500">理论沪金价 =</span> 伦敦金(USD/oz) ÷ 31.1035 × 汇率</p>
                <p><span className="text-gray-500">溢价率 =</span> (实际沪金 - 理论沪金) ÷ 理论沪金 × 100%</p>
              </div>
            </div>
          </div>
        </div>

        {/* 溢价率数据表格 */}
        {tableData.length > 0 && (
          <PremiumTable data={tableData} exchangeRate={calcData?.exchange_rate ?? 7.25} />
        )}

        {/* 信号解读面板 */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            信号解读规则
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-300 mb-3">黄金溢价率</h4>
              <div className="flex items-center gap-3 text-sm">
                <div className="p-1 rounded bg-red-500/20">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                </div>
                <span className="text-gray-400">&gt; +2%: 国内抢金，恐慌情绪浓厚</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="p-1 rounded bg-emerald-500/20">
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                </div>
                <span className="text-gray-400">&lt; -2%: 国内金价偏低，可能有机会</span>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-300 mb-3">铜溢价率</h4>
              <div className="flex items-center gap-3 text-sm">
                <div className="p-1 rounded bg-emerald-500/20">
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                </div>
                <span className="text-gray-400">&lt; -5%: 国内铜便宜，做多机会</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="p-1 rounded bg-red-500/20">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                </div>
                <span className="text-gray-400">&gt; +5%: 国内铜溢价过高</span>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-300 mb-3">金银比</h4>
              <div className="flex items-center gap-3 text-sm">
                <div className="p-1 rounded bg-amber-500/20">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                </div>
                <span className="text-gray-400">&gt; 80: 避险情绪高涨，白银被低估</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="p-1 rounded bg-amber-500/20">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                </div>
                <span className="text-gray-400">&lt; 60: 白银可能被高估</span>
              </div>
            </div>
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-300 mb-3">铜金比 (经济温度计)</h4>
              <div className="flex items-center gap-3 text-sm">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <span className="text-gray-400">上升: 经济预期改善</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <TrendingDown className="w-4 h-4 text-red-400" />
                <span className="text-gray-400">下降: 经济预期恶化，避险升温</span>
              </div>
            </div>
          </div>
        </div>

        {/* 历史溢价率走势 */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">历史溢价率走势</h2>
            <div className="flex items-center space-x-3">
              <select
                value={selectedPair}
                onChange={(e) => setSelectedPair(e.target.value)}
                className="border border-[#2a3441] rounded-lg px-3 py-2 text-sm bg-[#1a1f2e] text-gray-200"
              >
                {pairs.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
              <select
                value={historyDays}
                onChange={(e) => setHistoryDays(Number(e.target.value))}
                className="border border-[#2a3441] rounded-lg px-3 py-2 text-sm bg-[#1a1f2e] text-gray-200"
              >
                <option value={7}>7天</option>
                <option value={30}>30天</option>
                <option value={90}>90天</option>
                <option value={365}>1年</option>
              </select>
            </div>
          </div>
          {chartSeries.length > 0 ? (
            <LineChart
              title={`${pairs.find((p) => p.value === selectedPair)?.label}溢价率走势`}
              series={chartSeries}
              yAxisName="%"
            />
          ) : (
            <div className="card text-center py-12 text-gray-500">暂无历史数据</div>
          )}
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="card bg-red-500/10 border-red-500/20 text-center py-8 text-red-400">
            数据加载失败，请检查后端服务是否启动
          </div>
        )}
      </div>
    </>
  );
}
