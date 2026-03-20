import type { Metadata } from 'next';
import { Bell, Search, Settings } from 'lucide-react';
import { Sidebar } from '@/components/layout/sidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

export const metadata: Metadata = {
  title: {
    default: 'Dashboard',
    template: '%s — Dashboard | Talentora AI',
  },
  description: 'Talentora AI dashboard — European job market intelligence.',
  robots: { index: false, follow: false },
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-secondary-50">
      {/* Sidebar */}
      <Sidebar className="shrink-0" />

      {/* Main area */}
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">
        {/* Top bar */}
        <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b border-secondary-200 bg-white px-6">
          {/* Search */}
          <div className="w-full max-w-sm">
            <Input
              placeholder="Search jobs, skills, companies…"
              leftIcon={<Search className="h-4 w-4" />}
              variant="ghost"
              inputSize="sm"
              aria-label="Search"
            />
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Notification bell */}
            <div className="relative">
              <Button variant="ghost" size="icon-sm" aria-label="Notifications">
                <Bell className="h-4 w-4" />
              </Button>
              <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary-600 text-[9px] font-bold text-white">
                3
              </span>
            </div>

            {/* Plan badge */}
            <Badge variant="subtle-primary" size="sm">Pro plan</Badge>

            {/* Settings */}
            <Button variant="ghost" size="icon-sm" aria-label="Settings">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
