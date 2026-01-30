# Developer API Strategy
## Citadel × TradeSynapse Protocol

**Brand:** Citadel | **Protocol:** TradeSynapse  
**Last Updated:** January 30, 2026  
**Status:** Phase 0 Planning

---

## Executive Summary

Citadel provides a **Freemium API ecosystem** enabling developers to build on top of autonomous capital allocation. Three tiers (Free, Pro, Enterprise) unlock REST, SDK, white-label, and marketplace capabilities. Revenue comes from: API subscriptions, marketplace transaction fees, white-label revenue share, and strategy licensing.

**Projected Developer API Revenue:**
- Year 1: $200K (early adopters)
- Year 2: $2M+ (scaling integrations)
- Year 3: $5M+ (mature marketplace)

---

## API Tiers Overview

| **Feature** | **Free** | **Pro** | **Enterprise** |
|-----------|---------|--------|----------------|
| **Cost** | Free | $99/mo | Custom |
| **API Requests/day** | 100 | 10,000 | Unlimited |
| **Rate Limit** | 1 req/sec | 100 req/sec | Custom |
| **API Endpoints** | Read-only | Read + Write | Full |
| **Webhooks** | ❌ | ✅ | ✅ |
| **Custom Strategies** | ❌ | ❌ | ✅ |
| **White-Label** | ❌ | ❌ | ✅ |
| **SLA** | Best effort | 99.5% | 99.99% |
| **Support** | Community | Email | Dedicated |
| **Use Cases** | Testing, learning | Production apps | Exchanges, wealth managers |

---

## Tier 1: Free API (Freemium Entry)

### Purpose
Enable developers to experiment, test integrations, learn the API without financial commitment.

### Features
- **100 requests/day** (sufficient for testing)
- **Read-only endpoints** (GET /wallet, GET /strategy, GET /performance, etc.)
- **No webhooks** (polling only)
- **Rate: 1 request/second**
- **No commercial use** (personal projects only)
- **Community support** (Discord, GitHub discussions)

### Included Endpoints
```
GET  /v1/auth/me
GET  /v1/wallets
GET  /v1/wallets/{id}/balances
GET  /v1/strategies/queue
GET  /v1/strategies/{id}/performance
GET  /v1/entities/perception/signals
GET  /v1/entities/risk/confidence
GET  /v1/audit/trail
GET  /v1/token/price
GET  /v1/token/holders
```

### Example: Free Tier Developer
```javascript
// Portfolio tracker reading Citadel data
const response = await fetch('https://api.citadel.finance/v1/wallets/123/balances', {
  headers: { 'Authorization': 'Bearer FREE_KEY_xxx' }
});
const balances = await response.json();
// Display on personal dashboard (no commercial use)
```

### Upgrade Path
→ Needs webhooks? → Pro ($99/mo)  
→ Needs write access? → Pro ($99/mo)  
→ Building a platform? → Enterprise

---

## Tier 2: Pro API ($99/mo)

### Purpose
Production integrations, commercial apps, active development.

### Features
- **10,000 requests/day** (production workload)
- **Read + Write endpoints** (can execute strategies, update preferences)
- **Webhooks** (real-time events without polling)
- **Rate: 100 requests/second**
- **Commercial use allowed** (apps, integrations, dashboards)
- **Priority email support**
- **99.5% SLA**

### Included Endpoints
```
# Read (all Free tier + more)
GET  /v1/strategies/{id}/metrics
GET  /v1/entities/strategy/decisions
GET  /v1/performance/analytics
GET  /v1/guardians/checks

# Write (Pro tier exclusive)
POST /v1/strategies/{id}/veto
POST /v1/strategies/{id}/adjust-threshold
POST /v1/user/preferences/update
POST /v1/webhook/subscribe
```

### Webhook Events
```
strategy.executed
strategy.vetoed
profit.claimed
risk.alert
entity.decision
wallet.funded
```

