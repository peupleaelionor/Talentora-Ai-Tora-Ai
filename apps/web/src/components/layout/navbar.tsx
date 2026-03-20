'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, ChevronDown, BarChart3, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface NavLink {
  label: string;
  href: string;
  badge?: string;
  children?: { label: string; href: string; description?: string }[];
}

const navLinks: NavLink[] = [
  {
    label: 'Product',
    href: '#product',
    children: [
      { label: 'Job Intelligence', href: '/product/jobs', description: 'Track 5M+ live job offers across Europe' },
      { label: 'Skill Demand', href: '/product/skills', description: 'Monitor rising and declining skills in real-time' },
      { label: 'Salary Benchmarks', href: '/product/salary', description: 'Accurate salary data across 50+ countries' },
      { label: 'Trend Reports', href: '/product/reports', description: 'AI-generated market intelligence reports' },
    ],
  },
  { label: 'Pricing', href: '/pricing' },
  { label: 'Enterprise', href: '/enterprise' },
  { label: 'Blog', href: '/blog' },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);
  const [activeDropdown, setActiveDropdown] = React.useState<string | null>(null);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  React.useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setActiveDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Close mobile menu on navigation
  React.useEffect(() => { setMobileOpen(false); }, [pathname]);

  return (
    <header
      className={cn(
        'fixed inset-x-0 top-0 z-50 transition-all duration-300',
        scrolled
          ? 'bg-white/95 backdrop-blur-lg border-b border-secondary-200/80 shadow-xs'
          : 'bg-transparent'
      )}
    >
      <div className="container-wide">
        <nav className="flex h-16 items-center justify-between gap-8">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2.5 font-heading font-bold text-xl tracking-tight"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary shadow-primary-sm">
              <BarChart3 className="h-4.5 w-4.5 text-white" />
            </div>
            <span className="text-secondary-900">Talentora</span>
            <span className="text-gradient font-semibold">AI</span>
          </Link>

          {/* Desktop navigation */}
          <div ref={dropdownRef} className="hidden md:flex items-center gap-1">
            {navLinks.map((link) =>
              link.children ? (
                <div key={link.label} className="relative">
                  <button
                    onClick={() =>
                      setActiveDropdown(
                        activeDropdown === link.label ? null : link.label
                      )
                    }
                    className={cn(
                      'flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium',
                      'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50',
                      'transition-colors duration-150',
                      activeDropdown === link.label && 'text-secondary-900 bg-secondary-50'
                    )}
                    aria-expanded={activeDropdown === link.label}
                    aria-haspopup="true"
                  >
                    {link.label}
                    <ChevronDown
                      className={cn(
                        'h-3.5 w-3.5 transition-transform duration-200',
                        activeDropdown === link.label && 'rotate-180'
                      )}
                    />
                  </button>
                  {activeDropdown === link.label && (
                    <div className="absolute left-0 top-full mt-2 w-72 rounded-xl border border-secondary-200 bg-white p-2 shadow-xl animate-fade-down">
                      {link.children.map((child) => (
                        <Link
                          key={child.href}
                          href={child.href}
                          className="flex flex-col rounded-lg px-3 py-2.5 hover:bg-secondary-50 transition-colors"
                          onClick={() => setActiveDropdown(null)}
                        >
                          <span className="text-sm font-medium text-secondary-900">
                            {child.label}
                          </span>
                          {child.description && (
                            <span className="mt-0.5 text-xs text-secondary-500 leading-snug">
                              {child.description}
                            </span>
                          )}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium',
                    'transition-colors duration-150',
                    pathname === link.href
                      ? 'text-primary-700 bg-primary-50'
                      : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50'
                  )}
                >
                  {link.label}
                  {link.badge && (
                    <Badge variant="subtle-primary" size="xs">
                      {link.badge}
                    </Badge>
                  )}
                </Link>
              )
            )}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/login">Sign in</Link>
            </Button>
            <Button size="sm" className="shadow-primary-sm" asChild>
              <Link href="/signup">
                <Sparkles className="h-3.5 w-3.5" />
                Start free trial
              </Link>
            </Button>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden rounded-lg p-2 text-secondary-600 hover:bg-secondary-100 transition-colors"
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </nav>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-secondary-200 bg-white/98 backdrop-blur-lg animate-fade-down">
          <div className="container-wide py-4 flex flex-col gap-1">
            {navLinks.map((link) => (
              <React.Fragment key={link.label}>
                {link.children ? (
                  <>
                    <p className="px-3 pt-3 pb-1 text-xs font-semibold uppercase tracking-wider text-secondary-400">
                      {link.label}
                    </p>
                    {link.children.map((child) => (
                      <Link
                        key={child.href}
                        href={child.href}
                        className="rounded-lg px-3 py-2.5 text-sm font-medium text-secondary-700 hover:bg-secondary-50 hover:text-secondary-900 transition-colors"
                      >
                        {child.label}
                      </Link>
                    ))}
                  </>
                ) : (
                  <Link
                    href={link.href}
                    className={cn(
                      'rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                      pathname === link.href
                        ? 'text-primary-700 bg-primary-50'
                        : 'text-secondary-700 hover:bg-secondary-50 hover:text-secondary-900'
                    )}
                  >
                    {link.label}
                  </Link>
                )}
              </React.Fragment>
            ))}

            <div className="flex flex-col gap-2 pt-4 border-t border-secondary-100 mt-2">
              <Button variant="outline" fullWidth asChild>
                <Link href="/login">Sign in</Link>
              </Button>
              <Button fullWidth asChild>
                <Link href="/signup">Start free trial</Link>
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
