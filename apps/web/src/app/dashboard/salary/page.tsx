import type { Metadata } from 'next';
import { DollarSign, TrendingUp, Globe2, Filter, Download, ChevronRight } from 'lucide-react';
import { MetricCard } from '@/components/dashboard/metric-card';
import { TrendChart } from '@/components/dashboard/trend-chart';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import type { TimeSeries } from '@/types';

export const metadata: Metadata = { title: 'Salary Analysis' };

// ── Mock data ─────────────────────────────────────────────────────────────────

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function ts(name: string, base: number, id: string, color: string): TimeSeries {
  return {
    id, name, color,
    data: months.map((m, i) => ({
      date: m,
      value: Math.round(base + i * base * 0.008 + Math.sin(i * 0.5 + Number(id)) * 1_200),
    })),
  };
}

const salaryTrendSeries: TimeSeries[] = [
  ts('Software Eng.', 78_000, '1', '#4f46e5'),
  ts('Data Scientist', 82_000, '2', '#7c3aed'),
  ts('Product Manager', 74_000, '3', '#0ea5e9'),
  ts('DevOps / SRE',    76_000, '4', '#16a34a'),
];

const countryCompareSeries: TimeSeries[] = [
  ts('Switzerland', 98_000, '5', '#4f46e5'),
  ts('Germany',     72_000, '6', '#7c3aed'),
  ts('France',      62_000, '7', '#0ea5e9'),
  ts('Spain',       48_000, '8', '#16a34a'),
  ts('Poland',      38_000, '9', '#f59e0b'),
];

const benchmarks = [
  { role: 'Staff Engineer',       p10: 90,  p25: 110, median: 130, p75: 155, p90: 185, currency: '€k' },
  { role: 'ML Engineer',          p10: 75,  p25: 95,  median: 118, p75: 145, p90: 175, currency: '€k' },
  { role: 'Data Engineer',        p10: 65,  p25: 80,  median: 98,  p75: 118, p90: 142, currency: '€k' },
  { role: 'Product Manager',      p10: 60,  p25: 74,  median: 90,  p75: 112, p90: 138, currency: '€k' },
  { role: 'Backend Engineer',     p10: 55,  p25: 70,  median: 86,  p75: 104, p90: 128, currency: '€k' },
  { role: 'Frontend Engineer',    p10: 50,  p25: 64,  median: 78,  p75: 96,  p90: 118, currency: '€k' },
  { role: 'DevOps / SRE',         p10: 58,  p25: 72,  median: 88,  p75: 108, p90: 132, currency: '€k' },
  { role: 'Security Engineer',    p10: 62,  p25: 78,  median: 95,  p75: 116, p90: 140, currency: '€k' },
];

const countryData = [
  { name: 'Switzerland', flag: '🇨🇭', median: 98_000, change: 4.2 },
  { name: 'Denmark',     flag: '🇩🇰', median: 84_000, change: 3.8 },
  { name: 'Netherlands', flag: '🇳🇱', median: 78_000, change: 4.9 },
  { name: 'Germany',     flag: '🇩🇪', median: 72_000, change: 3.1 },
  { name: 'Sweden',      flag: '🇸🇪', median: 68_000, change: 5.2 },
  { name: 'France',      flag: '🇫🇷', median: 62_000, change: 2.7 },
  { name: 'Ireland',     flag: '🇮🇪', median: 74_000, change: 4.1 },
  { name: 'Spain',       flag: '🇪🇸', median: 48_000, change: 6.3 },
  { name: 'Poland',      flag: '🇵🇱', median: 38_000, change: 9.8 },
  { name: 'Portugal',    flag: '🇵🇹', median: 36_000, change: 7.4 },
];

// ── Percentile bar component ──────────────────────────────────────────────────