### Example: Pro Tier Developer
```javascript
// Third-party portfolio aggregator
const citadelClient = new CitadelAPI('PRO_KEY_xxx');

// Subscribe to real-time events
citadelClient.on('strategy.executed', (event) => {
  console.log(`Strategy ${event.strategyId} executed: +${event.profit}`);
  updateDashboard(event);
});

// Programmatically veto risky strategies
if (riskScore > 0.8) {
  await citadelClient.vetoStrategy(strategyId, 'Risk too high');
}
```

### Pricing Model
- **Base: $99/month**
- **Overage: $0.01 per 100 extra requests/day**
- **Webhook events: included in 10k limit**

### Upgrade Path
→ Need custom strategies? → Enterprise  
→ Need white-label? → Enterprise  
→ Building platform? → Enterprise

---

## Tier 3: Enterprise API (Custom Pricing)

### Purpose
Platform integrations, white-label solutions, custom strategies.

### Features
- **Unlimited requests/day**
- **All endpoints** (read, write, admin)
- **Custom strategies** (deploy on Citadel infrastructure)
- **White-label support** (private API, branded dashboard)
- **Webhooks + real-time data streams**
- **Rate: unlimited (custom SLA)**
- **99.99% SLA**
- **Dedicated support + technical account manager**

### Included Endpoints
```
# All Pro endpoints + Enterprise:
POST /v1/strategies/custom/deploy
POST /v1/entities/signal/inject
POST /v1/audit/export (full history)
POST /v1/api-keys/manage
DELETE /v1/api-keys/{id}
GET  /v1/admin/dashboard
```

### Custom Strategies
Deploy proprietary trading strategies on TradeSynapse:
```solidity
// Enterprise developer's custom strategy
contract CustomStrategy is IStrategy {
  function evaluate(Market memory market) external returns (Decision) {
    // Custom ML model evaluation
    return decideAllocation(market.signals);
  }
}
```

### White-Label Benefits
- Private API endpoints (yourdomain.com/api/v1)
- Branded documentation
- Custom rate limits per endpoint
- Multi-tenant isolation
- Revenue share: 80/20 (you get 80% of profits generated)

### Enterprise Pricing Model
**Starting at: $10K/month + 20% revenue share on profits**

Example:
- Crypto exchange integrates Citadel
- Users allocate $10M to Citadel
- Citadel generates $500K profit/year
- Exchange pays: $120K/year + $100K (20% revenue share) = $220K total

---

## Developer Marketplace (Phase 2)

### Concept
Developers publish custom strategies to Citadel Marketplace. Users discover, install, activate.

### Revenue Model
```
User profit from strategy: $1,000
├─ Creator gets: $700 (70%)
├─ Citadel gets: $200 (20%)
└─ Network/infrastructure: $100 (10%)
```

### Example Marketplace Strategies
- **"ML Momentum"** by @TradeDev — AI-powered trend detection
- **"Arbitrage Hunter"** by @CryptoBot — Cross-exchange spreads
- **"Risk-Averse Conservative"** by @SafeTrader — Low-volatility allocation
- **"Aggressive Growth"** by @Degenerate — High-risk high-reward

### Developer Publishing Flow
```
1. Code strategy in Solidity/Python
2. Test on devnet
3. Submit to marketplace (Citadel reviews)
4. Set price tier (Free, $10, $50, $100, Custom)
5. Deploy to mainnet
6. Users install → earn profits
7. Creator earns 70% of generated profits
```

### Marketplace Economics
- **Year 1:** 10 strategies, $50K marketplace revenue
- **Year 2:** 100 strategies, $500K marketplace revenue
- **Year 3:** 500+ strategies, $3M+ marketplace revenue

---

## REST API Endpoints (Complete List)

### Authentication
```
POST /v1/auth/register
POST /v1/auth/login
POST /v1/auth/refresh
GET  /v1/auth/me
```

### Wallets
```
GET  /v1/wallets
GET  /v1/wallets/{id}
GET  /v1/wallets/{id}/balances
POST /v1/wallets/{id}/deposit
POST /v1/wallets/{id}/withdraw
GET  /v1/wallets/{id}/transactions
```

