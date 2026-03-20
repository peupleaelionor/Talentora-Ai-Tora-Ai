# Monetisation Strategy

## Pricing Tiers

| | Free | Starter | Pro | Team | Enterprise |
|---|---|---|---|---|---|
| **Price/month** | €0 | €49 | €149 | €399 | Custom |
| API calls/month | 100 | 5,000 | 25,000 | 100,000 | Unlimited |
| Salary benchmarks | Limited | ✅ | ✅ | ✅ | ✅ |
| Skills trends | 7 days | 90 days | 1 year | 3 years | Unlimited |
| Reports/month | 1 | 10 | 50 | Unlimited | Unlimited |
| CSV exports | ❌ | ✅ | ✅ | ✅ | ✅ |
| API access | ❌ | ❌ | ✅ | ✅ | ✅ |
| Users | 1 | 1 | 3 | 15 | Unlimited |
| SLA | None | None | 99.5% | 99.9% | 99.99% |
| Support | Community | Email | Priority | Dedicated | SLA-backed |

## Revenue Scenarios

### Conservative (Month 12)
- 500 Free → 5% conversion = 25 Starter (€1,225/mo)
- 100 Starter → 15% upgrade = 15 Pro (€2,235/mo)
- 10 Pro → 20% upgrade = 2 Team (€798/mo)
- **MRR: ~€4,258**

### Base (Month 18)
- 2,000 Free → 6% = 120 Starter (€5,880)
- 120 Starter → 20% = 24 Pro (€3,576)
- 24 Pro → 25% = 6 Team (€2,394)
- 1 Enterprise (€1,500)
- **MRR: ~€13,350**

### Optimistic (Month 24)
- 10,000 Free → 7% = 700 Starter (€34,300)
- 700 Starter → 20% = 140 Pro (€20,860)
- 140 Pro → 15% = 21 Team (€8,379)
- 5 Enterprise avg €3k = €15,000
- **MRR: ~€78,539**

## Billing Implementation

- **Provider**: Stripe Billing (subscriptions + webhooks)
- **Flow**: Checkout session → Stripe-hosted page → webhook `checkout.session.completed` → activate workspace plan
- **Metering**: API call counter in Redis, synced to `workspaces.monthly_api_calls` hourly
- **Overage**: Soft limit warning at 80%, hard limit at 100% with 429 responses
- **Upgrades**: Stripe prorates automatically
- **Cancellation**: Downgrade to Free at period end; data retained 90 days

## Growth Strategy

1. **SEO content**: "Average Python developer salary France 2024" — organic acquisition
2. **Freemium funnel**: Free tier creates habit; gate advanced features behind paywall
3. **Developer API**: Starter+ API access drives B2B integration (ATS vendors)
4. **HR community**: Partner with ANDRH, Cadremploi for co-marketing
5. **Data partnerships**: License aggregated (anonymised) data to consulting firms
6. **Referral programme**: 1 month free for each paying referral
