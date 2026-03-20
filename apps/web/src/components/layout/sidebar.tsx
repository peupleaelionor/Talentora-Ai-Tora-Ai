'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Briefcase,
  Brain,
  DollarSign,
  FileText,
  Settings,
  Bell,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  User,
  ChevronsUpDown,
  LogOut,
  Building2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface SidebarItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  badgeVariant?: 'subtle-primary' | 'subtle-success' | 'subtle-warning';
}

interface SidebarSection {
  title?: string;
  items: SidebarItem[];
}

const sections: SidebarSection[] = [
  {
    items: [
      { label: 'Overview',    href: '/dashboard',          icon: LayoutDashboard },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { label: 'Job Trends',  href: '/dashboard/jobs',     icon: Briefcase },
      { label: 'Skills',      href: '/dashboard/skills',   icon: Brain,      badge: 'New', badgeVariant: 'subtle-primary' },
      { label: 'Salary',      href: '/dashboard/salary',   icon: DollarSign },
      { label: 'Reports',     href: '/dashboard/reports',  icon: FileText },
    ],
  },
  {
    title: 'Account',
    items: [
      { label: 'Notifications', href: '/dashboard/notifications', icon: Bell },
      { label: 'Settings',     href: '/dashboard/settings',  icon: Settings },
      { label: 'Help',         href: '/help',                icon: HelpCircle },
    ],
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = React.useState(false);

  return (
    <aside
      className={cn(
        'relative flex h-full flex-col border-r border-secondary-200 bg-white',
        'transition-all duration-300 ease-smooth',
        collapsed ? 'w-16' : 'w-64',
        className
      )}
    >
      {/* Logo */}
      <div className={cn(
        'flex h-16 items-center border-b border-secondary-100 px-4',
        collapsed ? 'justify-center' : 'gap-3'
      )}>
        <Link
          href="/dashboard"
          className="flex items-center gap-2.5 font-heading font-bold text-xl tracking-tight"
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-primary shadow-primary-sm">
            <BarChart3 className="h-4 w-4 text-white" />
          </div>
          {!collapsed && (
            <span className="text-secondary-900 text-base">
              Talentora <span className="text-gradient">AI</span>
            </span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 scrollbar-hide">
        {sections.map((section, sIdx) => (
          <div key={sIdx} className={cn('px-3', sIdx > 0 && 'mt-4')}>
            {section.title && !collapsed && (
              <p className="mb-1 px-2 text-[11px] font-semibold uppercase tracking-widest text-secondary-400">
                {section.title}
              </p>
            )}
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      title={collapsed ? item.label : undefined}
                      className={cn(
                        'group flex items-center gap-3 rounded-lg px-2 py-2.5',
                        'text-sm font-medium transition-all duration-150',
                        isActive
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900',
                        collapsed && 'justify-center px-0'
                      )}
                    >
                      <Icon
                        className={cn(
                          'h-4.5 w-4.5 shrink-0 transition-colors',
                          isActive
                            ? 'text-primary-600'
                            : 'text-secondary-400 group-hover:text-secondary-600'
                        )}
                      />
                      {!collapsed && (
                        <>
                          <span className="flex-1 truncate">{item.label}</span>
                          {item.badge && (
                            <Badge
                              variant={item.badgeVariant ?? 'subtle-primary'}
                              size="xs"
                            >
                              {item.badge}
                            </Badge>
                          )}
                        </>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Org / User card */}
      {!collapsed && (
        <div className="border-t border-secondary-100 p-3">
          <button className="flex w-full items-center gap-3 rounded-lg px-2 py-2 hover:bg-secondary-50 transition-colors group">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary-100 group-hover:bg-secondary-200 transition-colors">
              <Building2 className="h-4 w-4 text-secondary-500" />
            </div>
            <div className="flex-1 text-left min-w-0">
              <p className="truncate text-sm font-medium text-secondary-900">Acme Corp</p>
              <p className="truncate text-xs text-secondary-400">Pro plan</p>
            </div>
            <ChevronsUpDown className="h-4 w-4 text-secondary-400 shrink-0" />
          </button>

          <div className="mt-1 flex items-center gap-3 rounded-lg px-2 py-2">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-primary text-white text-xs font-bold">
              JD
            </div>
            <div className="flex-1 min-w-0">
              <p className="truncate text-sm font-medium text-secondary-900">Jane Doe</p>
              <p className="truncate text-xs text-secondary-400">jane@acme.com</p>
            </div>
            <button
              title="Sign out"
              className="text-secondary-400 hover:text-secondary-600 transition-colors rounded-md p-1 hover:bg-secondary-100"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className={cn(
          'absolute -right-3 top-20 flex h-6 w-6 items-center justify-center',
          'rounded-full border border-secondary-200 bg-white shadow-xs',
          'text-secondary-400 hover:text-secondary-600 hover:shadow-sm',
          'transition-all duration-200 z-10'
        )}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </button>
    </aside>
  );
}