### Strategies
```
GET  /v1/strategies
GET  /v1/strategies/{id}
GET  /v1/strategies/{id}/performance
GET  /v1/strategies/{id}/trades
GET  /v1/strategies/queue
POST /v1/strategies/{id}/veto
POST /v1/strategies/{id}/adjust-threshold
POST /v1/strategies/custom/deploy (Enterprise)
```

### Entities
```
GET  /v1/entities/perception/signals
GET  /v1/entities/memory/patterns
GET  /v1/entities/risk/confidence
GET  /v1/entities/strategy/decisions
GET  /v1/entities/execution/status
```

### Performance & Analytics
```
GET  /v1/performance/overview
GET  /v1/performance/daily
GET  /v1/performance/monthly
GET  /v1/performance/roi
GET  /v1/analytics/trades
GET  /v1/analytics/drawdown
```

### Guardian & Approval
```
GET  /v1/guardians/checks
POST /v1/guardians/approve
POST /v1/guardians/reject
GET  /v1/guardians/history
```

### Token (TST)
```
GET  /v1/token/price
GET  /v1/token/supply
GET  /v1/token/holders
GET  /v1/token/staking
POST /v1/token/claim-airdrop
POST /v1/token/stake
POST /v1/token/unstake
```

### Audit & Compliance
```
GET  /v1/audit/trail
POST /v1/audit/export
GET  /v1/audit/events/{id}
```

---

## SDK Support (Phase 1)

### JavaScript/TypeScript
```bash
npm install @citadel/api
```

```typescript
import { CitadelAPI } from '@citadel/api';

const client = new CitadelAPI({
  apiKey: process.env.CITADEL_API_KEY,
  tier: 'pro'
});

// List wallets
const wallets = await client.wallets.list();

// Get performance
const perf = await client.performance.getMonthly('2026-01-01', '2026-01-31');

// Subscribe to events
client.on('strategy.executed', (event) => {
  console.log(`Profit: $${event.profit}`);
});
```

### Python
```bash
pip install citadel-api
```

```python
from citadel import CitadelAPI

client = CitadelAPI(api_key=os.getenv('CITADEL_API_KEY'))

# Get wallet balances
balances = client.wallets.get_balances('wallet_123')

# Veto a strategy
client.strategies.veto('strategy_456', reason='Too risky')

# Stream events
for event in client.stream_events(['strategy.executed', 'profit.claimed']):
    print(f"Event: {event['type']}")
```

### Web3.js Integration
```javascript
import { ethers } from 'ethers';
import { CitadelStrategy } from '@citadel/contracts';

const strategyAddress = '0x...';
const strategy = new ethers.Contract(strategyAddress, CitadelStrategy.ABI);

// Read strategy decisions
const decisions = await strategy.getDecisions();

// Call strategy methods (requires signing)
const tx = await strategy.vetoDecision(decisionId);
await tx.wait();
```

---

## Rate Limiting & Quotas

### Free Tier
- **100 requests/day**
- **1 request/second**
- Reset at 00:00 UTC
- 429 (Too Many Requests) if exceeded

### Pro Tier
- **10,000 requests/day**
- **100 requests/second**
- Bursting allowed up to 500 req/sec
- Reset at 00:00 UTC
- Overage: $0.01 per 100 requests

### Enterprise Tier
- **Unlimited**
- **Custom rate limits per endpoint**
- **Custom SLA (usually 99.99%)**

