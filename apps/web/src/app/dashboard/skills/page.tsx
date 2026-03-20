import type { Metadata } from 'next';
import { Brain, TrendingUp, TrendingDown, Filter, Download, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { MetricCard } from '@/components/dashboard/metric-card';
import { TrendChart } from '@/components/dashboard/trend-chart';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import type { TimeSeries } from '@/types';

export const metadata: Metadata = { title: 'Skill Demand' };

// ── Mock data ─────────────────────────────────────────────────────────────────

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function ts(name: string, base: number, id: string, color: string): TimeSeries {
  return {
    id, name, color,
    data: months.map((m, i) => ({
      date: m,
      value: Math.round(base + Math.sin(i * 0.9 + Number(id) * 0.3) * base * 0.18 + i * base * 0.04),
    })),
  };
}

const topSkillsSeries: TimeSeries[] = [
  ts('Python',     95_000, '1', '#4f46e5'),
  ts('TypeScript', 72_000, '2', '#7c3aed'),
  ts('Rust',       18_000, '3', '#0ea5e9'),
  ts('Go',         34_000, '4', '#16a34a'),
  ts('Kubernetes', 48_000, '5', '#f59e0b'),
];

const categorySeries: TimeSeries[] = [
  ts('Cloud',    120_000, '6', '#4f46e5'),
  ts('AI/ML',    90_000,  '7', '#7c3aed'),
  ts('Security', 65_000,  '8', '#ef4444'),
  ts('DevOps',   80_000,  '9', '#0ea5e9'),
];

const skills = [
  { name: 'Python',      category: 'Programming', score: 98, jobs: 124_000, growth: 18.3, premium: 12.4 },
  { name: 'TypeScript',  category: 'Programming', score: 94, jobs: 98_000,  growth: 24.1, premium: 14.2 },
  { name: 'Kubernetes',  category: 'DevOps',      score: 91, jobs: 78_000,  growth: 31.6, premium: 18.7 },
  { name: 'LLM/GenAI',   category: 'AI/ML',       score: 89, jobs: 42_000,  growth: 182.4, premium: 28.3 },
  { name: 'Terraform',   category: 'DevOps',      score: 87, jobs: 62_000,  growth: 29.8, premium: 16.1 },
  { name: 'Rust',        category: 'Programming', score: 85, jobs: 18_000,  growth: 42.7, premium: 22.5 },
  { name: 'AWS',         category: 'Cloud',       score: 92, jobs: 110_000, growth: 11.2, premium: 11.8 },
  { name: 'React',       category: 'Frontend',    score: 88, jobs: 89_000,  growth: 8.4,  premium: 9.2  },
  { name: 'dbt',         category: 'Data',        score: 82, jobs: 24_000,  growth: 38.9, premium: 15.6 },
  { name: 'PyTorch',     category: 'AI/ML',       score: 84, jobs: 32_000,  growth: 54.3, premium: 24.7 },
];

const emerging = [
  { name: 'Agentic AI',      growth: 312, badge: 'Explosive' },
  { name: 'RAG / LangChain', growth: 241, badge: 'Hot' },
  { name: 'Rust',            growth: 43,  badge: 'Rising' },
  { name: 'eBPF',            growth: 38,  badge: 'Rising' },
  { name: 'Temporal.io',     growth: 31,  badge: 'Rising' },
];

const declining2 = [
  { name: 'Perl',       change: -38 },
  { name: 'CoffeeScript', change: -42 },
  { name: 'COBOL',      change: -29 },
  { name: 'Flash/Flex', change: -71 },
];

const categoryColors: Record<string, string> = {
  Programming: 'bg-primary-100 text-primary-700',
  DevOps:      'bg-warning-100 text-warning-700',
  'AI/ML':     'bg-accent-100 text-accent-700',
  Cloud:       'bg-sky-100 text-sky-700',
  Frontend:    'bg-teal-100 text-teal-700',
  Data:        'bg-success-100 text-success-700',
};

// ── Page ──────────────────────────────────────────────────────────────────────

export default function SkillsPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Skill Demand</h1>
          <p className="mt-0.5 text-sm text-secondary-500">
            Real-time skill intelligence across European job postings
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
        <MetricCard title="Skills Tracked"       value={10_240}  format="number" trendDirection="stable" period="Taxonomy v2.4" icon={Brain} />
        <MetricCard title="Fastest-Growing Skill" value="LLM/GenAI" changePercent={182.4} trendDirection="up" icon={TrendingUp} iconColor="text-accent-600" iconBg="bg-accent-50" badge="🔥" />
        <MetricCard title="Avg. Salary Premium"  value={14.8}   format="percent" changePercent={1.2} icon={Brain} iconColor="text-success-600" iconBg="bg-success-50" />
        <MetricCard title="New Skills (30d)"     value={42}      format="raw"    changePercent={18.2} trendDirection="up" icon={TrendingUp} iconColor="text-warning-600" iconBg="bg-warning-50" />
      </div>

      {/* Skill demand trends chart */}
      <TrendChart
        title="Top 5 Skills — Demand Trend"
        subtitle="Monthly job postings mentioning each skill"
        type="line"
        series={topSkillsSeries}
        height={300}
        valueFormat="number"
        showDots
      />

      {/* Skills table */}
      <Card className="p-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Skill Leaderboard</CardTitle>
              <CardDescription>Ranked by composite demand score</CardDescription>
            </div>
            <Badge variant="subtle-primary" size="sm">Updated daily</Badge>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-secondary-100 text-xs font-medium text-secondary-400">
                  <th className="pb-3 text-left w-6">#</th>
                  <th className="pb-3 text-left">Skill</th>
                  <th className="pb-3 text-left">Category</th>
                  <th className="pb-3 text-right">Demand Score</th>
                  <th className="pb-3 text-right">Open Roles</th>
                  <th className="pb-3 text-right">YoY Growth</th>
                  <th className="pb-3 text-right">Salary Premium</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-secondary-50">
                {skills.map((skill, i) => (
                  <tr key={skill.name} className="hover:bg-secondary-50/50 transition-colors">
                    <td className="py-3 text-secondary-400 text-xs">{i + 1}</td>
                    <td className="py-3 font-semibold text-secondary-900">{skill.name}</td>
                    <td className="py-3">
                      <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${categoryColors[skill.category] ?? 'bg-secondary-100 text-secondary-600'}`}>
                        {skill.category}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="h-1.5 w-16 rounded-full bg-secondary-100">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-primary-500 to-accent-500"
                            style={{ width: `${skill.score}%` }}
                          />
                        </div>
                        <span className="tabular-nums text-secondary-700 text-xs">{skill.score}</span>
                      </div>
                    </td>
                    <td className="py-3 text-right tabular-nums text-secondary-600">
                      {(skill.jobs / 1000).toFixed(0)}k
                    </td>
                    <td className="py-3 text-right">
                      <span className="font-semibold text-success-600 tabular-nums">+{skill.growth}%</span>
                    </td>
                    <td className="py-3 text-right">
                      <span className="text-primary-600 font-medium tabular-nums">+{skill.premium}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Bottom row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Category trends */}
        <div className="lg:col-span-2">
          <TrendChart
            title="Skill Category Trends"
            subtitle="Cloud, AI/ML, Security and DevOps demand"
            type="area"
            series={categorySeries}
            height={240}
            valueFormat="number"
          />
        </div>

        {/* Emerging + declining */}
        <div className="space-y-4">
          <Card className="p-0">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Emerging Skills</CardTitle>
            </CardHeader>
            <CardContent className="pt-0 space-y-2">
              {emerging.map((s) => (
                <div key={s.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-3.5 w-3.5 text-success-500 shrink-0" />
                    <span className="text-sm text-secondary-800">{s.name}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-semibold text-success-600">+{s.growth}%</span>
                    <Badge
                      variant={s.badge === 'Explosive' ? 'error' : s.badge === 'Hot' ? 'warning' : 'subtle-success'}
                      size="xs"
                    >
                      {s.badge}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="p-0">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Declining Skills</CardTitle>
            </CardHeader>
            <CardContent className="pt-0 space-y-2">
              {declining2.map((s) => (
                <div key={s.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingDown className="h-3.5 w-3.5 text-error-400 shrink-0" />
                    <span className="text-sm text-secondary-600">{s.name}</span>
                  </div>
                  <span className="text-xs font-semibold text-error-500">{s.change}%</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
