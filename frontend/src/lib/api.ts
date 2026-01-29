/**
 * API 请求封装
 */
import axios, { AxiosInstance } from 'axios';

// 创建一个带类型的 Axios 实例，响应拦截器自动解构 data
const createApiInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: '/api',
    timeout: 30000,
  });

  // 请求拦截器
  instance.interceptors.request.use(
    (config) => {
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // 响应拦截器 - 自动解构 response.data
  instance.interceptors.response.use(
    (response) => {
      return response.data;
    },
    (error) => {
      console.error('API Error:', error);
      return Promise.reject(error);
    }
  );

  return instance;
};

const api = createApiInstance();

// 类型定义
type ApiResponse<T = any> = Promise<T>;

// 实时数据
export const getSnapshot = (): ApiResponse => api.get('/snapshot');
export const getSymbolSnapshot = (symbol: string): ApiResponse => api.get(`/snapshot/${symbol}`);
export const getSymbols = (): ApiResponse => api.get('/symbols');

// 溢价率计算器
export const getCalculatorData = (): ApiResponse => api.get('/calculator');
export const getPremiumHistory = (pair: string, days: number = 30): ApiResponse =>
  api.get('/calculator/history', { params: { pair, days } });
export const getRatioHistory = (ratioType: string, days: number = 30): ApiResponse =>
  api.get('/calculator/ratios', { params: { ratio_type: ratioType, days } });

// 归一化图表
export const getNormalizedData = (group: string, period: string = '1y', baseDate?: string): ApiResponse =>
  api.get('/normalized', { params: { group, period, base_date: baseDate } });
export const fetchNormalized = (group: string, period: string = '7d', baseDate?: string): ApiResponse =>
  api.get('/normalized', { params: { group, period, base_date: baseDate } });
export const getChartGroups = (): ApiResponse => api.get('/normalized/groups');

// 宏观数据
export const getCpiData = (country: string = 'CN', months: number = 24): ApiResponse =>
  api.get('/macro/cpi', { params: { country, months } });
export const getCpiCompare = (months: number = 24): ApiResponse =>
  api.get('/macro/cpi/compare', { params: { months } });
export const getOilPrice = (months: number = 24): ApiResponse =>
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
