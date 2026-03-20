import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  [
    'inline-flex items-center gap-1 font-medium',
    'transition-colors duration-150',
  ],
  {
    variants: {
      variant: {
        // Solid
        default:     'bg-secondary-700 text-white',
        primary:     'bg-primary-600 text-white',
        accent:      'bg-accent-600 text-white',
        success:     'bg-success-600 text-white',
        warning:     'bg-warning-600 text-white',
        error:       'bg-error-600 text-white',
        // Subtle (light background)
        'subtle-default':  'bg-secondary-100 text-secondary-700',
        'subtle-primary':  'bg-primary-100 text-primary-700',
        'subtle-accent':   'bg-accent-100 text-accent-700',
        'subtle-success':  'bg-success-100 text-success-700',
        'subtle-warning':  'bg-warning-100 text-warning-700',
        'subtle-error':    'bg-error-100 text-error-700',
        // Outline
        outline:          'border border-secondary-300 text-secondary-600 bg-transparent',
        'outline-primary':'border border-primary-300 text-primary-600 bg-transparent',
      },
      size: {
        xs: 'px-1.5 py-0 text-[10px] leading-5',
        sm: 'px-2   py-0.5 text-xs',
        md: 'px-2.5 py-0.5 text-xs',
        lg: 'px-3   py-1   text-sm',
      },
      rounded: {
        sm:   'rounded',
        md:   'rounded-md',
        full: 'rounded-full',
      },
      dot: {
        true: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'sm',
      rounded: 'full',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
  dotColor?: string;
}

function Badge({
  className,
  variant,
  size,
  rounded,
  dot,
  dotColor,
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(badgeVariants({ variant, size, rounded, dot, className }))}
      {...props}
    >
      {dot && (
        <span
          className={cn(
            'inline-block h-1.5 w-1.5 rounded-full',
            dotColor ?? 'bg-current'
          )}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
}

export { Badge, badgeVariants };
