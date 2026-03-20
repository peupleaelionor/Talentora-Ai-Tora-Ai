import Link from 'next/link';
import {
  BarChart3,
  TrendingUp,
  Globe2,
  Zap,
  Brain,
  DollarSign,
  FileBarChart,
  ShieldCheck,
  Check,
  ChevronRight,
  ArrowRight,
  Play,
  Star,
  Building2,
  Users,
  Database,
  Cpu,
} from 'lucide-react';
import { Navbar } from '@/components/layout/navbar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';

// ── Static data ───────────────────────────────────────────────────────────────

const stats = [
  { value: '5M+',  label: 'Job offers tracked',    icon: Database },
  { value: '100k+',label: 'Companies monitored',   icon: Building2 },
  { value: '50+',  label: 'Countries covered',     icon: Globe2 },
  { value: 'Live', label: 'Real-time data',        icon: Zap },
];

const features = [
  {
    icon: BarChart3,
    color: 'text-primary-600',
    bg: 'bg-primary-50',
    title: 'Job Market Intelligence',
    description:
      'Track 5M+ live job postings across Europe. Filter by role, sector, location and contract type. Identify emerging demand before your competitors.',
    highlights: ['Daily data ingestion', 'Deduplication engine', 'Job taxonomy mapping'],
  },
  {
    icon: Brain,
    color: 'text-accent-600',
    bg: 'bg-accent-50',
    title: 'Skill Demand Tracking',
    description:
      'Monitor which skills are rising or declining in real time. Get AI-ranked skill adjacency maps to identify upskilling opportunities.',
    highlights: ['Skill taxonomy with 10k+ nodes', 'Growth velocity scores', 'Adjacent skill clusters'],
  },
  {
    icon: DollarSign,
    color: 'text-success-600',
    bg: 'bg-success-50',
    title: 'Salary Benchmarks',
    description:
      'Accurate, percentile-based salary data sourced from 5M+ postings. Compare compensation across countries, industries and experience levels.',
    highlights: ['P10–P90 percentiles', 'Currency normalised', 'Updated weekly'],
  },
  {
    icon: TrendingUp,
    color: 'text-warning-600',
    bg: 'bg-warning-50',
    title: 'Trend Analysis',
    description:
      'AI-generated reports surface macro and micro shifts in the labour market. Get board-ready insights with a single click.',
    highlights: ['LLM-powered narratives', 'Custom date ranges', 'Export to PDF / Excel'],
  },
  {
    icon: Globe2,
    color: 'text-primary-600',
    bg: 'bg-primary-50',
    title: 'European Coverage',
    description:
      'From Lisbon to Warsaw, we aggregate job data from local boards, LinkedIn, Indeed and 200+ country-specific sources.',
    highlights: ['30+ languages parsed', 'GDPR compliant', '200+ data sources'],
  },
  {
    icon: Cpu,
    color: 'text-accent-600',
    bg: 'bg-accent-50',
    title: 'API & Integrations',
    description:
      'Embed our intelligence directly in your ATS, HRIS or BI stack. REST API with webhooks, Zapier connector and native Slack/Teams alerts.',
    highlights: ['REST API + webhooks', 'Zapier / Make integration', 'Bi-directional ATS sync'],
  },
];

const pricingTiers = [
  {
    id: 'starter',
    name: 'Starter',
    tagline: 'For independent analysts & freelancers',
    monthlyPrice: 49,
    annualPrice: 39,
    seats: 1,
    features: [
      'Up to 500 job searches / month',
      '10 countries covered',
      'Basic salary benchmarks',
      'Skill demand dashboard',
      '3 saved reports',
      'CSV export',
      'Email support',
    ],
    notIncluded: [
      'API access',
      'Custom reports',
      'Team collaboration',
    ],
  },
  {
    id: 'pro',
    name: 'Pro',
    tagline: 'For recruiters and HR professionals',
    monthlyPrice: 149,
    annualPrice: 119,
    seats: 3,
    highlighted: true,
    badge: 'Most popular',
    features: [
      'Unlimited job searches',
      'All 50+ countries',
      'Advanced salary percentiles (P10–P90)',
      'Full skill intelligence',
      'Unlimited saved reports',
      'PDF + Excel export',
      'API access (10k calls/month)',
      'Priority email support',
    ],
    notIncluded: [
      'White-label reports',
      'Dedicated account manager',
    ],
  },
  {
    id: 'team',
    name: 'Team',
    tagline: 'For HR teams and consultancies',
    monthlyPrice: 399,
    annualPrice: 319,
    seats: 10,
    features: [
      'Everything in Pro',
      'Up to 10 seats',
      'Team workspaces & sharing',
      'White-label reports',
      'API access (100k calls/month)',
      'Webhooks & real-time alerts',
      'Custom date ranges',
      'Slack & Teams integration',
      'SLA-backed support',
    ],
    notIncluded: [
      'Dedicated account manager',
      'Custom data ingestion',
    ],
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    tagline: 'For large organisations & platforms',
    monthlyPrice: null,
    annualPrice: null,
    seats: 'unlimited' as const,
    features: [
      'Everything in Team',
      'Unlimited seats',
      'Dedicated account manager',
      'Custom data ingestion',
      'On-premise deployment option',
      'SSO & SCIM provisioning',
      'Custom SLA & uptime guarantee',
      'Bespoke AI models',
      'Quarterly business reviews',
    ],
    notIncluded: [],
  },
];

