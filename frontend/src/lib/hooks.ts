/**
 * 自定义 Hooks
 */
import useSWR from 'swr';
import api from './api';

const fetcher = (url: string) => api.get(url).then((res: any) => res);

// 实时数据 - 每分钟刷新
export function useSnapshot() {
  return useSWR('/snapshot', fetcher, {
    refreshInterval: 60000, // 1分钟
    revalidateOnFocus: false,
  });
}

// 溢价率计算器 - 每分钟刷新
export function useCalculator() {
  return useSWR('/calculator', fetcher, {
    refreshInterval: 60000,
    revalidateOnFocus: false,
  });
}

// 归一化数据
export function useNormalized(group: string, period: string = '1y') {
  return useSWR(`/normalized?group=${group}&period=${period}`, fetcher, {
    revalidateOnFocus: false,
  });
}

// CPI 对比数据
export function useCpiCompare(months: number = 24) {
  return useSWR(`/macro/cpi/compare?months=${months}`, fetcher, {
    revalidateOnFocus: false,
  });
}

// 溢价率历史
export function usePremiumHistory(pair: string, days: number = 30) {
  return useSWR(`/calculator/history?pair=${pair}&days=${days}`, fetcher, {
    revalidateOnFocus: false,
  });
}

// 比值历史
export function useRatioHistory(ratioType: string, days: number = 30) {
  return useSWR(`/calculator/ratios?ratio_type=${ratioType}&days=${days}`, fetcher, {
    revalidateOnFocus: false,
  });
}
