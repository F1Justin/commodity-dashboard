/**
 * 布局组件 - 深色主题
 */
import Link from 'next/link';
import { useRouter } from 'next/router';
import { ReactNode } from 'react';
import {
  LayoutDashboard,
  Calculator,
  LineChart,
  Globe2,
  Download,
  Building2,
} from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { href: '/', label: '仪表盘', icon: LayoutDashboard },
  { href: '/calculator', label: '溢价率计算器', icon: Calculator },
  { href: '/charts', label: '归一化图表', icon: LineChart },
  { href: '/macro', label: '宏观数据', icon: Globe2 },
  { href: '/export', label: '数据导出', icon: Download },
];

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-[#0f1419]">
      {/* 顶部导航 */}
      <header className="bg-[#1a1f2e] border-b border-[#2a3441] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">大宗商品战情室</h1>
            </div>

            {/* 导航链接 */}
            <nav className="flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`nav-link ${
                      router.pathname === item.href ? 'active' : ''
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="hidden md:inline">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* 底部 */}
      <footer className="bg-[#1a1f2e] border-t border-[#2a3441] py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
          大宗商品战情室 v1.0.0 | 数据来源: AkShare
        </div>
      </footer>
    </div>
  );
}
