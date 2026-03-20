import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** Format a number as a compact string (e.g. 5000000 → "5M") */
export function formatCompact(value: number, locale = 'en-EU'): string {
  return new Intl.NumberFormat(locale, {
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 1,
  }).format(value);
}

/** Format a number with locale-aware separators */
export function formatNumber(value: number, locale = 'en-EU'): string {
  return new Intl.NumberFormat(locale).format(value);
}

/** Format currency (default EUR) */
export function formatCurrency(
  value: number,
  currency = 'EUR',
  locale = 'en-EU'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/** Format a percentage */
export function formatPercent(
  value: number,
  digits = 1,
  locale = 'en-EU'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value / 100);
}

/** Format a date in short form */
export function formatDate(
  date: Date | string,
  options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' },
  locale = 'en-EU'
): string {
  return new Intl.DateTimeFormat(locale, options).format(
    typeof date === 'string' ? new Date(date) : date
  );
}

/** Format a relative time (e.g. "3 days ago") */
export function formatRelativeTime(date: Date | string, locale = 'en-EU'): string {
  const target = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = target.getTime() - now.getTime();
  const diffSecs = Math.round(diffMs / 1000);
  const diffMins = Math.round(diffSecs / 60);
  const diffHours = Math.round(diffMins / 60);
  const diffDays = Math.round(diffHours / 24);

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

  if (Math.abs(diffDays) >= 30) return formatDate(date, undefined, locale);
  if (Math.abs(diffDays) >= 1)   return rtf.format(diffDays, 'day');
  if (Math.abs(diffHours) >= 1)  return rtf.format(diffHours, 'hour');
  if (Math.abs(diffMins) >= 1)   return rtf.format(diffMins, 'minute');
  return rtf.format(diffSecs, 'second');
}

/** Calculate percentage change between two values */
export function percentChange(current: number, previous: number): number {
  if (previous === 0) return 0;
  return ((current - previous) / previous) * 100;
}

/** Clamp a number between min and max */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/** Slugify a string for URLs */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/** Truncate a string to a max length with ellipsis */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + '…';
}

/** Generate initials from a name */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0]?.toUpperCase() ?? '')
    .slice(0, 2)
    .join('');
}

/** Deep merge two objects */
export function deepMerge<T extends object>(target: T, source: Partial<T>): T {
  const result = { ...target };
  for (const key in source) {
    const sourceVal = source[key];
    const targetVal = result[key];
    if (
      sourceVal &&
      typeof sourceVal === 'object' &&
      !Array.isArray(sourceVal) &&
      targetVal &&
      typeof targetVal === 'object' &&
      !Array.isArray(targetVal)
    ) {
      result[key] = deepMerge(targetVal as object, sourceVal as object) as T[typeof key];
    } else if (sourceVal !== undefined) {
      result[key] = sourceVal as T[typeof key];
    }
  }
  return result;
}

/** Debounce a function */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** Check if running in browser */
export const isBrowser = typeof window !== 'undefined';

/** Generate a random ID */
export function generateId(prefix = 'id'): string {
  return `${prefix}-${Math.random().toString(36).slice(2, 9)}`;
}
