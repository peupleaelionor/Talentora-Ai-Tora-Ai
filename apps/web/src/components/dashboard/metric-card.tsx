import * as React from 'react';
import { TrendingUp, TrendingDown, Minus, type LucideIcon } from 'lucide-react';
import { cn, formatCompact, formatCurrency, formatPercent } from '@/lib/utils';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

type MetricFormat = 'number' | 'currency' | 'percent' | 'raw';
type TrendDirection = 'up' | 'down' | 'stable';

interface MetricCardProps {
  title: string;
  value: number | string;
  format?: MetricFormat;
  currency?: string;
  change?: number;
  changePercent?: number;
  trendDirection?: TrendDirection;
  trendPositive?: boolean; // is "up" a good thing? (default true)
  period?: string;
  icon?: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  description?: string;
  badge?: string;
  loading?: boolean;
  className?: string;
}

function TrendIcon({
  direction,
  positive,
  className,
}: {
  direction: TrendDirection;
  positive: boolean;
  className?: string;
}) {
  if (direction === 'up')
    return <TrendingUp className={cn('h-3.5 w-3.5', className)} />;
  if (direction === 'down')
    return <TrendingDown className={cn('h-3.5 w-3.5', className)} />;
  return <Minus className={cn('h-3.5 w-3.5', className)} />;
}

function formatValue(
  value: number | string,
  format: MetricFormat,
  currency: string
): string {
  if (typeof value === 'string') return value;
  switch (format) {
    case 'currency':
      return formatCurrency(value, currency);
    case 'percent':
      return formatPercent(value);
    case 'number':
      return formatCompact(value);
    default:
      return String(value);
  }
}

export function MetricCard({
  title,
  value,
  format = 'number',
  currency = 'EUR',
  change,
  changePercent,
  trendDirection,
  trendPositive = true,
  period = 'vs last month',
  icon: Icon,
  iconColor = 'text-primary-600',
  iconBg = 'bg-primary-50',
  description,
  badge,
  loading = false,
  className,
}: MetricCardProps) {
  const direction: TrendDirection =
    trendDirection ??
    (changePercent !== undefined
      ? changePercent > 0
        ? 'up'
        : changePercent < 0
        ? 'down'
        : 'stable'
      : 'stable');

  const isGood =
    direction === 'stable' ? null : trendPositive ? direction === 'up' : direction === 'down';

  const trendColor =
    isGood === null
      ? 'text-secondary-500'
      : isGood
      ? 'text-success-600'
      : 'text-error-600';

  const trendBg =
    isGood === null
      ? 'bg-secondary-50'
      : isGood
      ? 'bg-success-50'
      : 'bg-error-50';

  if (loading) {
    return (
      <Card className={cn('p-6', className)}>
        <div className="flex items-start justify-between">
          <div className="h-4 w-32 animate-pulse rounded bg-secondary-100" />
          <div className="h-10 w-10 animate-pulse rounded-xl bg-secondary-100" />
        </div>
        <div className="mt-4 h-8 w-24 animate-pulse rounded bg-secondary-100" />
        <div className="mt-3 h-4 w-36 animate-pulse rounded bg-secondary-100" />
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        'p-6 hover:shadow-md hover:-translate-y-0.5 cursor-default transition-all duration-200',
        className
      )}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-secondary-500">{title}</p>
          {badge && (
            <Badge variant="subtle-primary" size="xs" className="mt-1">
              {badge}
            </Badge>
          )}
        </div>
        {Icon && (
          <div
            className={cn(
              'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl',
              iconBg
            )}
          >
            <Icon className={cn('h-5 w-5', iconColor)} />
          </div>
        )}
      </div>

      {/* Value */}
      <p className="mt-3 stat-number text-3xl font-bold text-secondary-900 leading-none">
        {formatValue(value, format, currency)}
      </p>

      {/* Trend */}
      {(changePercent !== undefined || change !== undefined) && (
        <div className="mt-3 flex items-center gap-2">
          <span
            className={cn(
              'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
              trendBg,
              trendColor
            )}
          >
            <TrendIcon direction={direction} positive={trendPositive} />
            {changePercent !== undefined
              ? `${Math.abs(changePercent).toFixed(1)}%`
              : change !== undefined
              ? formatCompact(Math.abs(change))
              : null}
          </span>
          <span className="text-xs text-secondary-400">{period}</span>
        </div>
      )}

      {/* Description */}
      {description && (
        <p className="mt-2 text-xs text-secondary-400 leading-relaxed">
          {description}
        </p>
      )}
    </Card>
  );
}
