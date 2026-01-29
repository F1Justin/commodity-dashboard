/**
 * 比值指标卡片 - 深色主题
 */
import SignalLight from '../SignalLight';
import { Info } from 'lucide-react';

interface RatioCardProps {
  title: string;
  value: number | null;
  signal: 'high' | 'low' | 'normal' | 'high_alert' | 'low_alert';
  message?: string;
  description?: string;
  historicalRange?: string;
  icon?: React.ReactNode;
}

export default function RatioCard({
  title,
  value,
  signal,
  message,
  description,
  historicalRange,
  icon,
}: RatioCardProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {icon && <div className="text-gray-500">{icon}</div>}
          <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
        </div>
        <SignalLight status={signal} showLabel={false} />
      </div>
      <div className="text-3xl font-bold text-white mb-2">
        {value !== null ? value.toFixed(2) : '--'}
      </div>
      {message && (
        <p className="text-sm text-gray-400 mb-2">{message}</p>
      )}
      {historicalRange && (
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Info className="w-3 h-3" />
          <span>历史区间: {historicalRange}</span>
        </div>
      )}
      {description && (
        <p className="text-xs text-gray-500 mt-2">{description}</p>
      )}
    </div>
  );
}
