import type { Config } from 'tailwindcss';
import { fontFamily } from 'tailwindcss/defaultTheme';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Primary — Indigo / Blue
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
          DEFAULT: '#4f46e5',
          foreground: '#ffffff',
        },
        // Secondary — Slate
        secondary: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
          DEFAULT: '#475569',
          foreground: '#ffffff',
        },
        // Accent — Violet / Purple
        accent: {
          50:  '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
          950: '#2e1065',
          DEFAULT: '#7c3aed',
          foreground: '#ffffff',
        },
        // Semantic colors
        success: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          DEFAULT: '#16a34a',
          foreground: '#ffffff',
        },
        warning: {
          50:  '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          DEFAULT: '#d97706',
          foreground: '#ffffff',
        },
        error: {
          50:  '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          DEFAULT: '#dc2626',
          foreground: '#ffffff',
        },
        // Surface / Background aliases
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
      },

      fontFamily: {
        sans: ['var(--font-inter)', ...fontFamily.sans],
        mono: ['var(--font-mono)', ...fontFamily.mono],
        heading: ['var(--font-inter)', ...fontFamily.sans],
      },

      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
        xs:   ['0.75rem',  { lineHeight: '1rem' }],
        sm:   ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem',     { lineHeight: '1.5rem' }],
        lg:   ['1.125rem', { lineHeight: '1.75rem' }],
        xl:   ['1.25rem',  { lineHeight: '1.75rem' }],
        '2xl':['1.5rem',   { lineHeight: '2rem' }],
        '3xl':['1.875rem', { lineHeight: '2.25rem' }],
        '4xl':['2.25rem',  { lineHeight: '2.5rem', letterSpacing: '-0.02em' }],
        '5xl':['3rem',     { lineHeight: '1.1',    letterSpacing: '-0.025em' }],
        '6xl':['3.75rem',  { lineHeight: '1',      letterSpacing: '-0.03em' }],
        '7xl':['4.5rem',   { lineHeight: '1',      letterSpacing: '-0.035em' }],
        '8xl':['6rem',     { lineHeight: '1',      letterSpacing: '-0.04em' }],
      },

      spacing: {
        '4.5': '1.125rem',
        '13':  '3.25rem',
        '15':  '3.75rem',
        '18':  '4.5rem',
        '22':  '5.5rem',
        '30':  '7.5rem',
        '34':  '8.5rem',
        '68':  '17rem',
        '72':  '18rem',
        '76':  '19rem',
        '80':  '20rem',
        '88':  '22rem',
        '96':  '24rem',
        '104': '26rem',
        '112': '28rem',
        '120': '30rem',
        '128': '32rem',
      },

      borderRadius: {
        '2xs': '0.125rem',
        xs:    '0.25rem',
        sm:    '0.375rem',
        DEFAULT:'0.5rem',
        md:    '0.625rem',
        lg:    '0.75rem',
        xl:    '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
        full:  '9999px',
      },

      boxShadow: {
        '2xs':   '0 1px 2px 0 rgb(0 0 0 / 0.03)',
        xs:      '0 1px 3px 0 rgb(0 0 0 / 0.05), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
        sm:      '0 2px 4px 0 rgb(0 0 0 / 0.06), 0 1px 3px -1px rgb(0 0 0 / 0.06)',
        DEFAULT: '0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.07)',
        md:      '0 6px 10px -2px rgb(0 0 0 / 0.08), 0 3px 6px -3px rgb(0 0 0 / 0.08)',
        lg:      '0 10px 20px -4px rgb(0 0 0 / 0.1),  0 4px 8px  -4px rgb(0 0 0 / 0.08)',
        xl:      '0 20px 40px -8px rgb(0 0 0 / 0.12), 0 8px 16px -8px rgb(0 0 0 / 0.08)',
        '2xl':   '0 30px 60px -12px rgb(0 0 0 / 0.14)',
        'inner-sm': 'inset 0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'inner':    'inset 0 2px 4px 0 rgb(0 0 0 / 0.06)',
        // Colored glow shadows
        'primary-sm': '0 4px 14px 0 rgb(79 70 229 / 0.25)',
        'primary':    '0 8px 24px 0 rgb(79 70 229 / 0.3)',
        'primary-lg': '0 16px 40px 0 rgb(79 70 229 / 0.35)',
        'accent-sm':  '0 4px 14px 0 rgb(124 58 237 / 0.25)',
        'accent':     '0 8px 24px 0 rgb(124 58 237 / 0.3)',
        none: 'none',
      },

      backgroundImage: {
        'gradient-radial':      'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':       'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-primary':     'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
        'gradient-hero':        'linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #3730a3 100%)',
        'gradient-subtle':      'linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f5f3ff 100%)',
        'gradient-card':        'linear-gradient(145deg, rgba(255,255,255,0.9) 0%, rgba(238,242,255,0.5) 100%)',
        'dot-pattern':          'radial-gradient(circle, #e2e8f0 1px, transparent 1px)',
        'grid-pattern':         'linear-gradient(#e2e8f0 1px, transparent 1px), linear-gradient(to right, #e2e8f0 1px, transparent 1px)',
      },

      keyframes: {
        // Entrance
        'fade-in': {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-down': {
          from: { opacity: '0', transform: 'translateY(-16px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          from: { opacity: '0', transform: 'translateX(24px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        'slide-in-left': {
          from: { opacity: '0', transform: 'translateX(-24px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        'zoom-in': {
          from: { opacity: '0', transform: 'scale(0.96)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        // Continuous
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.7' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-8px)' },
        },
        'shimmer': {
          from: { backgroundPosition: '-200% 0' },
          to:   { backgroundPosition: '200% 0' },
        },
        'spin-slow': {
          from: { transform: 'rotate(0deg)' },
          to:   { transform: 'rotate(360deg)' },
        },
        'bounce-subtle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':      { transform: 'translateY(-4px)' },
        },
        // Counter
        'count-up': {
          from: { transform: 'translateY(100%)', opacity: '0' },
          to:   { transform: 'translateY(0)',    opacity: '1' },
        },
      },

      animation: {
        'fade-in':       'fade-in 0.4s ease-out',
        'fade-up':       'fade-up 0.5s ease-out',
        'fade-down':     'fade-down 0.5s ease-out',
        'slide-in-right':'slide-in-right 0.4s ease-out',
        'slide-in-left': 'slide-in-left 0.4s ease-out',
        'zoom-in':       'zoom-in 0.3s ease-out',
        'pulse-subtle':  'pulse-subtle 2.5s ease-in-out infinite',
        'float':         'float 4s ease-in-out infinite',
        'shimmer':       'shimmer 2s linear infinite',
        'spin-slow':     'spin-slow 8s linear infinite',
        'bounce-subtle': 'bounce-subtle 2s ease-in-out infinite',
        'count-up':      'count-up 0.4s ease-out',
      },

      transitionTimingFunction: {
        'spring':       'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        'smooth':       'cubic-bezier(0.4, 0, 0.2, 1)',
        'sharp':        'cubic-bezier(0.4, 0, 0.6, 1)',
        'ease-in-expo': 'cubic-bezier(0.95, 0.05, 0.795, 0.035)',
        'ease-out-expo':'cubic-bezier(0.19, 1, 0.22, 1)',
      },

      transitionDuration: {
        '0':   '0ms',
        '75':  '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '250': '250ms',
        '300': '300ms',
        '400': '400ms',
        '500': '500ms',
        '700': '700ms',
        '1000':'1000ms',
      },

      zIndex: {
        '-1':  '-1',
        '0':   '0',
        '10':  '10',
        '20':  '20',
        '30':  '30',
        '40':  '40',
        '50':  '50',
        '60':  '60',
        '70':  '70',
        '80':  '80',
        '90':  '90',
        '100': '100',
        'overlay': '200',
        'modal':   '300',
        'toast':   '400',
        'tooltip': '500',
      },
    },
  },
  plugins: [],
};

export default config;
