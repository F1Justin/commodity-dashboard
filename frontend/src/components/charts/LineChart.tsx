/**
 * 折线图组件 - 深色主题
 */
import ReactECharts from 'echarts-for-react';

interface Series {
  name: string;
  data: [string, number][];
}

interface LineChartProps {
  title: string;
  series: Series[];
  yAxisName?: string;
  showDataZoom?: boolean;
  height?: number;
}

export default function LineChart({
  title,
  series,
  yAxisName = '',
  showDataZoom = true,
  height = 400,
}: LineChartProps) {
  // 深色主题配色 - 扩展颜色列表支持更多品种
  const colors = [
    '#3b82f6', // 蓝色
    '#f59e0b', // 琥珀色
    '#10b981', // 绿色
    '#ef4444', // 红色
    '#8b5cf6', // 紫色
    '#ec4899', // 粉色
    '#06b6d4', // 青色
    '#f97316', // 橙色
    '#84cc16', // 黄绿
    '#6366f1', // 靛蓝
    '#14b8a6', // 蓝绿
    '#a855f7', // 紫罗兰
    '#eab308', // 黄色
    '#22c55e', // 亮绿
    '#0ea5e9', // 天蓝
    '#d946ef', // 洋红
  ];

  const option = {
    backgroundColor: 'transparent',
    title: {
      text: title,
      left: 'center',
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
      textStyle: {
        color: '#e5e7eb',
      },
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: '#4b5563',
        },
      },
    },
    legend: {
      data: series.map((s) => s.name),
      top: 30,
      textStyle: {
        color: '#9ca3af',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: showDataZoom ? '15%' : '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#374151',
        },
      },
      axisLabel: {
        color: '#9ca3af',
      },
      splitLine: {
        lineStyle: {
          color: '#1f2937',
        },
      },
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      nameTextStyle: {
        color: '#9ca3af',
        padding: [0, 40, 0, 0],
      },
      axisLine: {
        lineStyle: {
          color: '#374151',
        },
      },
      axisLabel: {
        color: '#9ca3af',
      },
      splitLine: {
        lineStyle: {
          color: '#1f2937',
        },
      },
    },
    series: series.map((s, index) => ({
      name: s.name,
      type: 'line',
      smooth: true,
      symbol: 'none',
      data: s.data,
      lineStyle: {
        width: 2,
        color: colors[index % colors.length],
      },
      itemStyle: {
        color: colors[index % colors.length],
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: colors[index % colors.length] + '40' },
            { offset: 1, color: colors[index % colors.length] + '05' },
          ],
        },
      },
      // 国际品种使用虚线
      ...(s.name.includes('LME') || s.name.includes('伦敦') || s.name.includes('CBOT')
        ? { lineStyle: { type: 'dashed', width: 2, color: colors[index % colors.length] } }
        : {}),
    })),
    dataZoom: showDataZoom
      ? [
          {
            type: 'slider',
            start: 0,
            end: 100,
            backgroundColor: '#1f2937',
            borderColor: '#374151',
            dataBackground: {
              lineStyle: { color: '#4b5563' },
              areaStyle: { color: '#374151' },
            },
            selectedDataBackground: {
              lineStyle: { color: '#3b82f6' },
              areaStyle: { color: '#3b82f640' },
            },
            handleStyle: {
              color: '#3b82f6',
              borderColor: '#3b82f6',
            },
            textStyle: {
              color: '#9ca3af',
            },
          },
          {
            type: 'inside',
          },
        ]
      : [],
  };

  return (
    <ReactECharts option={option} style={{ height: `${height}px` }} />
  );
}
