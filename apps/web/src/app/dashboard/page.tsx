import type { Metadata } from 'next';
import {
  Briefcase,
  Brain,
  DollarSign,
  Globe2,
  ArrowRight,
  Clock,
  TrendingUp,
  Building2,
  Zap,
} from 'lucide-react';
import Link from 'next/link';
import { MetricCard } from '@/components/dashboard/metric-card';
import { TrendChart } from '@/components/dashboard/trend-chart';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { TimeSeries } from '@/types';

export const metadata: Metadata = { title: 'Overview' };

// ── Mock data ─────────────────────────────────────────────────────────────────

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function makeSeries(name: string, baseVal: number, id: string, color?: string): TimeSeries {
  return {
    id,
    name,
    color,
    data: months.map((m, i) => ({
      date: m,
      value: Math.round(baseVal + (Math.sin(i * 0.7) + Math.cos(i * 0.3)) * baseVal * 0.2 + i * baseVal * 0.03),
    })),
  };
}

const totalSeries = makeSeries('Total listings', 4_500_000, 'total', '#4f46e5');
const newSeries   = makeSeries('New today', 26_000, 'new', '#7c3aed');

const recentActivity = [
  { type: 'alert',  text: 'Python demand up 18% in Germany this week',     time: '2m ago',   icon: TrendingUp,  color: 'text-success-600', bg: 'bg-success-50' },
  { type: 'report', text: 'Q2 European Tech Report is ready to download',  time: '1h ago',   icon: Briefcase,   color: 'text-primary-600', bg: 'bg-primary-50' },
  { type: 'alert',  text: 'Rust roles in France surged 42% month-over-month', time: '3h ago', icon: Zap,        color: 'text-warning-600', bg: 'bg-warning-50' },
  { type: 'new',    text: '28,400 new job offers ingested across Europe',   time: '5h ago',   icon: Globe2,      color: 'text-accent-600',  bg: 'bg-accent-50'  },
  { type: 'update', text: 'Salary benchmark updated for 12 new roles',     time: '1d ago',   icon: DollarSign,  color: 'text-success-600', bg: 'bg-success-50' },
];

const topSectors = [
  { name: 'Software Engineering', count: 823_000, change: 14.2 },
  { name: 'Data & Analytics',     count: 412_000, change: 22.8 },
  { name: 'Product Management',   count: 187_000, change: 9.1  },
  { name: 'Sales & RevOps',       count: 341_000, change: 4.5  },
  { name: 'Finance & Accounting', count: 258_000, change: -2.3 },
  { name: 'HR & People Ops',      count: 142_000, change: 7.9  },
];

