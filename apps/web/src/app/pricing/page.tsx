import Link from 'next/link';
import { Check, Star, ArrowRight, Zap, ChevronRight, ShieldCheck, HelpCircle } from 'lucide-react';
import type { Metadata } from 'next';
import { Navbar } from '@/components/layout/navbar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';

export const metadata: Metadata = {
  title: 'Pricing',
  description:
    'Transparent pricing for Talentora AI. Start with a 14-day free trial. No credit card required.',
};

const tiers = [
  {
    id: 'starter',
    name: 'Starter',
    tagline: 'For independent analysts & freelancers',
    monthlyPrice: 49,
    annualPrice: 39,
    annualTotal: 468,
    savings: 120,
    seats: 1,
    color: 'border-secondary-200',
    ctaLabel: 'Start free trial',
    ctaHref: '/signup?plan=starter',
    sections: [
      {
        title: 'Data Access',
        features: [
          { label: '500 job searches / month', included: true },
          { label: '10 countries covered', included: true },
          { label: 'Basic salary benchmarks (median only)', included: true },
          { label: 'Full P10–P90 percentile data', included: false },
          { label: 'Unlimited searches', included: false },
          { label: 'All 50+ countries', included: false },
        ],
      },
      {
        title: 'Analytics & Reports',
        features: [
          { label: 'Skill demand dashboard', included: true },
          { label: '3 saved reports', included: true },
          { label: 'CSV export', included: true },
          { label: 'PDF & Excel export', included: false },
          { label: 'Unlimited saved reports', included: false },
          { label: 'Custom date ranges', included: false },
        ],
      },
      {
        title: 'Integration & Support',
        features: [
          { label: 'Email support (48h SLA)', included: true },
          { label: 'API access', included: false },
          { label: 'Webhooks', included: false },
          { label: 'Slack / Teams integration', included: false },
        ],
      },
    ],
  },
  {
    id: 'pro',
    name: 'Pro',
    tagline: 'For recruiters and HR professionals',
    monthlyPrice: 149,
    annualPrice: 119,
    annualTotal: 1428,
    savings: 360,
    seats: 3,
    highlighted: true,
    badge: 'Most popular',
    color: 'border-primary-400 ring-2 ring-primary-400',
    ctaLabel: 'Start free trial',
    ctaHref: '/signup?plan=pro',
    sections: [
      {
        title: 'Data Access',
        features: [
          { label: 'Unlimited job searches', included: true },
          { label: 'All 50+ countries', included: true },
          { label: 'Full P10–P90 percentile salary data', included: true },
          { label: 'Full skill intelligence', included: true },
          { label: 'Historical data (24 months)', included: true },
          { label: 'Custom data ingestion', included: false },
        ],
      },
      {
        title: 'Analytics & Reports',
        features: [
          { label: 'Unlimited saved reports', included: true },
          { label: 'PDF & Excel export', included: true },
          { label: 'AI-generated narrative reports', included: true },
          { label: 'Custom date ranges', included: true },
          { label: 'White-label reports', included: false },
          { label: 'Scheduled report delivery', included: false },
        ],
      },
      {
        title: 'Integration & Support',
        features: [
          { label: 'API access (10,000 calls/month)', included: true },
          { label: 'Priority email support (24h SLA)', included: true },
          { label: 'Webhooks', included: false },
          { label: 'Slack / Teams integration', included: false },
        ],
      },
    ],
  },
  {
    id: 'team',
    name: 'Team',
    tagline: 'For HR teams and consultancies',
    monthlyPrice: 399,
    annualPrice: 319,
    annualTotal: 3828,
    savings: 960,
    seats: 10,
    color: 'border-secondary-200',
    ctaLabel: 'Start free trial',
    ctaHref: '/signup?plan=team',
    sections: [
      {
        title: 'Data Access',
        features: [
          { label: 'Everything in Pro', included: true },
          { label: 'Historical data (48 months)', included: true },
          { label: 'Bulk data downloads', included: true },
          { label: 'Custom data ingestion', included: false },
          { label: 'Dedicated data pipeline', included: false },
        ],
      },
      {
        title: 'Analytics & Reports',
        features: [
          { label: 'White-label reports', included: true },
          { label: 'Scheduled report delivery', included: true },
          { label: 'Team workspaces & sharing', included: true },
          { label: 'Custom branding', included: true },
          { label: 'Bespoke AI models', included: false },
        ],
      },
      {
        title: 'Integration & Support',
        features: [
          { label: 'API access (100,000 calls/month)', included: true },
          { label: 'Webhooks & real-time alerts', included: true },
          { label: 'Slack & Teams integration', included: true },
          { label: 'SLA-backed support (4h response)', included: true },
          { label: 'Dedicated account manager', included: false },
        ],
      },
    ],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    tagline: 'For large organisations & platforms',
    monthlyPrice: null,
    annualPrice: null,
    annualTotal: null,
    savings: null,
    seats: 'unlimited' as const,
    color: 'border-secondary-200',
    ctaLabel: 'Contact sales',
    ctaHref: '/contact?subject=enterprise',
    sections: [
      {
        title: 'Data Access',
        features: [
          { label: 'Everything in Team', included: true },
          { label: 'Custom data ingestion', included: true },
          { label: 'Dedicated data pipeline', included: true },
          { label: 'On-premise deployment option', included: true },
          { label: 'Full historical archive', included: true },
        ],
      },
      {
        title: 'Analytics & Reports',
        features: [
          { label: 'Bespoke AI models', included: true },
          { label: 'Custom taxonomy mapping', included: true },
          { label: 'Quarterly business reviews', included: true },
          { label: 'Co-developed features', included: true },
        ],
      },
      {
        title: 'Security & Support',
        features: [
          { label: 'SSO & SCIM provisioning', included: true },
          { label: 'Custom SLA & uptime guarantee', included: true },
          { label: 'Dedicated account manager', included: true },
          { label: 'ISO 27001 audit reports', included: true },
          { label: 'DPA & custom contracts', included: true },
        ],
      },
    ],
  },
];