const testimonials = [
  {
    quote: 'Talentora AI replaced three different data subscriptions. The salary benchmarks alone saved us weeks of manual research every quarter.',
    name: 'Laura M.',
    role: 'Head of Talent, Series-B startup',
    initials: 'LM',
  },
  {
    quote: 'The skill demand tracking is genuinely impressive. We spotted the Python→Rust shift in our engineering hires six months before competitors.',
    name: 'Thomas K.',
    role: 'VP Recruiting, European Tech Scale-up',
    initials: 'TK',
  },
  {
    quote: 'We embed the API into our ATS. Candidates now see real salary ranges instantly. NPS improved by 22 points.',
    name: 'Sofia B.',
    role: 'Product Director, HR-Tech SaaS',
    initials: 'SB',
  },
];

const faqs = [
  {
    q: 'Where does your data come from?',
    a: 'We aggregate from 200+ sources including LinkedIn, Indeed, StepStone, Glassdoor, and 150+ local European job boards. Our ingestion pipeline runs continuously, with most datasets refreshed daily.',
  },
  {
    q: 'Is the data GDPR compliant?',
    a: 'Yes. We only process publicly listed job postings and aggregate salary information. No personal candidate data is stored. We are registered with the relevant DPAs and maintain a full record of processing activities.',
  },
  {
    q: 'Can I export data to Excel or CSV?',
    a: 'All paid plans include CSV export. Pro and above includes Excel and PDF. Enterprise plans support bulk exports and scheduled delivery to S3 or SFTP.',
  },
  {
    q: 'Do you offer a free trial?',
    a: 'Yes — all plans come with a 14-day free trial, no credit card required. You can explore the full feature set before committing.',
  },
  {
    q: 'How does annual billing work?',
    a: 'Annual plans are billed upfront once per year and save approximately 20% vs monthly. You can switch from monthly to annual at any time and will receive a prorated credit.',
  },
  {
    q: 'What API rate limits apply?',
    a: 'Starter plans do not include API access. Pro includes 10,000 calls/month, Team 100,000 calls/month. Enterprise is negotiated based on volume. All plans benefit from the same low-latency infrastructure.',
  },
];

// ── Page ──────────────────────────────────────────────────────────────────────

