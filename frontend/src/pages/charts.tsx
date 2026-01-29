/**
 * 归一化图表页面 - 网格化展示
 */
import Head from 'next/head';
import { useState, useEffect } from 'react';
import { fetchNormalized } from '@/lib/api';
import { LineChart as LineChartIcon, Info, Coins, Zap, Fuel, Wheat, Layers } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

const chartGroups = [
  { id: 'all', name: '全部品种', icon: Layers },
  { id: 'precious_metals', name: '贵金属', icon: Coins },
  { id: 'base_metals', name: '有色金属', icon: Zap },
  { id: 'energy', name: '能源', icon: Fuel },
  { id: 'agriculture', name: '农产品', icon: Wheat },
];

const periods = [
  { value: '1d', label: '24小时' },
  { value: '7d', label: '7天' },
];

// 颜色配置
const colors = [
  '#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899',
  '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6', '#a855f7',
  '#eab308', '#22c55e', '#0ea5e9', '#d946ef',
];

interface ChartData {
  group: string;
  group_name: string;
  period: string;
  base_date: string;
  base_value: number;
  series: Array<{
    symbol: string;
    name: string;
    data: Array<[string, number]>;
  }>;
}

// 小图表组件（固定，无缩放）
function MiniChart({ 
  title, 
  series, 
  height = 220 
}: { 
  title: string; 
  series: Array<{ name: string; data: [string, number][] }>; 
  height?: number;
}) {
  const option = {
    backgroundColor: 'transparent',
    title: {
      text: title,
      left: 'center',
      top: 5,
      textStyle: {
        fontSize: 13,
        fontWeight: 500,
        color: '#e5e7eb',
      },
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1f2937',
      borderColor: '#374151',
      textStyle: { color: '#e5e7eb', fontSize: 11 },
      confine: true,
    },
    legend: {
      data: series.map((s) => s.name),
      top: 28,
      textStyle: { color: '#9ca3af', fontSize: 10 },
      itemWidth: 12,
      itemHeight: 8,
      itemGap: 8,
    },
    grid: {
      left: '8%',
      right: '4%',
      top: series.length > 4 ? 70 : 55,
      bottom: '8%',
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#6b7280', fontSize: 9 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#6b7280', fontSize: 9 },
      splitLine: { lineStyle: { color: '#1f2937' } },
    },
    series: series.map((s, index) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      symbol: 'none',
      data: s.data,
      lineStyle: {
        width: 1.5,
        color: colors[index % colors.length],
        type: s.name.includes('LME') || s.name.includes('伦敦') || s.name.includes('CBOT') ? 'dashed' : 'solid',
      },
      itemStyle: { color: colors[index % colors.length] },
    })),
  };

  return (
    <ReactECharts 
      option={option} 
      style={{ height: `${height}px` }} 
      opts={{ renderer: 'canvas' }}
    />
  );
}

// 大图表组件（全部品种，固定，无缩放）
function LargeChart({ 
  title, 
  series, 
  height = 320 
}: { 
  title: string; 
  series: Array<{ name: string; data: [string, number][] }>; 
  height?: number;
}) {
  const option = {
    backgroundColor: 'transparent',
    title: {
      text: title,
      left: 'center',
      top: 5,
      textStyle: {
        fontSize: 14,
        fontWeight: 500,
        color: '#e5e7eb',
      },
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1f2937',
      borderColor: '#374151',
      textStyle: { color: '#e5e7eb', fontSize: 11 },
      confine: true,
    },
    legend: {
      data: series.map((s) => s.name),
      top: 30,
      textStyle: { color: '#9ca3af', fontSize: 10 },
      itemWidth: 14,
      itemHeight: 8,
      itemGap: 10,
    },
    grid: {
      left: '6%',
      right: '3%',
      top: 80,
      bottom: '8%',
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#6b7280', fontSize: 10 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#6b7280', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1f2937' } },
    },
    series: series.map((s, index) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      symbol: 'none',
      data: s.data,
      lineStyle: {
        width: 1.5,
        color: colors[index % colors.length],
        type: s.name.includes('LME') || s.name.includes('伦敦') || s.name.includes('CBOT') ? 'dashed' : 'solid',
      },
      itemStyle: { color: colors[index % colors.length] },
    })),
  };

  return (
    <ReactECharts 
      option={option} 
      style={{ height: `${height}px` }} 
      opts={{ renderer: 'canvas' }}
    />
  );
}

