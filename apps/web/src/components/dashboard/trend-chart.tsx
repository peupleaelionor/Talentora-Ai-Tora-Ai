'use client';

import * as React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  type TooltipProps,
} from 'recharts';
import { cn, formatCompact, formatCurrency } from '@/lib/utils';
import { Card } from '@/components/ui/card';
import type { TimeSeries } from '@/types';

// ── Color palette ─────────────────────────────────────────────────────────────
const CHART_COLORS = [
  '#4f46e5', // primary indigo
  '#7c3aed', // accent violet
  '#0ea5e9', // sky
  '#16a34a', // success green
  '#f59e0b', // warning amber
  '#ef4444', // error red
  '#8b5cf6', // purple
  '#06b6d4', // cyan
];

// ── Custom tooltip ────────────────────────────────────────────────────────────
function CustomTooltip({
  active,
  payload,
  label,
  valueFormat,
  currency,
}: TooltipProps<number, string> & {
  valueFormat?: 'number' | 'currency' | 'percent';
  currency?: string;
}) {
  if (!active || !payload?.length) return null;

  function fmtVal(v: number): string {
    if (valueFormat === 'currency') return formatCurrency(v, currency ?? 'EUR');
    if (valueFormat === 'percent') return `${v.toFixed(1)}%`;
    return formatCompact(v);
  }

  return (
    <div className="rounded-xl border border-secondary-200 bg-white p-3 shadow-lg">
      <p className="mb-2 text-xs font-semibold text-secondary-500">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center gap-2 text-sm">
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-secondary-600">{entry.name}:</span>
          <span className="font-semibold text-secondary-900">
            {fmtVal(entry.value as number)}
          </span>
        </div>
      ))}
    </div>
  );
}

// ── Prop types ────────────────────────────────────────────────────────────────
type ChartType = 'line' | 'area' | 'bar';

interface TrendChartProps {
  title?: string;
  subtitle?: string;
  type?: ChartType;
  series: TimeSeries[];
  height?: number;
  valueFormat?: 'number' | 'currency' | 'percent';
  currency?: string;
  showGrid?: boolean;
  showLegend?: boolean;
  showDots?: boolean;
  referenceLines?: { value: number; label?: string; color?: string }[];
  colors?: string[];
  className?: string;
  loading?: boolean;
  xAxisKey?: string;
}

// ── Shared chart data format ──────────────────────────────────────────────────
function buildChartData(series: TimeSeries[]) {
  if (!series.length) return [];
  const allDates = Array.from(
    new Set(series.flatMap((s) => s.data.map((d) => d.date)))
  ).sort();

  return allDates.map((date) => {
    const row: Record<string, unknown> = { date };
    for (const s of series) {
      const point = s.data.find((d) => d.date === date);
      row[s.name] = point?.value ?? null;
    }
    return row;
  });
}

// ── Component ─────────────────────────────────────────────────────────────────
export function TrendChart({
  title,
  subtitle,
  type = 'area',
  series,
  height = 280,
  valueFormat = 'number',
  currency = 'EUR',
  showGrid = true,
  showLegend = true,
  showDots = false,
  referenceLines = [],
  colors = CHART_COLORS,
  className,
  loading = false,
  xAxisKey = 'date',
}: TrendChartProps) {
  const data = React.useMemo(() => buildChartData(series), [series]);

  function fmtYAxis(v: number): string {
    if (valueFormat === 'currency') return formatCurrency(v, currency, 'en');
    if (valueFormat === 'percent') return `${v}%`;
    return formatCompact(v);
  }

  const axisProps = {
    tick: { fontSize: 11, fill: '#94a3b8' },
    axisLine: { stroke: '#e2e8f0' },
    tickLine: false,
  };

  if (loading) {
    return (
      <Card className={cn('p-6', className)}>
        {title && (
          <div className="mb-4">
            <div className="h-5 w-40 animate-pulse rounded bg-secondary-100" />
            {subtitle && <div className="mt-1.5 h-3 w-56 animate-pulse rounded bg-secondary-100" />}
          </div>
        )}
        <div
          className="animate-pulse rounded-lg bg-secondary-50"
          style={{ height }}
        />
      </Card>
    );
  }

  const sharedLineProps = (s: TimeSeries, idx: number) => ({
    key: s.id,
    type: 'monotone' as const,
    dataKey: s.name,
    stroke: s.color ?? colors[idx % colors.length],
    strokeWidth: 2,
    dot: showDots ? { r: 3 } : false,
    activeDot: { r: 5, strokeWidth: 0 },
  });

  const sharedAreaProps = (s: TimeSeries, idx: number) => ({
    ...sharedLineProps(s, idx),
    fill: `url(#gradient-${idx})`,
    fillOpacity: 0.15,
  });

  const gradientDefs = (
    <defs>
      {series.map((s, idx) => (
        <linearGradient
          key={s.id}
          id={`gradient-${idx}`}
          x1="0" y1="0" x2="0" y2="1"
        >
          <stop
            offset="5%"
            stopColor={s.color ?? colors[idx % colors.length]}
            stopOpacity={0.3}
          />
          <stop
            offset="95%"
            stopColor={s.color ?? colors[idx % colors.length]}
            stopOpacity={0}
          />
        </linearGradient>
      ))}
    </defs>
  );

  const sharedCartesian = (
    <>
      {showGrid && (
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
      )}
      <XAxis dataKey={xAxisKey} {...axisProps} dy={8} />
      <YAxis tickFormatter={fmtYAxis} {...axisProps} dx={-4} width={60} />
      <Tooltip
        content={
          <CustomTooltip valueFormat={valueFormat} currency={currency} />
        }
        cursor={{ stroke: '#e2e8f0', strokeWidth: 1 }}
      />
      {showLegend && series.length > 1 && (
        <Legend
          wrapperStyle={{ fontSize: 12, paddingTop: 12, color: '#64748b' }}
          iconType="circle"
          iconSize={8}
        />
      )}
      {referenceLines.map((rl) => (
        <ReferenceLine
          key={rl.value}
          y={rl.value}
          stroke={rl.color ?? '#94a3b8'}
          strokeDasharray="4 4"
          label={{ value: rl.label, fill: '#94a3b8', fontSize: 11 }}
        />
      ))}
    </>
  );

  function renderChart() {
    if (type === 'bar') {
      return (
        <BarChart data={data} barGap={4} barCategoryGap="30%">
          {sharedCartesian}
          {series.map((s, idx) => (
            <Bar
              key={s.id}
              dataKey={s.name}
              fill={s.color ?? colors[idx % colors.length]}
              radius={[4, 4, 0, 0]}
              maxBarSize={40}
            />
          ))}
        </BarChart>
      );
    }
    if (type === 'line') {
      return (
        <LineChart data={data}>
          {sharedCartesian}
          {series.map((s, idx) => (
            <Line {...sharedLineProps(s, idx)} />
          ))}
        </LineChart>
      );
    }
    // default: area
    return (
      <AreaChart data={data}>
        {gradientDefs}
        {sharedCartesian}
        {series.map((s, idx) => (
          <Area {...sharedAreaProps(s, idx)} />
        ))}
      </AreaChart>
    );
  }

  return (
    <Card className={cn('p-6', className)}>
      {(title || subtitle) && (
        <div className="mb-5">
          {title && (
            <h3 className="text-base font-semibold text-secondary-900">{title}</h3>
          )}
          {subtitle && (
            <p className="mt-0.5 text-sm text-secondary-400">{subtitle}</p>
          )}
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        {renderChart()}
      </ResponsiveContainer>
    </Card>
  );
}
