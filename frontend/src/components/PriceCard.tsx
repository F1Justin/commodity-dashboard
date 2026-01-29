/**
 * 价格卡片组件 - 深色主题
 */
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface PriceCardProps {
  title: string;
  price: number | null;
  unit: string;
  change?: number;
  subtitle?: string;
  icon?: React.ReactNode;
}

export default function PriceCard({ title, price, unit, change, subtitle, icon }: PriceCardProps) {
  const isPositive = change !== undefined && change > 0;
  const isNegative = change !== undefined && change < 0;

  return (
    <div className="card hover:border-[#3a4451] transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {icon && <div className="text-gray-500">{icon}</div>}
          <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
        </div>
        {change !== undefined && (
          <div className={`flex items-center gap-1 text-sm font-medium ${
            isPositive ? 'text-red-400' : isNegative ? 'text-emerald-400' : 'text-gray-500'
          }`}>
            {isPositive ? <TrendingUp className="w-4 h-4" /> : 
             isNegative ? <TrendingDown className="w-4 h-4" /> : 
             <Minus className="w-4 h-4" />}
            <span>{Math.abs(change).toFixed(2)}%</span>
          </div>
        )}
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold text-white">
          {price !== null ? price.toLocaleString() : '--'}
        </span>
        <span className="text-gray-500 text-sm">{unit}</span>
      </div>
      {subtitle && (
        <p className="text-gray-500 text-xs mt-2">{subtitle}</p>
      )}
    </div>
  );
}
