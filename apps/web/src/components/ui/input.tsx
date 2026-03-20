import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// ── Input wrapper ─────────────────────────────────────────────────────────────

const inputVariants = cva(
  [
    'flex w-full rounded-lg border bg-white px-3 py-2',
    'text-sm text-foreground placeholder:text-muted-foreground',
    'transition-all duration-200 ease-smooth',
    'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-0 focus:border-primary-400',
    'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-secondary-50',
    'file:border-0 file:bg-transparent file:text-sm file:font-medium',
  ],
  {
    variants: {
      variant: {
        default: 'border-secondary-300 hover:border-secondary-400',
        ghost:   'border-transparent bg-secondary-100 hover:bg-secondary-200 focus:bg-white',
        filled:  'border-transparent bg-secondary-100 hover:bg-secondary-50 focus:bg-white focus:border-secondary-300',
        error:   'border-error-400 focus:ring-error-300 hover:border-error-500',
        success: 'border-success-400 focus:ring-success-300',
      },
      inputSize: {
        sm:      'h-8  text-xs px-2.5',
        default: 'h-10 text-sm px-3',
        lg:      'h-11 text-base px-4',
        xl:      'h-12 text-base px-4',
      },
    },
    defaultVariants: {
      variant: 'default',
      inputSize: 'default',
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  leftAddon?: React.ReactNode;
  rightAddon?: React.ReactNode;
  error?: string;
  hint?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      variant,
      inputSize,
      type = 'text',
      leftIcon,
      rightIcon,
      leftAddon,
      rightAddon,
      error,
      hint,
      id,
      ...props
    },
    ref
  ) => {
    const hasError = Boolean(error);
    const resolvedVariant = hasError ? 'error' : variant;

    const inputEl = (
      <input
        id={id}
        type={type}
        ref={ref}
        className={cn(
          inputVariants({ variant: resolvedVariant, inputSize }),
          leftIcon  && 'pl-9',
          rightIcon && 'pr-9',
          leftAddon && 'rounded-l-none',
          rightAddon && 'rounded-r-none',
          className
        )}
        aria-invalid={hasError}
        aria-describedby={
          hasError ? `${id}-error` : hint ? `${id}-hint` : undefined
        }
        {...props}
      />
    );

    return (
      <div className="w-full">
        {/* Addon / Icon wrapper */}
        {leftIcon || rightIcon || leftAddon || rightAddon ? (
          <div className="flex">
            {leftAddon && (
              <span className="inline-flex items-center rounded-l-lg border border-r-0 border-secondary-300 bg-secondary-50 px-3 text-sm text-secondary-500">
                {leftAddon}
              </span>
            )}
            <div className="relative flex-1">
              {leftIcon && (
                <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-secondary-400">
                  {leftIcon}
                </span>
              )}
              {inputEl}
              {rightIcon && (
                <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-secondary-400">
                  {rightIcon}
                </span>
              )}
            </div>
            {rightAddon && (
              <span className="inline-flex items-center rounded-r-lg border border-l-0 border-secondary-300 bg-secondary-50 px-3 text-sm text-secondary-500">
                {rightAddon}
              </span>
            )}
          </div>
        ) : (
          <div className="relative">
            {inputEl}
          </div>
        )}

        {/* Hint / Error messages */}
        {hasError && (
          <p id={`${id}-error`} className="mt-1.5 text-xs text-error-600" role="alert">
            {error}
          </p>
        )}
        {!hasError && hint && (
          <p id={`${id}-hint`} className="mt-1.5 text-xs text-muted-foreground">
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input, inputVariants };