### Response Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1643635200
X-RateLimit-Used: 58
```

---

## Developer Experience

### Documentation
- **Interactive API explorer** (Swagger UI)
- **Code examples** (JS, Python, Solidity)
- **Webhook testing sandbox**
- **API status page** (status.citadel.finance)

### Developer Tools
- **CLI tool** (`citadel-cli`)
- **Local testing framework** (Hardhat plugin)
- **Postman collection** (downloadable)
- **Terraform/Pulumi modules** (infrastructure-as-code)

### Community
- **Discord** (#api-support, #marketplace)
- **GitHub discussions** (github.com/citadel/api)
- **Monthly webinars** (API deep dives)
- **Hackathons** (quarterly $50K prize pool)

---

## Revenue Projections

### Year 1 (2026-2027)
- Free tier: 500 developers (no revenue)
- Pro tier: 50 developers × $99/mo × 12 = $59.4K
- Enterprise: 2 deals × $15K/mo × 12 = $360K
- Marketplace: $50K (10 strategies)
- **Total Year 1: $469.4K**

### Year 2 (2027-2028)
- Free tier: 2,000 developers (ecosystem)
- Pro tier: 300 developers × $99/mo × 12 = $356.4K
- Enterprise: 10 deals × $20K/mo × 12 = $2.4M
- Marketplace: $500K (100 strategies)
- White-label revenue share: $600K
- **Total Year 2: $3.856M**

### Year 3 (2028-2029)
- Free tier: 5,000 developers (ecosystem effect)
- Pro tier: 800 developers × $99/mo × 12 = $950.4K
- Enterprise: 25 deals × $25K/mo × 12 = $7.5M
- Marketplace: $3M (500 strategies)
- White-label revenue share: $1.5M
- **Total Year 3: $13M+**

---

## Implementation Roadmap

### Phase 1 (Weeks 3-4 of Phase 0)
- ✅ Basic REST API (read-only, Free tier)
- ✅ JavaScript SDK
- ✅ Python SDK
- ✅ API documentation + Swagger UI
- ✅ Rate limiting + quota management
- ✅ Basic monitoring/analytics

### Phase 2 (Weeks 1-2 of Phase 1)
- ✅ Pro tier (write endpoints, webhooks)
- ✅ Webhook event system
- ✅ API key management dashboard
- ✅ CLI tool (`citadel-cli`)
- ✅ Community support channels

### Phase 3 (Phase 1+)
- ✅ Enterprise tier (white-label, custom strategies)
- ✅ Marketplace platform
- ✅ Strategy publishing workflow
- ✅ Revenue splitting & payouts
- ✅ Developer analytics dashboard

---

## Security Considerations

### API Keys
- **Rotatable keys** (Pro/Enterprise)
- **Scoped permissions** (read-only, write, admin)
- **IP whitelisting** (Enterprise)
- **OAuth 2.0 support** (coming Phase 2)

### Data Protection
- **All endpoints HTTPS/TLS 1.3**
- **Request signing** (prevent tampering)
- **Rate limiting** (prevent abuse)
- **API audit logs** (Pro/Enterprise)

### Compliance
- **SOC 2 Type II** (Year 1)
- **GDPR compliant** (data deletion, privacy)
- **AML/KYC integration** (Enterprise)

---

## Success Metrics

By end of Year 1:
- ✅ 500+ active developers (Free tier)
- ✅ 50+ Pro tier subscriptions
- ✅ 2+ Enterprise partnerships
- ✅ 10+ marketplace strategies
- ✅ $469K ARR from APIs
- ✅ 99.9% API uptime
- ✅ <200ms average response time

By end of Year 2:
- ✅ 2,000+ developers
- ✅ 300+ Pro subscriptions
- ✅ 10+ Enterprise deals
- ✅ 100+ marketplace strategies
- ✅ $3.8M+ ARR from APIs
- ✅ 99.95% API uptime

---

## Questions & Next Steps

**Ready to build?**
1. Review this strategy with team
2. Finalize API endpoint contracts (technical specs)
3. Design SDK architecture
4. Plan Phase 1 Week 3 API implementation

**Questions?**
- What endpoints are highest priority?
- Should we support GraphQL alongside REST?
- Any specific SDK languages we're missing?

---

**Status:** Planning Complete → Ready for Phase 1 Implementation  
**Owner:** Product Team  
**Last Review:** January 30, 2026