const topCountries = [
  { name: 'Germany',     flag: '🇩🇪', jobs: 921_000 },
  { name: 'France',      flag: '🇫🇷', jobs: 784_000 },
  { name: 'Netherlands', flag: '🇳🇱', jobs: 453_000 },
  { name: 'Spain',       flag: '🇪🇸', jobs: 398_000 },
  { name: 'Poland',      flag: '🇵🇱', jobs: 312_000 },
];

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DashboardOverviewPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Good morning, Jane</h1>
          <p className="mt-0.5 text-sm text-secondary-500">
            Here&apos;s what&apos;s happening across the European job market today.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="subtle-success" dot size="sm">Live data</Badge>
          <Button variant="outline" size="sm" asChild>
            <Link href="/dashboard/reports">
              Generate report
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <MetricCard
          className="xl:col-span-2"
          title="Active Job Offers"
          value={4_823_100}
          format="number"
          changePercent={12.4}
          period="vs last month"
          icon={Briefcase}
          description="Across 50+ European countries"
        />
        <MetricCard
          className="xl:col-span-2"
          title="New Listings Today"
          value={28_400}
          format="number"
          changePercent={8.2}
          period="vs yesterday"
          icon={Zap}
          iconColor="text-accent-600"
          iconBg="bg-accent-50"
        />
        <MetricCard
          className="xl:col-span-2"
          title="Median EU Salary"
          value={52_400}
          format="currency"
          changePercent={3.1}
          period="vs last year"
          icon={DollarSign}
          iconColor="text-success-600"
          iconBg="bg-success-50"
        />
        <MetricCard
          className="xl:col-span-2"
          title="Companies Hiring"
          value={98_700}
          format="number"
          changePercent={6.8}
          period="vs last month"
          icon={Building2}
          iconColor="text-warning-600"
          iconBg="bg-warning-50"
        />
        <MetricCard
          className="xl:col-span-2"
          title="Top Skill Demand"
          value="Python"
          changePercent={18.3}
          trendDirection="up"
          period="vs last month"
          icon={Brain}
          iconColor="text-accent-600"
          iconBg="bg-accent-50"
          badge="Trending"
        />
        <MetricCard
          className="xl:col-span-2"
          title="Countries Covered"
          value={52}
          format="raw"
          trendDirection="stable"
          period="No change"
          icon={Globe2}
          iconColor="text-primary-600"
          iconBg="bg-primary-50"
        />
      </div>

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <TrendChart
            title="Job Offer Volume — 2024"
            subtitle="Total active listings across all European markets"
            type="area"
            series={[totalSeries]}
            height={240}
            valueFormat="number"
            showLegend={false}
          />
        </div>
        <TrendChart
          title="Daily New Listings"
          subtitle="New postings ingested per month"
          type="bar"
          series={[newSeries]}
          height={240}
          valueFormat="number"
          showLegend={false}
        />
      </div>

      {/* Bottom grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Top sectors */}
        <Card className="p-0">
          <CardHeader className="pb-3">
            <CardTitle>Top Sectors</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-3">
              {topSectors.map((sector) => (
                <li key={sector.name} className="flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="truncate text-sm font-medium text-secondary-800">
                      {sector.name}
                    </p>
                    <p className="text-xs text-secondary-400">
                      {(sector.count / 1000).toFixed(0)}k listings
                    </p>
                  </div>
                  <span
                    className={`text-xs font-semibold ${
                      sector.change >= 0 ? 'text-success-600' : 'text-error-600'
                    }`}
                  >
                    {sector.change >= 0 ? '+' : ''}{sector.change}%
                  </span>
                </li>
              ))}
            </ul>
            <Button variant="ghost" size="sm" className="mt-4 w-full" asChild>
              <Link href="/dashboard/jobs">
                View all sectors <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Top countries */}
        <Card className="p-0">
          <CardHeader className="pb-3">
            <CardTitle>Top Markets</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-3">
              {topCountries.map((c, i) => (
                <li key={c.name} className="flex items-center gap-3">
                  <span className="text-lg">{c.flag}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-secondary-800">{c.name}</p>
                    <div className="mt-1 h-1.5 rounded-full bg-secondary-100 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-500"
                        style={{ width: `${(c.jobs / 921_000) * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-secondary-500">
                    {(c.jobs / 1000).toFixed(0)}k
                  </span>
                </li>
              ))}
            </ul>
            <Button variant="ghost" size="sm" className="mt-4 w-full" asChild>
              <Link href="/dashboard/jobs">
                View all countries <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Recent activity */}
        <Card className="p-0">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle>Recent Activity</CardTitle>
              <Badge variant="subtle-primary" size="xs">Live</Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="space-y-3">
              {recentActivity.map((item, i) => {
                const Icon = item.icon;
                return (
                  <li key={i} className="flex items-start gap-3">
                    <div className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${item.bg}`}>
                      <Icon className={`h-3.5 w-3.5 ${item.color}`} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs text-secondary-700 leading-snug">{item.text}</p>
                      <p className="mt-0.5 flex items-center gap-1 text-[10px] text-secondary-400">
                        <Clock className="h-3 w-3" />
                        {item.time}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
