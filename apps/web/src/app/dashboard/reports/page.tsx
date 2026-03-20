import type { Metadata } from 'next';
import {
  FileText,
  Download,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Filter,
  RefreshCw,
  FileBarChart,
  FilePieChart,
  FileSpreadsheet,
  BarChart2,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { formatDate, formatCompact } from '@/lib/utils';
import type { ReportStatus, ReportType } from '@/types';

export const metadata: Metadata = { title: 'Reports' };

// ── Mock data ─────────────────────────────────────────────────────────────────

interface MockReport {
  id: string;
  title: string;
  type: ReportType;
  status: ReportStatus;
  format: string;
  createdAt: string;
  completedAt: string | null;
  sizeBytes: number | null;
  pages: number | null;
}

const reports: MockReport[] = [
  {
    id: 'r1',
    title: 'European Tech Job Market — Q2 2024',
    type: 'market-overview',
    status: 'ready',
    format: 'pdf',
    createdAt: '2024-06-28T09:00:00Z',
    completedAt: '2024-06-28T09:04:22Z',
    sizeBytes: 2_340_000,
    pages: 48,
  },
  {
    id: 'r2',
    title: 'Salary Benchmarks — Software Engineering (DE, FR, NL)',
    type: 'salary-analysis',
    status: 'ready',
    format: 'xlsx',
    createdAt: '2024-06-25T14:30:00Z',
    completedAt: '2024-06-25T14:32:10Z',
    sizeBytes: 890_000,
    pages: null,
  },
  {
    id: 'r3',
    title: 'Top 50 Rising Skills — H1 2024',
    type: 'skill-trends',
    status: 'generating',
    format: 'pdf',
    createdAt: '2024-06-30T11:15:00Z',
    completedAt: null,
    sizeBytes: null,
    pages: null,
  },
  {
    id: 'r4',
    title: 'Company Intelligence — FAANG Europe Hiring',
    type: 'company-intelligence',
    status: 'ready',
    format: 'pdf',
    createdAt: '2024-06-20T08:00:00Z',
    completedAt: '2024-06-20T08:06:45Z',
    sizeBytes: 3_100_000,
    pages: 62,
  },
  {
    id: 'r5',
    title: 'Custom Market Analysis — FinTech Berlin',
    type: 'custom',
    status: 'failed',
    format: 'pdf',
    createdAt: '2024-06-18T16:00:00Z',
    completedAt: null,
    sizeBytes: null,
    pages: null,
  },
  {
    id: 'r6',
    title: 'Remote Work Adoption — Southern Europe 2024',
    type: 'market-overview',
    status: 'ready',
    format: 'pdf',
    createdAt: '2024-06-15T10:00:00Z',
    completedAt: '2024-06-15T10:05:33Z',
    sizeBytes: 1_870_000,
    pages: 36,
  },
  {
    id: 'r7',
    title: 'Salary Benchmarks — Product Management EU',
    type: 'salary-analysis',
    status: 'draft',
    format: 'xlsx',
    createdAt: '2024-06-30T07:00:00Z',
    completedAt: null,
    sizeBytes: null,
    pages: null,
  },
];

const templates = [
  {
    icon: BarChart2,
    color: 'text-primary-600',
    bg: 'bg-primary-50',
    title: 'Market Overview',
    description: 'Comprehensive snapshot of job volumes, trends and sentiment',
    time: '~5 min',
  },
  {
    icon: FileBarChart,
    color: 'text-accent-600',
    bg: 'bg-accent-50',
    title: 'Salary Analysis',
    description: 'P10–P90 benchmarks by role, country and experience level',
    time: '~3 min',
  },
  {
    icon: FilePieChart,
    color: 'text-success-600',
    bg: 'bg-success-50',
    title: 'Skill Trends Report',
    description: 'Rising and declining skills with growth velocity scores',
    time: '~4 min',
  },
  {
    icon: FileSpreadsheet,
    color: 'text-warning-600',
    bg: 'bg-warning-50',
    title: 'Custom Report',
    description: 'Build a fully customised report with your own filters',
    time: '~6 min',
  },
];

// ── Status helpers ────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: ReportStatus }) {
  switch (status) {
    case 'ready':
      return (
        <Badge variant="subtle-success" size="sm">
          <CheckCircle2 className="h-3 w-3" />
          Ready
        </Badge>
      );
    case 'generating':
      return (
        <Badge variant="subtle-primary" size="sm">
          <Loader2 className="h-3 w-3 animate-spin" />
          Generating
        </Badge>
      );
    case 'failed':
      return (
        <Badge variant="subtle-error" size="sm">
          <AlertCircle className="h-3 w-3" />
          Failed
        </Badge>
      );
    case 'draft':
      return (
        <Badge variant="subtle-default" size="sm">
          <Clock className="h-3 w-3" />
          Draft
        </Badge>
      );
    default:
      return <Badge variant="outline" size="sm">{status}</Badge>;
  }
}

