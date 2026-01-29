/**
 * 宏观数据页面 - 深色主题
 */
import Head from 'next/head';
import { useState } from 'react';
import { useCpiCompare } from '@/lib/hooks';
import LineChart from '@/components/charts/LineChart';
import useSWR from 'swr';
import api from '@/lib/api';
import { Globe2, Info, TrendingUp, Fuel } from 'lucide-react';

const fetcher = (url: string) => api.get(url);

export default function Macro() {
  const [cpiMonths, setCpiMonths] = useState(24);
  const { data: cpiData, error: cpiError } = useCpiCompare(cpiMonths);
  const { data: oilData, error: oilError } = useSWR('/macro/oil_price?months=24', fetcher);

  // 转换 CPI 数据格式
  const cpiSeries = cpiData?.series?.map((s: any) => ({
    name: s.name,
    data: s.data,
  })) || [];

  // 转换油价数据格式
  const oilSeries = (oilData as any)
    ? [
        {
          name: '92号汽油',
          data: (oilData as any).gasoline?.data?.map((d: any) => [d.date, d.price]) || [],
        },
        {
          name: '0号柴油',
          data: (oilData as any).diesel?.data?.map((d: any) => [d.date, d.price]) || [],
        },
      ]
    : [];

  return (
    <>
      <Head>
        <title>宏观数据 - 大宗商品战情室</title>
      </Head>

      <div className="space-y-6">
        {/* 页面标题 */}
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Globe2 className="w-7 h-7 text-primary-400" />
            宏观数据
          </h1>
          <p className="text-gray-500 mt-1">
            中美 CPI、国内汽柴油价格等宏观经济指标
          </p>
        </div>

        {/* CPI 对比 */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-400" />
              中美 CPI 同比对比
            </h2>
            <select
              value={cpiMonths}
              onChange={(e) => setCpiMonths(Number(e.target.value))}
              className="border border-[#2a3441] rounded-lg px-3 py-2 text-sm bg-[#1a1f2e] text-gray-200"
            >
              <option value={12}>12个月</option>
              <option value={24}>24个月</option>
              <option value={36}>36个月</option>
              <option value={60}>60个月</option>
            </select>
          </div>
          {cpiError ? (
            <div className="card bg-red-500/10 border-red-500/20 text-center py-12 text-red-400">
              CPI 数据加载失败
            </div>
          ) : cpiSeries.length > 0 ? (
            <LineChart
              title="中美 CPI 同比走势"
              series={cpiSeries}
              yAxisName="%"
            />
          ) : (
            <div className="card text-center py-12 text-gray-500">
              暂无 CPI 数据
            </div>
          )}
        </div>

        {/* 汽柴油价格 */}
        <div>
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Fuel className="w-5 h-5 text-orange-400" />
            国内汽柴油零售价
          </h2>
          {oilError ? (
            <div className="card bg-red-500/10 border-red-500/20 text-center py-12 text-red-400">
              油价数据加载失败
            </div>
          ) : oilSeries.length > 0 && oilSeries[0].data.length > 0 ? (
            <LineChart
              title="国内汽柴油零售价走势"
              series={oilSeries}
              yAxisName="元/升"
            />
          ) : (
            <div className="card text-center py-12 text-gray-500">
              暂无油价数据
            </div>
          )}
        </div>

        {/* CPI 数据说明 */}
        <div className="card bg-[#151a24]">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <h3 className="font-medium text-white mb-3">数据说明</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-400">
                <div>
                  <h4 className="font-medium text-gray-300 mb-2">CPI (居民消费价格指数)</h4>
                  <ul className="space-y-1">
                    <li>• 衡量通货膨胀的核心指标</li>
                    <li>• 同比上涨表示物价上涨</li>
                    <li>• 中国数据来源: 国家统计局</li>
                    <li>• 美国数据来源: 美国劳工部</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-gray-300 mb-2">汽柴油零售价</h4>
                  <ul className="space-y-1">
                    <li>• 由发改委定期调整</li>
                    <li>• 反映国内成品油价格变化</li>
                    <li>• 与国际原油价格高度相关</li>
                    <li>• 调价周期约为 10 个工作日</li>
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
