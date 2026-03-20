import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  // Base styles
  [
    'inline-flex items-center justify-center gap-2 whitespace-nowrap',
    'font-medium transition-all duration-200 ease-smooth',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
    'select-none',
    '[&_svg]:pointer-events-none [&_svg]:shrink-0',
  ],
  {
    variants: {
      variant: {
        // Solid primary
        default: [
          'bg-primary-600 text-white shadow-primary-sm',
          'hover:bg-primary-700 hover:shadow-primary active:bg-primary-800 active:shadow-none',
          'active:scale-[0.98]',
        ],
        // Secondary solid
        secondary: [
          'bg-secondary-700 text-white shadow-xs',
          'hover:bg-secondary-800 active:bg-secondary-900 active:scale-[0.98]',
        ],
        // Accent / purple
        accent: [
          'bg-accent-600 text-white shadow-accent-sm',
          'hover:bg-accent-700 hover:shadow-accent active:bg-accent-800 active:scale-[0.98]',
        ],
        // Ghost (text button)
        ghost: [
          'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900',
          'active:bg-secondary-200 active:scale-[0.98]',
        ],
        // Outline
        outline: [
          'border border-secondary-300 bg-transparent text-secondary-700',
          'hover:bg-secondary-50 hover:border-secondary-400 hover:text-secondary-900',
          'active:bg-secondary-100 active:scale-[0.98]',
        ],
        // Outline primary
        'outline-primary': [
          'border border-primary-300 bg-transparent text-primary-700',
          'hover:bg-primary-50 hover:border-primary-400 hover:text-primary-800',
          'active:bg-primary-100 active:scale-[0.98]',
        ],
        // Destructive
        destructive: [
          'bg-error-600 text-white shadow-xs',
          'hover:bg-error-700 active:bg-error-800 active:scale-[0.98]',
        ],
        // Link-style
        link: [
          'text-primary-600 underline-offset-4',
          'hover:underline hover:text-primary-700',
          'h-auto px-0 py-0',
        ],
      },
      size: {
        xs:      'h-7  rounded-md px-2.5  text-xs  [&_svg]:size-3',
        sm:      'h-8  rounded-md px-3    text-sm  [&_svg]:size-3.5',
        default: 'h-10 rounded-lg px-4    text-sm  [&_svg]:size-4',
        md:      'h-10 rounded-lg px-4    text-sm  [&_svg]:size-4',
        lg:      'h-11 rounded-lg px-5    text-base [&_svg]:size-4',
        xl:      'h-12 rounded-xl px-6    text-base [&_svg]:size-5',
        '2xl':   'h-14 rounded-xl px-8    text-lg  [&_svg]:size-5',
        icon:    'h-10 w-10  rounded-lg              [&_svg]:size-4',
        'icon-sm':'h-8  w-8  rounded-md              [&_svg]:size-3.5',
        'icon-lg':'h-12 w-12 rounded-xl              [&_svg]:size-5',
      },
      fullWidth: {
        true: 'w-full',
      },
      loading: {
        true: 'cursor-wait opacity-80',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      loading,
      asChild = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button';

    return (
      <Comp
        ref={ref}
        className={cn(
          buttonVariants({ variant, size, fullWidth, loading, className })
        )}
        disabled={disabled ?? loading ?? false}
        {...props}
      >
        {loading ? (
          <svg
            className="animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12" cy="12" r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        ) : leftIcon ? (
          leftIcon
        ) : null}
        {children}
        {!loading && rightIcon ? rightIcon : null}
      </Comp>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };
