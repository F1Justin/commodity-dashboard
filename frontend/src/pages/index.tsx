/**
 * 仪表盘首页 - 深色主题
 */
import Head from 'next/head';
import { useCalculator, useSnapshot } from '@/lib/hooks';
import PriceCard from '@/components/PriceCard';
import GaugeChart from '@/components/charts/GaugeChart';
import RatioCard from '@/components/charts/RatioCard';
import SignalLight from '@/components/SignalLight';
import {
  Coins,
  Zap,
  Fuel,
  Wheat,
  TrendingUp,
  Activity,
  Scale,
  Thermometer,
  RefreshCw,
} from 'lucide-react';

export default function Dashboard() {
  const { data: calcData, error: calcError, mutate } = useCalculator();
  const { data: snapshotData, error: snapshotError } = useSnapshot();

  const isLoading = !calcData && !calcError;

  // 从快照数据中提取关键价格
  const keyPrices = [
    { symbol: 'SHFE.AU', name: '沪金', unit: '元/克', icon: <Coins className="w-4 h-4" /> },
    { symbol: 'SHFE.CU', name: '沪铜', unit: '元/吨', icon: <Zap className="w-4 h-4" /> },
    { symbol: 'INE.SC', name: 'INE原油', unit: '元/桶', icon: <Fuel className="w-4 h-4" /> },
    { symbol: 'DCE.M', name: '豆粕', unit: '元/吨', icon: <Wheat className="w-4 h-4" /> },
  ];

  return (
    <>
      <Head>
        <title>仪表盘 - 大宗商品战情室</title>
      </Head>

      <div className="space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">仪表盘</h1>
            <p className="text-gray-500 text-sm mt-1">实时监控全球大宗商品价格与溢价率</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              更新: {calcData?.timestamp ? new Date(calcData.timestamp).toLocaleTimeString() : '--'}
            </span>
            <button
              onClick={() => mutate()}
              className="p-2 rounded-lg bg-[#1a1f2e] border border-[#2a3441] hover:border-[#3a4451] transition-colors"
            >
              <RefreshCw className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>

        {/* 关键价格卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {keyPrices.map((item) => {
            const priceData = snapshotData?.data?.[item.symbol];
            return (
              <PriceCard
                key={item.symbol}
                title={item.name}
                price={priceData?.price ?? null}
                unit={item.unit}
                icon={item.icon}
                subtitle={priceData?.timestamp ? `更新: ${new Date(priceData.timestamp).toLocaleTimeString()}` : undefined}
              />
            );
          })}
        </div>

        {/* 溢价率仪表盘 */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-primary-400" />
            <h2 className="text-lg font-semibold text-white">溢价率仪表盘</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <GaugeChart
              title="黄金溢价率"
              value={calcData?.gold?.premium_rate ?? 0}
            />
            <GaugeChart
              title="白银溢价率"
              value={calcData?.silver?.premium_rate ?? 0}
            />
            <GaugeChart
              title="铜溢价率"
              value={calcData?.copper?.premium_rate ?? 0}
            />
            <GaugeChart
              title="铝溢价率"
              value={calcData?.aluminum?.premium_rate ?? 0}
            />
          </div>
        </div>

        {/* 信号面板 */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary-400" />
            <h2 className="text-lg font-semibold text-white">交易信号</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 溢价率信号 */}
            <div className="card">
              <h3 className="font-medium text-white mb-4 flex items-center gap-2">
                <Activity className="w-4 h-4 text-gray-500" />
                溢价率信号
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b border-[#2a3441]">
                  <span className="text-gray-400">黄金溢价率</span>
                  <SignalLight
                    status={calcData?.signals?.gold_premium || 'normal'}
                    message={calcData?.signals?.gold_premium_message}
                  />
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-400">铜溢价率</span>
                  <SignalLight
                    status={calcData?.signals?.copper_premium || 'normal'}
                    message={calcData?.signals?.copper_premium_message}
                  />
                </div>
              </div>
            </div>

            {/* 比值指标 */}
            <div className="card">
              <h3 className="font-medium text-white mb-4 flex items-center gap-2">
                <Scale className="w-4 h-4 text-gray-500" />
                比值指标
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b border-[#2a3441]">
                  <span className="text-gray-400">金银比</span>
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold text-white">{calcData?.ratios?.gold_silver?.toFixed(2) ?? '--'}</span>
                    <SignalLight
                      status={calcData?.signals?.gold_silver_ratio || 'normal'}
                      showLabel={false}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-400">铜金比</span>
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold text-white">{calcData?.ratios?.copper_gold?.toFixed(4) ?? '--'}</span>
                    <SignalLight
                      status={calcData?.signals?.economic_sentiment || 'normal'}
                      showLabel={false}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 比值指标详情 */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Thermometer className="w-5 h-5 text-primary-400" />
            <h2 className="text-lg font-semibold text-white">比值指标详情</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <RatioCard
              title="金银比"
              value={calcData?.ratios?.gold_silver ?? null}
              signal={calcData?.signals?.gold_silver_ratio || 'normal'}
              message={calcData?.signals?.gold_silver_message}
              historicalRange="60-80"
              description="金价/银价，反映避险情绪"
              icon={<Scale className="w-4 h-4" />}
            />
            <RatioCard
              title="铜金比 (经济温度计)"
              value={calcData?.ratios?.copper_gold ?? null}
              signal={calcData?.signals?.economic_sentiment || 'normal'}
              message={calcData?.signals?.economic_message}
              description="铜价/金价，反映经济预期"
              icon={<Thermometer className="w-4 h-4" />}
            />
          </div>
        </div>

        {/* 数据状态提示 */}
        {isLoading && (
          <div className="text-center py-8 text-gray-500">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
            加载中...
          </div>
        )}
        {calcError && (
          <div className="card bg-red-500/10 border-red-500/20 text-center py-8 text-red-400">
            数据加载失败，请检查后端服务是否启动
          </div>
        )}
      </div>
    </>
  );
}
