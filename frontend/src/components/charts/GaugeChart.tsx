/**
 * 仪表盘图表组件 - 深色主题
 */
import ReactECharts from 'echarts-for-react';

interface GaugeChartProps {
  title: string;
  value: number;
  min?: number;
  max?: number;
}

export default function GaugeChart({ title, value, min = -10, max = 10 }: GaugeChartProps) {
  const option = {
    backgroundColor: 'transparent',
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        center: ['50%', '75%'],
        radius: '90%',
        min,
        max,
        splitNumber: 4,
        axisLine: {
          lineStyle: {
            width: 6,
            color: [
              [0.25, '#10b981'],  // 绿色 -10 到 -5
              [0.45, '#34d399'],  // 浅绿 -5 到 -1
              [0.55, '#4b5563'],  // 灰色 -1 到 1
              [0.75, '#f87171'],  // 浅红 1 到 5
              [1, '#ef4444'],     // 红色 5 到 10
            ],
          },
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '12%',
          width: 20,
          offsetCenter: [0, '-60%'],
          itemStyle: {
            color: 'auto',
          },
        },
        axisTick: {
          length: 12,
          lineStyle: {
            color: 'auto',
            width: 2,
          },
        },
        splitLine: {
          length: 20,
          lineStyle: {
            color: 'auto',
            width: 5,
          },
        },
        axisLabel: {
          color: '#9ca3af',
          fontSize: 11,
          distance: -50,
          rotate: 'tangential',
          formatter: function (value: number) {
            if (value === min) return '做多';
            if (value === max) return '观望';
            if (value === 0) return '平衡';
            return '';
          },
        },
        title: {
          offsetCenter: [0, '-10%'],
          fontSize: 13,
          color: '#9ca3af',
        },
        detail: {
          fontSize: 22,
          offsetCenter: [0, '-35%'],
          valueAnimation: true,
          formatter: function (value: number) {
            return (value > 0 ? '+' : '') + value.toFixed(2) + '%';
          },
          color: 'inherit',
        },
        data: [
          {
            value: value,
            name: title,
          },
        ],
      },
    ],
  };

  return (
    <div className="card">
      <ReactECharts option={option} style={{ height: '180px' }} />
    </div>
  );
}