export default function Charts() {
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [chartsData, setChartsData] = useState<Record<string, ChartData>>({});
  const [loading, setLoading] = useState(true);

  // 加载所有图表数据
  useEffect(() => {
    const loadAllCharts = async () => {
      setLoading(true);
      
      try {
        const results: Record<string, ChartData> = {};
        
        const promises = chartGroups.map(async (group) => {
          try {
            const data = await fetchNormalized(group.id, selectedPeriod) as ChartData;
            return { id: group.id, data };
          } catch (e) {
            console.error(`Failed to fetch ${group.id}:`, e);
            return { id: group.id, data: null as ChartData | null };
          }
        });
        
        const responses = await Promise.all(promises);
        
        responses.forEach(({ id, data }) => {
          if (data && data.series) {
            results[id] = data;
          }
        });
        
        setChartsData(results);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    
    loadAllCharts();
  }, [selectedPeriod]);

  const formatChartSeries = (data: ChartData | undefined) => {
    if (!data?.series) return [];
    return data.series.map((s) => ({
      name: s.name,
      data: s.data,
    }));
  };

  // 分类图表（不包含 all）
  const categoryGroups = chartGroups.filter(g => g.id !== 'all');

  return (
    <>
      <Head>
        <title>归一化图表 - 大宗商品战情室</title>
      </Head>

      <div className="space-y-4">
        {/* 页面标题和周期切换 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <LineChartIcon className="w-6 h-6 text-primary-400" />
            <h1 className="text-xl font-bold text-white">归一化对比图表</h1>
          </div>
          
          {/* 周期切换 */}
          <div className="flex items-center gap-2">
            {periods.map((p) => (
              <button
                key={p.value}
                onClick={() => setSelectedPeriod(p.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedPeriod === p.value
                    ? 'bg-primary-500 text-white'
                    : 'bg-[#1a1f2e] text-gray-400 hover:bg-[#242d3a] border border-[#2a3441]'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* 加载中 */}
        {loading && (
          <div className="card text-center py-8 text-gray-500">
            <div className="animate-pulse">加载图表数据中...</div>
          </div>
        )}

        {/* 图表网格 */}
        {!loading && (
          <>
            {/* 全部品种大图 */}
            <div className="card p-3">
              {formatChartSeries(chartsData['all']).length > 0 ? (
                <LargeChart
                  title="全部品种综合对比"
                  series={formatChartSeries(chartsData['all'])}
                  height={300}
                />
              ) : (
                <div className="h-[300px] flex items-center justify-center text-gray-500">
                  暂无数据
                </div>
              )}
            </div>

            {/* 分类图表 2x2 网格 */}
            <div className="grid grid-cols-2 gap-4">
              {categoryGroups.map((group) => {
                const Icon = group.icon;
                const series = formatChartSeries(chartsData[group.id]);
                
                return (
                  <div key={group.id} className="card p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className="w-4 h-4 text-primary-400" />
                      <span className="text-sm font-medium text-gray-300">{group.name}</span>
                    </div>
                    {series.length > 0 ? (
                      <MiniChart
                        title=""
                        series={series}
                        height={200}
                      />
                    ) : (
                      <div className="h-[200px] flex items-center justify-center text-gray-500 text-sm">
                        暂无数据
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* 说明 */}
            <div className="card bg-primary-500/10 border-primary-500/20 p-3">
              <div className="flex items-start gap-2">
                <Info className="w-4 h-4 text-primary-400 mt-0.5" />
                <div className="text-xs text-gray-400">
                  <span className="text-primary-400 font-medium">归一化说明：</span>
                  以基准日价格为100，数值&gt;100表示上涨，&lt;100表示下跌。虚线表示国际品种。
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