function PercentileBar({
  p10, p25, median, p75, p90, max,
}: { p10: number; p25: number; median: number; p75: number; p90: number; max: number }) {
  const toW = (v: number) => `${(v / max) * 100}%`;
  return (
    <div className="relative h-4 rounded-full bg-secondary-100 overflow-hidden">
      {/* IQR band */}
      <div
        className="absolute top-0 h-full rounded-full bg-primary-200"
        style={{ left: toW(p25), width: `calc(${toW(p75)} - ${toW(p25)})` }}
      />
      {/* Median marker */}
      <div
        className="absolute top-0 h-full w-0.5 bg-primary-600"
        style={{ left: toW(median) }}
      />
      {/* P10 tick */}
      <div className="absolute top-1 h-2 w-0.5 bg-secondary-400 rounded-full" style={{ left: toW(p10) }} />
      {/* P90 tick */}
      <div className="absolute top-1 h-2 w-0.5 bg-secondary-400 rounded-full" style={{ left: toW(p90) }} />
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function SalaryPage() {
  const maxSalary = 200;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Salary Analysis</h1>
          <p className="mt-0.5 text-sm text-secondary-500">
            Percentile-based salary data across European markets
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
        </div>
      </div>

      {/* Metrics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="EU Median Salary"         value={52_400}  format="currency" changePercent={3.1} icon={DollarSign} />
        <MetricCard title="Fastest Salary Growth"    value="Poland"  changePercent={9.8} trendDirection="up" icon={TrendingUp} iconColor="text-success-600" iconBg="bg-success-50" badge="+9.8%" />
        <MetricCard title="Tech Premium vs Avg"      value={34.2}   format="percent" changePercent={1.4} icon={DollarSign} iconColor="text-accent-600" iconBg="bg-accent-50" />
        <MetricCard title="Countries with Data"      value={52}      format="raw"     trendDirection="stable" icon={Globe2} iconColor="text-primary-600" iconBg="bg-primary-50" />
      </div>

      {/* Salary trend chart */}
      <TrendChart
        title="Median Salary Trend by Role — 2024"
        subtitle="Annual equivalent, EUR"
        type="line"
        series={salaryTrendSeries}
        height={280}
        valueFormat="currency"
        showDots
      />

      {/* Percentile benchmark table */}
      <Card className="p-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Salary Benchmarks by Role</CardTitle>
              <CardDescription>P10 · P25 · Median · P75 · P90 · Annual EUR equivalent</CardDescription>
            </div>
            <div className="flex items-center gap-3 text-xs text-secondary-500">
              <span className="flex items-center gap-1"><span className="inline-block h-3 w-3 rounded-sm bg-primary-200"/>&nbsp;IQR (P25–P75)</span>
              <span className="flex items-center gap-1"><span className="inline-block h-3 w-0.5 bg-primary-600"/>&nbsp;Median</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-secondary-100 text-xs font-medium text-secondary-400">
                  <th className="pb-3 text-left w-48">Role</th>
                  <th className="pb-3 text-right w-16">P10</th>
                  <th className="pb-3 text-right w-16">P25</th>
                  <th className="pb-3 text-right w-20 text-primary-600">Median</th>
                  <th className="pb-3 text-right w-16">P75</th>
                  <th className="pb-3 text-right w-16">P90</th>
                  <th className="pb-3 text-left pl-4 min-w-40">Distribution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-secondary-50">
                {benchmarks.map((b) => (
                  <tr key={b.role} className="hover:bg-secondary-50/50 transition-colors">
                    <td className="py-3 font-medium text-secondary-800">{b.role}</td>
                    <td className="py-3 text-right tabular-nums text-secondary-500 text-xs">{b.p10}{b.currency}</td>
                    <td className="py-3 text-right tabular-nums text-secondary-600 text-xs">{b.p25}{b.currency}</td>
                    <td className="py-3 text-right tabular-nums font-semibold text-primary-700">{b.median}{b.currency}</td>
                    <td className="py-3 text-right tabular-nums text-secondary-600 text-xs">{b.p75}{b.currency}</td>
                    <td className="py-3 text-right tabular-nums text-secondary-500 text-xs">{b.p90}{b.currency}</td>
                    <td className="py-3 pl-4">
                      <PercentileBar
                        p10={b.p10} p25={b.p25} median={b.median}
                        p75={b.p75} p90={b.p90} max={maxSalary}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-secondary-400">
            Data based on 5M+ job postings across Europe. Currency-normalised to EUR. Sample sizes ≥500 per role.
          </p>
        </CardContent>
      </Card>

      {/* Bottom row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Country comparison chart */}
        <div className="lg:col-span-2">
          <TrendChart
            title="Salary Trend by Country"
            subtitle="Median annual salary trend, EUR"
            type="line"
            series={countryCompareSeries}
            height={260}
            valueFormat="currency"
          />
        </div>

        {/* Country table */}
        <Card className="p-0">
          <CardHeader className="pb-3">
            <CardTitle>Median by Country</CardTitle>
            <CardDescription>All roles, EUR equivalent</CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            <ul className="divide-y divide-secondary-50">
              {countryData.map((c) => (
                <li key={c.name} className="flex items-center gap-3 py-2">
                  <span className="text-base">{c.flag}</span>
                  <span className="flex-1 text-sm text-secondary-800">{c.name}</span>
                  <span className="tabular-nums text-sm font-semibold text-secondary-900">
                    €{(c.median / 1000).toFixed(0)}k
                  </span>
                  <span className={`text-xs font-medium ${c.change >= 5 ? 'text-success-600' : c.change >= 3 ? 'text-primary-600' : 'text-secondary-500'}`}>
                    +{c.change}%
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
