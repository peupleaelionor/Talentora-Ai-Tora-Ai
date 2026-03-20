import type { Metadata } from 'next';
import { Briefcase, TrendingUp, Filter, Download, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { MetricCard } from '@/components/dashboard/metric-card';
import { TrendChart } from '@/components/dashboard/trend-chart';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import type { TimeSeries } from '@/types';

export const metadata: Metadata = { title: 'Job Trends' };

// ── Mock data ─────────────────────────────────────────────────────────────────

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function ts(name: string, base: number, id: string, color: string): TimeSeries {
  return {
    id, name, color,
    data: months.map((m, i) => ({
      date: m,
      value: Math.round(base + Math.sin(i * 0.8 + Number(id)) * base * 0.15 + i * base * 0.025),
    })),
  };
}

const sectorSeries: TimeSeries[] = [
  ts('Software Eng.', 820_000, '1', '#4f46e5'),
  ts('Data & AI',     410_000, '2', '#7c3aed'),
  ts('Product',       185_000, '3', '#0ea5e9'),
  ts('Sales',         340_000, '4', '#16a34a'),
];

const contractSeries: TimeSeries[] = [
  ts('Full-time',  700_000, '5', '#4f46e5'),
  ts('Contract',   200_000, '6', '#7c3aed'),
  ts('Freelance',  80_000,  '7', '#f59e0b'),
  ts('Internship', 40_000,  '8', '#0ea5e9'),
];

const workModeSeries: TimeSeries[] = [
  ts('On-site', 450_000, '9',  '#4f46e5'),
  ts('Remote',  320_000, '10', '#7c3aed'),
  ts('Hybrid',  500_000, '11', '#16a34a'),
];

const hotRoles = [
  { role: 'AI/ML Engineer',         count: 42_800, change: 68.4, countries: ['🇩🇪','🇫🇷','🇳🇱'] },
  { role: 'Data Engineer',          count: 38_200, change: 41.2, countries: ['🇩🇪','🇵🇱','🇸🇪'] },
  { role: 'Backend Engineer (Rust)', count: 12_100, change: 38.7, countries: ['🇩🇪','🇳🇱','🇫🇷'] },
  { role: 'MLOps Engineer',         count: 8_900,  change: 35.1, countries: ['🇬🇧','🇩🇪','🇳🇱'] },
  { role: 'Platform Engineer',      count: 19_400, change: 28.6, countries: ['🇩🇪','🇮🇪','🇳🇱'] },
  { role: 'Product Designer',       count: 24_300, change: 22.3, countries: ['🇫🇷','🇪🇸','🇩🇪'] },
  { role: 'Revenue Operations',     count: 15_700, change: 19.8, countries: ['🇬🇧','🇩🇪','🇫🇷'] },
  { role: 'Security Engineer',      count: 18_100, change: 17.2, countries: ['🇩🇪','🇫🇷','🇸🇪'] },
];

const declining = [
  { role: 'QA Engineer (manual)', change: -18.4 },
  { role: 'SAP Consultant',       change: -12.1 },
  { role: 'Data Entry Operator',  change: -28.7 },
  { role: 'Help Desk (L1)',       change: -22.3 },
];

// ── Page ──────────────────────────────────────────────────────────────────────

export default function JobTrendsPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Job Trends</h1>
          <p className="mt-0.5 text-sm text-secondary-500">
            European job market dynamics · Updated daily
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-3.5 w-3.5" />
            Filters
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-3.5 w-3.5" />
            Export
          </Button>
          <Button size="sm" asChild>
            <Link href="/dashboard/reports">
              Generate report <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Active Listings"  value={4_823_100} format="number" changePercent={12.4} icon={Briefcase} />
        <MetricCard title="New This Week"          value={196_800}   format="number" changePercent={8.2}  icon={TrendingUp} iconColor="text-accent-600" iconBg="bg-accent-50" />
        <MetricCard title="Avg. Time to Fill"      value="28d"       trendDirection="down" changePercent={-4.3} trendPositive={false} icon={Briefcase} iconColor="text-success-600" iconBg="bg-success-50" />
        <MetricCard title="Unique Employers"       value={98_700}    format="number" changePercent={6.8}  icon={Briefcase} iconColor="text-warning-600" iconBg="bg-warning-50" />
      </div>

      {/* Chart — sector trends */}
      <TrendChart
        title="Job Volume by Sector"
        subtitle="Monthly active listings across top sectors"
        type="area"
        series={sectorSeries}
        height={300}
        valueFormat="number"
      />

      {/* Two charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <TrendChart
          title="By Contract Type"
          subtitle="Monthly breakdown by employment type"
          type="line"
          series={contractSeries}
          height={240}
          valueFormat="number"
        />
        <TrendChart
          title="By Work Mode"
          subtitle="On-site, remote and hybrid trends"
          type="bar"
          series={workModeSeries}
          height={240}
          valueFormat="number"
        />
      </div>

      {/* Hot roles + declining */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 p-0">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Fastest-Growing Roles</CardTitle>
                <CardDescription>Year-over-year posting growth</CardDescription>
              </div>
              <Badge variant="subtle-success" size="sm">YoY</Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-secondary-100 text-xs font-medium text-secondary-400">
                    <th className="pb-2 text-left">Role</th>
                    <th className="pb-2 text-right">Open positions</th>
                    <th className="pb-2 text-right">Growth</th>
                    <th className="pb-2 text-right">Top markets</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-secondary-50">
                  {hotRoles.map((r) => (
                    <tr key={r.role} className="hover:bg-secondary-50/50 transition-colors">
                      <td className="py-2.5 font-medium text-secondary-800">{r.role}</td>
                      <td className="py-2.5 text-right text-secondary-600 tabular-nums">
                        {(r.count / 1000).toFixed(1)}k
                      </td>
                      <td className="py-2.5 text-right">
                        <span className="text-success-600 font-semibold">+{r.change}%</span>
                      </td>
                      <td className="py-2.5 text-right">{r.countries.join(' ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card className="p-0">
          <CardHeader>
            <CardTitle>Declining Roles</CardTitle>
            <CardDescription>Roles with falling demand YoY</CardDescription>
          </CardHeader>
          <CardContent className="pt-0 space-y-3">
            {declining.map((r) => (
              <div key={r.role} className="flex items-center justify-between rounded-lg bg-error-50 px-3 py-2.5">
                <span className="text-sm text-secondary-700">{r.role}</span>
                <span className="text-sm font-semibold text-error-600">{r.change}%</span>
              </div>
            ))}
            <p className="text-xs text-secondary-400 mt-4 leading-relaxed">
              Roles are classified as declining when 3-month rolling average drops &gt;10% YoY.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
