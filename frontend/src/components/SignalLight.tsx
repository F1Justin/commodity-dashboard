/**
 * 信号灯组件
 */
import { AlertCircle, CheckCircle, MinusCircle, AlertTriangle } from 'lucide-react';

interface SignalLightProps {
  status: 'high' | 'low' | 'normal' | 'high_alert' | 'low_alert';
  message?: string;
  showLabel?: boolean;
}

const statusConfig: Record<string, { color: string; label: string; bgColor: string }> = {
  high: { color: 'text-red-400', label: '高', bgColor: 'bg-red-500/20' },
  low: { color: 'text-emerald-400', label: '低', bgColor: 'bg-emerald-500/20' },
  normal: { color: 'text-gray-400', label: '正常', bgColor: 'bg-gray-500/20' },
  high_alert: { color: 'text-amber-400', label: '警示', bgColor: 'bg-amber-500/20' },
  low_alert: { color: 'text-amber-400', label: '警示', bgColor: 'bg-amber-500/20' },
};

export default function SignalLight({ status, message, showLabel = true }: SignalLightProps) {
  const config = statusConfig[status] || statusConfig.normal;

  const IconComponent = status === 'high' ? AlertCircle
    : status === 'low' ? CheckCircle
    : status === 'normal' ? MinusCircle
    : AlertTriangle;

  return (
    <div className="flex items-center space-x-2">
      <div className={`p-1 rounded ${config.bgColor}`}>
        <IconComponent className={`w-4 h-4 ${config.color}`} />
      </div>
      {showLabel && (
        <span className={`text-sm font-medium ${config.color}`}>
          {config.label}
        </span>
      )}
      {message && (
        <span className="text-sm text-gray-500">{message}</span>
      )}
    </div>
  );
}
