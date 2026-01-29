/**
 * API 请求封装
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// 实时数据
export const getSnapshot = () => api.get('/snapshot');
export const getSymbolSnapshot = (symbol: string) => api.get(`/snapshot/${symbol}`);
export const getSymbols = () => api.get('/symbols');

// 溢价率计算器
export const getCalculatorData = () => api.get('/calculator');
export const getPremiumHistory = (pair: string, days: number = 30) =>
  api.get('/calculator/history', { params: { pair, days } });
export const getRatioHistory = (ratioType: string, days: number = 30) =>
  api.get('/calculator/ratios', { params: { ratio_type: ratioType, days } });

// 归一化图表
export const getNormalizedData = (group: string, period: string = '1y', baseDate?: string) =>
  api.get('/normalized', { params: { group, period, base_date: baseDate } });
export const fetchNormalized = (group: string, period: string = '7d', baseDate?: string) =>
  api.get('/normalized', { params: { group, period, base_date: baseDate } });
export const getChartGroups = () => api.get('/normalized/groups');

// 宏观数据
export const getCpiData = (country: string = 'CN', months: number = 24) =>
  api.get('/macro/cpi', { params: { country, months } });
export const getCpiCompare = (months: number = 24) =>
  api.get('/macro/cpi/compare', { params: { months } });
export const getOilPrice = (months: number = 24) =>
  api.get('/macro/oil_price', { params: { months } });

// 数据导出
export const getExportTypes = () => api.get('/export/types');
export const exportData = (
  type: string,
  format: string = 'csv',
  symbols?: string,
  startDate?: string,
  endDate?: string
) => {
  const params = new URLSearchParams();
  params.append('type', type);
  params.append('format', format);
  if (symbols) params.append('symbols', symbols);
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  
  // 直接打开下载链接
  window.open(`/api/export?${params.toString()}`, '_blank');
};

export default api;
