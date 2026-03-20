import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// ── Card container ────────────────────────────────────────────────────────────

const cardVariants = cva(
  'rounded-xl border bg-card text-card-foreground transition-all duration-200',
  {
    variants: {
      variant: {
        default:  'border-border shadow-xs',
        elevated: 'border-border shadow-md',
        outlined: 'border-border/80 shadow-none',
        ghost:    'border-transparent shadow-none bg-transparent',
        glass:    'border-white/20 bg-white/80 backdrop-blur-md shadow-md',
        gradient: 'border-primary-100 bg-gradient-card shadow-sm',
        premium:  'border-primary-200/50 bg-gradient-to-br from-white to-primary-50/30 shadow-md',
      },
      hover: {
        true:  'hover:shadow-lg hover:-translate-y-0.5 cursor-pointer',
        false: '',
      },
      padding: {
        none: 'p-0',
        sm:   'p-4',
        md:   'p-5',
        lg:   'p-6',
        xl:   'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      hover: false,
      padding: 'none',
    },
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, hover, padding, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, hover, padding, className }))}
      {...props}
    />
  )
);
Card.displayName = 'Card';

// ── Card Header ───────────────────────────────────────────────────────────────

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col gap-1.5 p-6', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

// ── Card Title ────────────────────────────────────────────────────────────────

const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-lg font-semibold leading-tight tracking-tight text-foreground',
      className
    )}
    {...props}
  >
    {children}
  </h3>
));
CardTitle.displayName = 'CardTitle';

// ── Card Description ──────────────────────────────────────────────────────────

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-muted-foreground leading-relaxed', className)}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

// ── Card Content ──────────────────────────────────────────────────────────────

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('px-6 pb-6', className)}
    {...props}
  />
));
CardContent.displayName = 'CardContent';

// ── Card Footer ───────────────────────────────────────────────────────────────

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center justify-between px-6 pb-6 pt-0',
      className
    )}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

// ── Card Divider ──────────────────────────────────────────────────────────────

const CardDivider = React.forwardRef<
  HTMLHRElement,
  React.HTMLAttributes<HTMLHRElement>
>(({ className, ...props }, ref) => (
  <hr
    ref={ref}
    className={cn('border-border mx-6', className)}
    {...props}
  />
));
CardDivider.displayName = 'CardDivider';

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  CardDivider,
  cardVariants,
};