function TypeIcon({ type }: { type: ReportType }) {
  switch (type) {
    case 'market-overview':      return <BarChart2 className="h-4 w-4 text-primary-500" />;
    case 'salary-analysis':      return <FileBarChart className="h-4 w-4 text-accent-500" />;
    case 'skill-trends':         return <FilePieChart className="h-4 w-4 text-success-500" />;
    case 'company-intelligence': return <FileText className="h-4 w-4 text-warning-500" />;
    default:                     return <FileText className="h-4 w-4 text-secondary-400" />;
  }
}

function typeLabel(type: ReportType): string {
  const map: Record<ReportType, string> = {
    'market-overview':      'Market Overview',
    'salary-analysis':      'Salary Analysis',
    'skill-trends':         'Skill Trends',
    'company-intelligence': 'Company Intelligence',
    'custom':               'Custom',
  };
  return map[type] ?? type;
}

function fileSize(bytes: number | null): string {
  if (!bytes) return '—';
  return bytes > 1_000_000
    ? `${(bytes / 1_000_000).toFixed(1)} MB`
    : `${Math.round(bytes / 1000)} KB`;
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ReportsPage() {
  const readyCount     = reports.filter((r) => r.status === 'ready').length;
  const generatingCount = reports.filter((r) => r.status === 'generating').length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Report Center</h1>
          <p className="mt-0.5 text-sm text-secondary-500">
            Generate, manage and export AI-powered market intelligence reports
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-3.5 w-3.5" />
            Filter
          </Button>
          <Button size="sm">
            <Plus className="h-3.5 w-3.5" />
            New report
          </Button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Total reports',   value: reports.length,  color: 'text-secondary-900' },
          { label: 'Ready',           value: readyCount,       color: 'text-success-600' },
          { label: 'Generating',      value: generatingCount,  color: 'text-primary-600' },
          { label: 'Storage used',    value: '12.4 MB',        color: 'text-secondary-900' },
        ].map((s) => (
          <Card key={s.label} padding="md" className="text-center">
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="mt-0.5 text-xs text-secondary-500">{s.label}</p>
          </Card>
        ))}
      </div>

      {/* Report templates */}
      <div>
        <h2 className="mb-4 text-base font-semibold text-secondary-900">Quick Start Templates</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {templates.map((t) => {
            const Icon = t.icon;
            return (
              <Card
                key={t.title}
                hover
                padding="md"
                className="group cursor-pointer"
              >
                <div className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${t.bg} transition-transform duration-200 group-hover:scale-110`}>
                  <Icon className={`h-5 w-5 ${t.color}`} />
                </div>
                <h3 className="text-sm font-semibold text-secondary-900">{t.title}</h3>
                <p className="mt-1 text-xs text-secondary-500 leading-relaxed">{t.description}</p>
                <p className="mt-2 text-xs text-secondary-400 flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {t.time} to generate
                </p>
                <Button variant="ghost" size="xs" className="mt-3 w-full justify-between">
                  Use template
                </Button>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Reports list */}
      <Card className="p-0">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>My Reports</CardTitle>
              <CardDescription>{reports.length} reports · Sorted by latest</CardDescription>
            </div>
            <Button variant="ghost" size="sm">
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-secondary-100 text-xs font-medium text-secondary-400">
                  <th className="pb-3 text-left">Report</th>
                  <th className="pb-3 text-left">Type</th>
                  <th className="pb-3 text-center">Status</th>
                  <th className="pb-3 text-right">Size</th>
                  <th className="pb-3 text-right">Pages</th>
                  <th className="pb-3 text-right">Created</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-secondary-50">
                {reports.map((r) => (
                  <tr key={r.id} className="group hover:bg-secondary-50/50 transition-colors">
                    <td className="py-3">
                      <div className="flex items-center gap-2.5 max-w-xs">
                        <TypeIcon type={r.type} />
                        <span className="font-medium text-secondary-800 truncate text-xs">
                          {r.title}
                        </span>
                      </div>
                    </td>
                    <td className="py-3">
                      <span className="text-xs text-secondary-500">{typeLabel(r.type)}</span>
                    </td>
                    <td className="py-3 text-center">
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="py-3 text-right tabular-nums text-xs text-secondary-500">
                      {fileSize(r.sizeBytes)}
                    </td>
                    <td className="py-3 text-right tabular-nums text-xs text-secondary-500">
                      {r.pages ?? '—'}
                    </td>
                    <td className="py-3 text-right text-xs text-secondary-400">
                      {formatDate(r.createdAt, { month: 'short', day: 'numeric' })}
                    </td>
                    <td className="py-3 text-right">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {r.status === 'ready' && (
                          <Button variant="ghost" size="icon-sm" title="Download">
                            <Download className="h-3.5 w-3.5" />
                          </Button>
                        )}
                        {r.status === 'failed' && (
                          <Button variant="ghost" size="icon-sm" title="Retry">
                            <RefreshCw className="h-3.5 w-3.5" />
                          </Button>
                        )}
                        {r.status === 'draft' && (
                          <Button variant="ghost" size="icon-sm" title="Generate">
                            <Loader2 className="h-3.5 w-3.5" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
