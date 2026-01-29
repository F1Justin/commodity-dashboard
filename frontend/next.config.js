/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  async rewrites() {
    // 生产环境使用环境变量，默认指向 Docker 内部网络的 backend 服务
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? `${backendUrl}/api/:path*`
          : 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