const comparisonRows = [
  { label: 'Job searches / month', values: ['500', 'Unlimited', 'Unlimited', 'Unlimited'] },
  { label: 'Countries covered', values: ['10', '50+', '50+', '50+'] },
  { label: 'Seats', values: ['1', '3', '10', 'Unlimited'] },
  { label: 'Salary percentiles', values: ['Median', 'P10–P90', 'P10–P90', 'P10–P90'] },
  { label: 'Historical data', values: ['—', '24 months', '48 months', 'Full archive'] },
  { label: 'Saved reports', values: ['3', 'Unlimited', 'Unlimited', 'Unlimited'] },
  { label: 'Export formats', values: ['CSV', 'PDF, Excel, CSV', 'PDF, Excel, CSV', 'All + custom'] },
  { label: 'API access', values: ['—', '10k calls/mo', '100k calls/mo', 'Custom'] },
  { label: 'White-label reports', values: ['—', '—', '✓', '✓'] },
  { label: 'SSO / SCIM', values: ['—', '—', '—', '✓'] },
  { label: 'Support', values: ['Email 48h', 'Priority 24h', 'SLA 4h', 'Dedicated AM'] },
];

export default function PricingPage() {
  return (
    <>
      <Navbar />
      <main className="pt-16">
        {/* ── Header ── */}
        <section className="bg-gradient-subtle section-sm border-b border-secondary-100">
          <div className="container-wide text-center">
            <Badge variant="subtle-primary" size="md" className="mb-4">
              <Zap className="h-3 w-3" />
              14-day free trial on all plans
            </Badge>
            <h1 className="text-balance text-4xl font-bold text-secondary-900 md:text-5xl">
              Transparent pricing,<br />
              <span className="text-gradient">no surprises</span>
            </h1>
            <p className="mx-auto mt-4 max-w-xl text-lg text-secondary-500">
              All prices in EUR, excluding VAT. Annual billing saves ~20%.
              No credit card required for the trial.
            </p>

            {/* Toggle placeholder – could be made interactive with client component */}
            <div className="mt-8 inline-flex items-center rounded-xl border border-secondary-200 bg-white p-1 shadow-xs gap-1">
              <span className="rounded-lg bg-secondary-900 px-4 py-1.5 text-sm font-medium text-white">
                Annual
              </span>
              <span className="px-4 py-1.5 text-sm font-medium text-secondary-500">
                Monthly
              </span>
            </div>
            <p className="mt-2 text-xs text-success-600 font-medium">
              ✓ Save up to 20% with annual billing
            </p>
          </div>
        </section>

        {/* ── Pricing cards ── */}
        <section className="section bg-white">
          <div className="container-wide">
            <div className="grid gap-6 lg:grid-cols-4">
              {tiers.map((tier, idx) => (
                <Card
                  key={tier.id}
                  className={`relative flex flex-col border-2 ${tier.color} ${tier.highlighted ? 'shadow-primary' : ''}`}
                >
                  {tier.badge && (
                    <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                      <Badge variant="primary" size="sm">
                        <Star className="h-3 w-3" />
                        {tier.badge}
                      </Badge>
                    </div>
                  )}

                  <div className="p-6 flex flex-col h-full">
                    {/* Header */}
                    <div>
                      <h2 className="text-lg font-bold text-secondary-900">{tier.name}</h2>
                      <p className="mt-1 text-xs text-secondary-500 leading-snug">{tier.tagline}</p>
                    </div>

                    {/* Pricing */}
                    <div className="mt-5">
                      {tier.annualPrice !== null ? (
                        <>
                          <div className="flex items-baseline gap-1">
                            <span className="text-4xl font-bold text-secondary-900">
                              €{tier.annualPrice}
                            </span>
                            <span className="text-sm text-secondary-400">/mo</span>
                          </div>
                          <p className="mt-1 text-xs text-secondary-400">
                            €{tier.annualTotal}/yr · Save €{tier.savings}
                          </p>
                        </>
                      ) : (
                        <>
                          <div className="text-3xl font-bold text-secondary-900">Custom</div>
                          <p className="mt-1 text-xs text-secondary-400">Tailored to your needs</p>
                        </>
                      )}
                    </div>

                    <div className="mt-1 text-xs text-secondary-500">
                      {typeof tier.seats === 'number'
                        ? `${tier.seats} seat${tier.seats > 1 ? 's' : ''} included`
                        : 'Unlimited seats'}
                    </div>

                    {/* Feature sections */}
                    <div className="mt-6 flex-1 space-y-5">
                      {tier.sections.map((section) => (
                        <div key={section.title}>
                          <p className="text-[11px] font-semibold uppercase tracking-wider text-secondary-400 mb-2">
                            {section.title}
                          </p>
                          <ul className="space-y-1.5">
                            {section.features.map((f) => (
                              <li key={f.label} className="flex items-start gap-2">
                                {f.included ? (
                                  <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success-500" />
                                ) : (
                                  <span className="mt-0.5 h-3.5 w-3.5 shrink-0 text-secondary-300 text-[10px] flex items-center justify-center">
                                    ✕
                                  </span>
                                )}
                                <span
                                  className={`text-xs leading-snug ${
                                    f.included ? 'text-secondary-700' : 'text-secondary-400'
                                  }`}
                                >
                                  {f.label}
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>

                    {/* CTA */}
                    <div className="mt-8">
                      <Button
                        variant={tier.highlighted ? 'default' : 'outline'}
                        fullWidth
                        asChild
                      >
                        <Link href={tier.ctaHref}>
                          {tier.ctaLabel}
                          <ChevronRight className="h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Trust row */}
            <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-sm text-secondary-500">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-success-500" />
                GDPR compliant
              </span>
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-success-500" />
                EU data residency
              </span>
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-success-500" />
                ISO 27001 certified
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="h-4 w-4 text-success-500" />
                14-day free trial
              </span>
              <span className="flex items-center gap-1.5">
                <Check className="h-4 w-4 text-success-500" />
                Cancel anytime
              </span>
            </div>
          </div>
        </section>

        {/* ── Feature comparison table ── */}
        <section className="section-sm bg-secondary-50 border-y border-secondary-100">
          <div className="container-wide">
            <h2 className="text-2xl font-bold text-secondary-900 mb-8 text-center">
              Full feature comparison
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-secondary-200">
                    <th className="pb-4 text-left font-medium text-secondary-500 w-48">Feature</th>
                    {tiers.map((t) => (
                      <th key={t.id} className={`pb-4 text-center font-semibold ${t.highlighted ? 'text-primary-700' : 'text-secondary-900'}`}>
                        {t.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-secondary-100">
                  {comparisonRows.map((row) => (
                    <tr key={row.label} className="hover:bg-white transition-colors">
                      <td className="py-3 text-secondary-600 text-xs font-medium">{row.label}</td>
                      {row.values.map((val, i) => (
                        <td key={i} className={`py-3 text-center text-xs ${tiers[i]?.highlighted ? 'text-primary-700 font-medium' : 'text-secondary-700'}`}>
                          {val === '✓' ? (
                            <Check className="h-4 w-4 text-success-500 mx-auto" />
                          ) : val === '—' ? (
                            <span className="text-secondary-300">—</span>
                          ) : (
                            val
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* ── FAQ ── */}
        <section className="section bg-white">
          <div className="container-tight">
            <div className="flex items-center gap-3 mb-8">
              <HelpCircle className="h-5 w-5 text-primary-500" />
              <h2 className="text-2xl font-bold text-secondary-900">Pricing FAQ</h2>
            </div>
            <div className="divide-y divide-secondary-100">
              {[
                { q: 'Can I switch plans later?', a: 'Yes, you can upgrade or downgrade at any time. Upgrades are effective immediately; downgrades take effect at the end of the billing cycle.' },
                { q: 'What happens after my trial ends?', a: 'After 14 days you will be prompted to choose a plan. If you do nothing, your account moves to a read-only state. Your data is preserved for 30 days.' },
                { q: 'Is VAT included in the prices?', a: 'No. All displayed prices exclude VAT. VAT will be applied at checkout based on your billing country and registered VAT number.' },
                { q: 'Do you offer nonprofit or academic discounts?', a: 'Yes — we offer 50% discounts for registered nonprofits and academic institutions. Contact us with proof of status.' },
                { q: 'Can I pay by invoice?', a: 'Annual plans of €1,000+ can be paid by bank transfer with net-30 terms. Contact our sales team to arrange this.' },
              ].map((faq) => (
                <div key={faq.q} className="py-5">
                  <h3 className="text-sm font-semibold text-secondary-900">{faq.q}</h3>
                  <p className="mt-1.5 text-sm text-secondary-600 leading-relaxed">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA ── */}
        <section className="section-sm bg-gradient-hero text-white">
          <div className="container-tight text-center">
            <h2 className="text-2xl font-bold md:text-3xl">Still have questions?</h2>
            <p className="mt-3 text-secondary-300">
              Talk to our team. We typically respond within 2 hours on business days.
            </p>
            <div className="mt-6 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
              <Button size="lg" asChild>
                <Link href="/signup">
                  Start free trial
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-white/20 bg-white/10 text-white hover:bg-white/20"
                asChild
              >
                <Link href="/contact">Talk to sales</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
