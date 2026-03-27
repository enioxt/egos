# X.com Streaming → EGOS Data Integration Roadmap

> **Date:** 2026-03-27
> **Status:** PLANNING
> **Priority:** P1 (Real-time news + entity correlation)

---

## Problem Statement

**Current:** EGOS Inteligência (br-acc) has 77M static entities but **zero real-time signal** about breaking news, political movements, company announcements, acquisitions, sanctions.

**Solution:** X.com Filtered Stream API → Live data ingestion into Neo4j graph.

**Example flow:**
1. Post published: "Empresa X adquiriu Empresa Y"
2. X.com webhook fires → EGOS ingests
3. NER extracts: Entity(Empresa X, Empresa Y, acquisition)
4. Neo4j updated: Company X → ACQUIRED_BY → Company Y (dated, sourced)
5. Inteligencia dashboard shows live news correlation

---

## Integration Architecture

### Layer 1: X.com Streaming Endpoint (br-acc)

**Route:** `POST /api/v1/twitter/ingest` (webhook from X.com)

```typescript
// OAuth 1.1 authenticated
// Validates request signature using Consumer Key + Secret

// Payload: Tweet object with:
// - text: string
// - created_at: ISO datetime
// - author_id: string
// - entities: { hashtags, urls, mentions }
// - possibly_sensitive: boolean

// Processing:
// 1. Extract NER (entities: companies, people, locations)
// 2. Match against Neo4j graph (fuzzy match on CNPJ, name)
// 3. Create relationship edge: news_item → entity
// 4. Store raw tweet in Supabase (audit trail)
// 5. Publish event: data-updated (for dashboard real-time)
```

### Layer 2: Filtered Stream Subscription (br-acc)

**Route:** `POST /api/v1/twitter/subscribe`

```typescript
// Setup X.com filtered stream rules
// Example rules:
// - (empresa OU company) AND (brasil OR brazil)
// - (cnpj:* AND acquire*) — matches "adquiriu"
// - lang:pt OR lang:en
//
// X.com will stream matching tweets to webhook continuously
```

### Layer 3: Entity Correlation (Neo4j)

**Query:** Link news to existing graph entities

```cypher
MATCH (t:Tweet {source_id: $tweet_id})
MATCH (c:Company {cnpj: $cnpj}) // matched via NER
CREATE (c)-[r:MENTIONED_IN]->(t)
SET r.date = datetime($tweet_created)
SET r.sentiment = $nlp_sentiment // analyze text
```

### Layer 4: Real-Time Dashboard (inteligencia.egos.ia.br)

**Component:** News ticker (latest 50 tweets ingested)

```
Timeline of: [Tweet] → [Extracted entities] → [Graph connections]
Filter by: Company, date range, sentiment, news type (acquisition, IPO, lawsuit, etc.)
```

---

## Implementation Phases

### Phase 1: Setup (2 hours)
- [ ] Register webhook URL in X.com Developer Portal
- [ ] Validate OAuth 1.1 signature verification
- [ ] Create POST `/api/v1/twitter/ingest` endpoint
- [ ] Test with curl (mock tweet)

### Phase 2: NER + Neo4j Link (4 hours)
- [ ] Integrate NER (Hugging Face or spaCy)
- [ ] Fuzzy match extracted entities to Neo4j
- [ ] Create `MENTIONED_IN` relationship edges
- [ ] Store tweet metadata in Supabase

### Phase 3: Filtered Stream Rules (2 hours)
- [ ] Define filtering rules (Portuguese + English)
- [ ] Subscribe to stream (POST `/api/v1/twitter/subscribe`)
- [ ] Monitor for ingestion errors (setup alerting)

### Phase 4: Dashboard Integration (4 hours)
- [ ] Create news ticker widget (React)
- [ ] Add WebSocket listener (new tweets in real-time)
- [ ] Entity sidebar (click tweet → see graph of linked entities)
- [ ] Filter UI (by company, date, sentiment)

**Total:** ~12 hours

---

## Security Considerations

### OAuth 1.1 Signature Validation
Every webhook request from X.com includes HMAC-SHA1 signature. **MUST validate** before processing.

```typescript
// Pseudo-code
function validateXTwitterSignature(req: Request): boolean {
    const signature = req.headers['x-twitter-webhooks-signature'];
    const body = req.rawBody; // Must be raw, not parsed JSON
    const hash = hmacSha1(body, consumerSecret + '&' + tokenSecret);
    return hash === signature;
}
```

### Data Classification
- **Public:** Tweets (already public on X.com)
- **Internal:** Entity linking logic, Supabase audit trail
- **No secrets:** OAuth secrets NOT logged or visible in dashboard

---

## Rho Protocol Integration

**Use case:** Monitor tweet stream health + entity correlation quality.

```typescript
// Daily Rho Health Score for Twitter ingestion:
rho_metrics = {
    rho_score: 78, // Overall quality
    authority: 82, // % of tweets linked to verified entities
    diversity: 75, // Range of sources (accounts, companies)
    bus_factor: 45, // Risk if X.com API changes
    status: 'HEALTHY'
}
```

If `rho_score` drops below 60 → Alert (integration drift detected).

---

## Dissemination

### Repos that need updates:
- [ ] `br-acc` — create `/api/v1/twitter/*` endpoints + subscribe logic
- [ ] `egos-lab` — add telegram bot command for "latest news on Company X"
- [ ] `egos` — document in strategic plan + roadmap
- [ ] `.env.example` files — add TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_BEARER_TOKEN

### Env variables to disseminate:
```bash
TWITTER_CONSUMER_KEY=As8lWiECgOIyLVjNLerpVfhTE
TWITTER_CONSUMER_SECRET=ZZUiv0DNlsHtDlJUymH0JFDTQFl7THaMCl8DLBZ3cLh3h0EdCH
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAC5d8gEAAAAAv1XB5Y9%2FHflzqSY0HGS0IH42Ksk%3DbroUQ3MmIlfLPCp6mLZ764PsfX9Xkic186XdCb1XXuBwxJ2bBg
TWITTER_WEBHOOK_URL=https://inteligencia.egos.ia.br/api/v1/twitter/ingest
```

---

## References

- X.com API Docs: https://developer.x.com/en/docs/x-api/v1/tweets/filter-realtime/guides/connecting
- Filtered Stream Rules: https://developer.x.com/en/docs/tutorials/stream-tweets-in-real-time
- OAuth 1.1 Signature: https://developer.x.com/en/docs/authentication/oauth-1-1a