export default function HomePage() {
  return (
    <>
      <Navbar />

      <main>
        {/* ── Hero ────────────────────────────────────────────────────────── */}
        <section className="relative overflow-hidden bg-gradient-hero pt-24 pb-20 md:pt-32 md:pb-32">
          {/* Background decoration */}
          <div className="absolute inset-0 bg-grid opacity-10" />
          <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-accent-600/20 blur-3xl" />
          <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-primary-500/20 blur-3xl" />

          <div className="container-wide relative">
            <div className="mx-auto max-w-4xl text-center">
              <Badge variant="subtle-primary" size="md" className="mb-6 bg-primary-500/20 text-primary-200 border border-primary-400/30">
                <Zap className="h-3 w-3" />
                Real-time European job market data
              </Badge>

              <h1 className="text-balance text-5xl font-bold tracking-tight text-white md:text-6xl lg:text-7xl">
                The Bloomberg
                <br />
                <span className="bg-gradient-to-r from-primary-300 via-accent-300 to-primary-200 bg-clip-text text-transparent">
                  for the Job Market
                </span>
              </h1>

              <p className="mx-auto mt-6 max-w-2xl text-lg text-secondary-300 leading-relaxed">
                Track 5M+ job offers in real time. Benchmark salaries across 50+ countries.
                Identify rising skills before your competitors. Built for European HR teams,
                recruiters and workforce analysts.
              </p>

              <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
                <Button size="xl" className="shadow-primary-lg" asChild>
                  <Link href="/signup">
                    Start free 14-day trial
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button
                  size="xl"
                  variant="outline"
                  className="border-white/20 bg-white/10 text-white hover:bg-white/20 hover:border-white/30"
                  asChild
                >
                  <Link href="/demo">
                    <Play className="h-4 w-4" />
                    Watch demo
                  </Link>
                </Button>
              </div>

              <p className="mt-4 text-sm text-secondary-400">
                No credit card required · Cancel anytime · GDPR compliant
              </p>
            </div>

            {/* Hero dashboard mockup */}
            <div className="mx-auto mt-16 max-w-5xl">
              <div className="rounded-2xl border border-white/10 bg-secondary-900/60 backdrop-blur-sm shadow-2xl overflow-hidden">
                {/* Browser chrome */}
                <div className="flex items-center gap-2 border-b border-white/10 bg-secondary-800/50 px-4 py-3">
                  <span className="h-3 w-3 rounded-full bg-error-400" />
                  <span className="h-3 w-3 rounded-full bg-warning-400" />
                  <span className="h-3 w-3 rounded-full bg-success-400" />
                  <span className="ml-4 flex-1 rounded-md bg-secondary-700 px-3 py-1 text-xs text-secondary-400">
                    app.talentora.ai/dashboard
                  </span>
                </div>
                {/* Mock dashboard content */}
                <div className="grid grid-cols-2 gap-4 p-6 md:grid-cols-4">
                  {[
                    { label: 'Active Job Offers', value: '4.8M', change: '+12%' },
                    { label: 'New Today', value: '28,400', change: '+8%' },
                    { label: 'Median Salary (EU)', value: '€52k', change: '+3%' },
                    { label: 'Top Skill', value: 'Python', change: '↑ Rank 1' },
                  ].map((m) => (
                    <div key={m.label} className="rounded-xl bg-secondary-800/50 p-4">
                      <p className="text-xs text-secondary-400">{m.label}</p>
                      <p className="mt-1 text-xl font-bold text-white">{m.value}</p>
                      <p className="mt-0.5 text-xs text-success-400">{m.change}</p>
                    </div>
                  ))}
                </div>
                <div className="px-6 pb-6">
                  <div className="h-32 rounded-xl bg-secondary-800/50 flex items-end gap-1 px-4 pb-4">
                    {[40, 55, 45, 70, 60, 80, 65, 90, 75, 85, 72, 95].map((h, i) => (
                      <div
                        key={i}
                        className="flex-1 rounded-sm bg-gradient-to-t from-primary-600 to-primary-400 transition-all"
                        style={{ height: `${h}%` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Stats ────────────────────────────────────────────────────────── */}
        <section className="border-b border-secondary-100 bg-white py-12">
          <div className="container-wide">
            <dl className="grid grid-cols-2 gap-8 md:grid-cols-4">
              {stats.map(({ value, label, icon: Icon }) => (
                <div key={label} className="flex flex-col items-center text-center">
                  <Icon className="mb-3 h-6 w-6 text-primary-500" />
                  <dt className="stat-number text-3xl font-bold text-secondary-900">
                    {value}
                  </dt>
                  <dd className="mt-1 text-sm text-secondary-500">{label}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* ── Features ─────────────────────────────────────────────────────── */}
        <section id="product" className="section bg-secondary-50">
          <div className="container-wide">
            <div className="mx-auto max-w-2xl text-center">
              <Badge variant="subtle-primary" size="md" className="mb-4">Platform capabilities</Badge>
              <h2 className="text-balance text-3xl font-bold text-secondary-900 md:text-4xl">
                Everything you need to{' '}
                <span className="text-gradient">lead with data</span>
              </h2>
              <p className="mt-4 text-lg text-secondary-500 leading-relaxed">
                A unified intelligence platform covering every dimension of the European labour market.
              </p>
            </div>

            <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((f) => {
                const Icon = f.icon;
                return (
                  <Card
                    key={f.title}
                    variant="default"
                    hover
                    padding="lg"
                    className="group"
                  >
                    <div
                      className={`mb-5 flex h-11 w-11 items-center justify-center rounded-xl ${f.bg} transition-transform duration-300 group-hover:scale-110`}
                    >
                      <Icon className={`h-5 w-5 ${f.color}`} />
                    </div>
                    <h3 className="text-lg font-semibold text-secondary-900">
                      {f.title}
                    </h3>
                    <p className="mt-2 text-sm text-secondary-500 leading-relaxed">
                      {f.description}
                    </p>
                    <ul className="mt-4 space-y-1.5">
                      {f.highlights.map((h) => (
                        <li key={h} className="flex items-center gap-2 text-xs text-secondary-600">
                          <Check className="h-3.5 w-3.5 text-success-500 shrink-0" />
                          {h}
                        </li>
                      ))}
                    </ul>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* ── Pricing ──────────────────────────────────────────────────────── */}
        <section id="pricing" className="section bg-white">
          <div className="container-wide">
            <div className="mx-auto max-w-2xl text-center">
              <Badge variant="subtle-primary" size="md" className="mb-4">Pricing</Badge>
              <h2 className="text-balance text-3xl font-bold text-secondary-900 md:text-4xl">
                Transparent pricing, no surprises
              </h2>
              <p className="mt-4 text-lg text-secondary-500">
                Start with a 14-day free trial. All prices exclude VAT.
              </p>
            </div>

            <div className="mt-14 grid gap-6 lg:grid-cols-4">
              {pricingTiers.map((tier) => (
                <Card
                  key={tier.id}
                  variant={tier.highlighted ? 'premium' : 'default'}
                  className={`relative flex flex-col ${tier.highlighted ? 'ring-2 ring-primary-500 shadow-primary' : ''}`}
                >
                  {tier.badge && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge variant="primary" size="sm">
                        <Star className="h-3 w-3" />
                        {tier.badge}
                      </Badge>
                    </div>
                  )}

                  <div className="p-6 flex-1 flex flex-col">
                    <div>
                      <h3 className="text-lg font-bold text-secondary-900">{tier.name}</h3>
                      <p className="mt-1 text-xs text-secondary-500">{tier.tagline}</p>
                    </div>

                    <div className="mt-5">
                      {tier.monthlyPrice !== null ? (
                        <div className="flex items-baseline gap-1">
                          <span className="text-4xl font-bold text-secondary-900">
                            €{tier.annualPrice ?? tier.monthlyPrice}
                          </span>
                          <span className="text-sm text-secondary-400">/mo</span>
                        </div>
                      ) : (
                        <div className="text-2xl font-bold text-secondary-900">Custom</div>
                      )}
                      {tier.monthlyPrice !== null && tier.annualPrice && (
                        <p className="mt-1 text-xs text-secondary-400">
                          Billed annually · €{tier.monthlyPrice}/mo monthly
                        </p>
                      )}
                    </div>

                    <div className="mt-2 text-xs text-secondary-500">
                      {typeof tier.seats === 'number' ? `${tier.seats} seat${tier.seats > 1 ? 's' : ''}` : 'Unlimited seats'}
                    </div>

                    <ul className="mt-6 space-y-2.5 flex-1">
                      {tier.features.map((f) => (
                        <li key={f} className="flex items-start gap-2 text-sm text-secondary-700">
                          <Check className="mt-0.5 h-4 w-4 shrink-0 text-success-500" />
                          {f}
                        </li>
                      ))}
                      {tier.notIncluded.map((f) => (
                        <li key={f} className="flex items-start gap-2 text-sm text-secondary-400 line-through">
                          <span className="mt-0.5 h-4 w-4 shrink-0 text-secondary-300 inline-flex items-center justify-center text-xs">✕</span>
                          {f}
                        </li>
                      ))}
                    </ul>

                    <div className="mt-8">
                      <Button
                        variant={tier.highlighted ? 'default' : 'outline'}
                        fullWidth
                        asChild
                      >
                        <Link href={tier.monthlyPrice === null ? '/contact' : '/signup'}>
                          {tier.monthlyPrice === null ? 'Contact sales' : 'Start free trial'}
                          <ChevronRight className="h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            <p className="mt-8 text-center text-sm text-secondary-400">
              All plans include a 14-day free trial · No credit card required · Cancel anytime
            </p>
          </div>
        </section>

        {/* ── Testimonials ─────────────────────────────────────────────────── */}
        <section className="section bg-secondary-50">
          <div className="container-wide">
            <div className="mx-auto max-w-2xl text-center mb-14">
              <Badge variant="subtle-primary" size="md" className="mb-4">Testimonials</Badge>
              <h2 className="text-balance text-3xl font-bold text-secondary-900 md:text-4xl">
                Trusted by European HR leaders
              </h2>
            </div>
            <div className="grid gap-6 md:grid-cols-3">
              {testimonials.map((t) => (
                <Card key={t.name} variant="default" padding="lg">
                  <div className="flex gap-0.5 mb-4">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-warning-400 text-warning-400" />
                    ))}
                  </div>
                  <p className="text-sm text-secondary-700 leading-relaxed italic">
                    "{t.quote}"
                  </p>
                  <div className="mt-5 flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-primary text-white text-sm font-bold">
                      {t.initials}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-secondary-900">{t.name}</p>
                      <p className="text-xs text-secondary-400">{t.role}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* ── FAQ ──────────────────────────────────────────────────────────── */}
        <section className="section bg-white">
          <div className="container-tight">
            <div className="mx-auto max-w-2xl text-center mb-12">
              <Badge variant="subtle-primary" size="md" className="mb-4">FAQ</Badge>
              <h2 className="text-balance text-3xl font-bold text-secondary-900 md:text-4xl">
                Frequently asked questions
              </h2>
            </div>
            <div className="divide-y divide-secondary-100">
              {faqs.map((faq) => (
                <div key={faq.q} className="py-6">
                  <h3 className="text-base font-semibold text-secondary-900">{faq.q}</h3>
                  <p className="mt-2 text-sm text-secondary-600 leading-relaxed">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA Banner ───────────────────────────────────────────────────── */}
        <section className="section bg-gradient-hero text-white">
          <div className="container-tight text-center">
            <h2 className="text-balance text-3xl font-bold md:text-4xl">
              Ready to lead with labour market data?
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-secondary-300 leading-relaxed">
              Join 2,000+ European HR teams, recruiters and workforce analysts using Talentora AI every day.
            </p>
            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Button size="xl" className="shadow-primary-lg" asChild>
                <Link href="/signup">
                  Start free 14-day trial
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button
                size="xl"
                variant="outline"
                className="border-white/20 bg-white/10 text-white hover:bg-white/20"
                asChild
              >
                <Link href="/pricing">View pricing</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>

      {/* ── Footer ─────────────────────────────────────────────────────────── */}
      <footer className="border-t border-secondary-200 bg-white">
        <div className="container-wide py-12">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-5">
            {/* Brand */}
            <div className="lg:col-span-2">
              <Link href="/" className="flex items-center gap-2.5 font-heading font-bold text-xl">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary">
                  <BarChart3 className="h-4 w-4 text-white" />
                </div>
                <span className="text-secondary-900">Talentora</span>
                <span className="text-gradient">AI</span>
              </Link>
              <p className="mt-3 max-w-xs text-sm text-secondary-500 leading-relaxed">
                The Bloomberg for the European job market. Real-time intelligence for HR leaders.
              </p>
              <div className="mt-4 flex gap-1 text-xs text-secondary-400">
                <ShieldCheck className="h-4 w-4 text-success-500 shrink-0" />
                <span>GDPR compliant · EU data residency · ISO 27001</span>
              </div>
            </div>

            {/* Links */}
            {[
              {
                title: 'Product',
                links: [
                  { label: 'Job Intelligence', href: '/product/jobs' },
                  { label: 'Skill Demand', href: '/product/skills' },
                  { label: 'Salary Benchmarks', href: '/product/salary' },
                  { label: 'API & Integrations', href: '/product/api' },
                  { label: 'Changelog', href: '/changelog' },
                ],
              },
              {
                title: 'Company',
                links: [
                  { label: 'About', href: '/about' },
                  { label: 'Blog', href: '/blog' },
                  { label: 'Careers', href: '/careers' },
                  { label: 'Press', href: '/press' },
                  { label: 'Contact', href: '/contact' },
                ],
              },
              {
                title: 'Legal',
                links: [
                  { label: 'Privacy Policy', href: '/legal/privacy' },
                  { label: 'Terms of Service', href: '/legal/terms' },
                  { label: 'Cookie Policy', href: '/legal/cookies' },
                  { label: 'DPA', href: '/legal/dpa' },
                  { label: 'Security', href: '/security' },
                ],
              },
            ].map((col) => (
              <div key={col.title}>
                <h4 className="text-sm font-semibold text-secondary-900">{col.title}</h4>
                <ul className="mt-3 space-y-2">
                  {col.links.map((l) => (
                    <li key={l.href}>
                      <Link
                        href={l.href}
                        className="text-sm text-secondary-500 hover:text-secondary-900 transition-colors"
                      >
                        {l.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-secondary-100 pt-8 sm:flex-row">
            <p className="text-xs text-secondary-400">
              © {new Date().getFullYear()} Talentora AI SAS. All rights reserved. Registered in France.
            </p>
            <div className="flex items-center gap-4 text-xs text-secondary-400">
              <span className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-success-500 animate-pulse-subtle" />
                All systems operational
              </span>
              <Link href="/status" className="hover:text-secondary-700">Status</Link>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
