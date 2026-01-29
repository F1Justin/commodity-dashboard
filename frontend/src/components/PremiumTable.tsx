/**
 * 溢价率数据表格组件 - 深色主题
 */
import SignalLight from './SignalLight';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface PremiumData {
  name: string;
  domesticPrice: number;
  foreignPrice: number;
  theoreticalPrice: number;
  premiumRate: number;
  signal: 'high' | 'low' | 'normal';
  message?: string;
}

interface PremiumTableProps {
  data: PremiumData[];
  exchangeRate: number;
}

export default function PremiumTable({ data, exchangeRate }: PremiumTableProps) {
  const getPremiumDisplay = (rate: number) => {
    const isPositive = rate > 0;
    const isNegative = rate < 0;
    const Icon = isPositive ? ArrowUpRight : isNegative ? ArrowDownRight : Minus;
    const colorClass = rate > 2 ? 'text-red-400' : rate < -2 ? 'text-emerald-400' : 'text-gray-400';
    
    return (
      <div className={`flex items-center gap-1 font-semibold ${colorClass}`}>
        <Icon className="w-4 h-4" />
        <span>{isPositive ? '+' : ''}{rate.toFixed(2)}%</span>
      </div>
    );
  };

  return (
    <div className="card overflow-hidden p-0">
      <div className="px-6 py-4 border-b border-[#2a3441] flex items-center justify-between">
        <h3 className="font-semibold text-white">溢价率一览</h3>
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <span>汇率:</span>
          <span className="text-primary-400 font-medium">{exchangeRate.toFixed(4)}</span>
          <span>USD/CNY</span>
        </div>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>品种</th>
            <th>国内价格</th>
            <th>国际价格</th>
            <th>理论价格</th>
            <th>溢价率</th>
            <th>信号</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.name}>
              <td className="font-medium text-white">{item.name}</td>
              <td className="text-gray-300">{item.domesticPrice?.toLocaleString() ?? '--'}</td>
              <td className="text-gray-300">{item.foreignPrice?.toLocaleString() ?? '--'}</td>
              <td className="text-gray-400">{item.theoreticalPrice?.toLocaleString() ?? '--'}</td>
              <td>
                {item.premiumRate !== undefined
                  ? getPremiumDisplay(item.premiumRate)
                  : '--'}
              </td>
              <td>
                <SignalLight status={item.signal} showLabel={false} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
