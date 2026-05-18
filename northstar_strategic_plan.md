# Northstar — Cold Outreach Strategic Plan
**Prepared for:** Breega Scaling Squad · RevOps & Growth Intern Case Study  
**Objective:** Double qualified demo pipeline from 8–10 to 16–20/month within 90 days

---

## 1. Diagnosis — Why the 1% Reply Rate Happened

The SDR's previous campaigns failed for three compounding reasons:

- **Wrong list**: Apollo bulk exports with only title/industry filters produce noisy lists with no signal about *why* a prospect would care *now*
- **No enrichment**: Without context (tech stack, recent hires, funding), every email sounds generic — and gets treated as spam
- **Generic copy**: "Hi {FirstName}, we help data teams…" — indistinguishable from the 40 other cold emails in the inbox

The root problem is not volume. It's relevance. Doubling sends on the same approach would double the noise, not the pipeline.

---

## 2. ICP Definition — Getting Specific

**Target personas** (in priority order):

| Tier | Title | Why They Care |
|------|-------|---------------|
| A | Head of Data / VP Data | Budget owner, directly accountable for data quality |
| A | Data Engineering Manager | Day-to-day pain with governance gaps |
| B | CDO / CTO | Strategic buyer at Series B+ |
| B | Analytics Lead | Proxy buyer, strong influencer |

**Company filters:**

- **Geography**: France, Germany, Netherlands, UK, Spain (GDPR pressure = strongest governance need)
- **Stage**: Series A to Series C, raised within the last 24 months (budget unlocked, scaling pain active)
- **Headcount**: 50–500 employees (Northstar's defined ICP)
- **Tech stack signals**: dbt, Snowflake, BigQuery, Databricks, Fivetran — companies using modern data stacks feel governance gaps acutely
- **Hiring signal**: Active job postings for Data Engineers or Analytics Engineers = data team scaling = governance needed

**Negative filters (exclusions):**

- Pre-seed / bootstrap (no budget)
- >500 employees (enterprise sales cycle, wrong motion)
- B2C companies (lower data governance regulatory pressure)
- Competitors' customers (detected via job postings mentioning competing tools)

---

## 3. The Machine — Architecture

The outreach machine has four sequential stages upstream of the sending tool:

```
[1. SOURCING] → [2. ENRICHMENT] → [3. SCORING] → [4. PERSONALIZATION] → Sending Tool
```

**Stage 1 — Sourcing**  
Pull prospects from Apollo.io (free tier: 50 exports/month) or LinkedIn Sales Navigator trial. Filter by ICP criteria above. Target: 100–200 raw prospects/week.

**Stage 2 — Enrichment** (the differentiator)  
For each prospect, layer on:
- Company funding data (Crunchbase/Dealroom via Clay)
- Tech stack (BuiltWith or Clay's tech enrichment)
- Recent hiring signals (job postings via Adzuna API or LinkedIn scrape)
- Prospect's recent LinkedIn activity (recent posts, job changes)

**Stage 3 — Scoring**  
Assign each prospect an ICP score (0–10):

| Signal | Points |
|--------|--------|
| dbt / Snowflake / BigQuery in stack | +2 |
| Funded in last 12 months | +2 |
| Actively hiring data engineers | +2 |
| Headcount 50–200 (sweet spot) | +1 |
| Head of Data title (Tier A) | +2 |
| Recent LinkedIn activity (last 30 days) | +1 |

Score ≥ 7 → **Tier A** (priority outreach, manual personalization)  
Score 4–6 → **Tier B** (semi-personalized sequence)  
Score < 4 → **Tier C** (deprioritize or discard)

**Stage 4 — Personalization**  
AI-generated opening line per prospect using their enrichment data as context:
- Recent funding → "Congrats on the Series B — scaling your data team fast often surfaces governance gaps before you expect them."
- dbt in stack → "Saw you're running dbt at [Company] — teams at that stage often hit a wall when lineage and access control start diverging."
- Hiring signal → "You're hiring two Data Engineers right now — that's usually when data quality incidents start compounding."

Output: enriched CSV with `personalization_line` column, ready to plug into Instantly or Lemlist.

---

## 4. Stack Choices & Rationale

| Tool | Purpose | Cost | Why This |
|------|---------|------|----------|
| **Apollo.io** | Lead sourcing | Free (50 exports) | Best free-tier data for B2B; GDPR-compliant |
| **Clay** | Enrichment + AI personalization | Free trial (~$149/mo paid) | Best-in-class enrichment orchestrator; built for exactly this workflow |
| **Hunter.io** | Email verification | Free (25/mo) | Reduces bounce rate, protects domain reputation |
| **Instantly.ai** | Sending | ~$37/mo | Best deliverability + inbox rotation for cold email |
| **Google Sheets** | Pipeline tracking | Free | Simple, shareable, plugs into Clay |
| **Python script** | Fallback enrichment pipeline | Free | Custom logic when Clay trial expires |

**Total estimated monthly cost: ~$186/mo** (well under the €600 cap; leaves room for Clay paid tier at scale)

**If Clay trial is unavailable:** The Python script in this submission replicates the enrichment + scoring + personalization logic using free APIs (Hunter, Crunchbase public data, OpenAI/Claude API).

---

## 5. Sequence Strategy

**Recommended sequence structure (5 touches over 14 days):**

| Touch | Channel | Timing | Angle |
|-------|---------|--------|-------|
| 1 | Email | Day 0 | Personalized opener + 1 specific pain |
| 2 | LinkedIn | Day 2 | Connection request (no pitch) |
| 3 | Email | Day 5 | Case study or relevant insight |
| 4 | Email | Day 9 | Different angle / objection handle |
| 5 | Email | Day 14 | Breakup email ("closing your file") |

**Subject line principle:** Never mention the product. Lead with the prospect's world.  
Example: *"your data stack post Series B"* vs *"data governance solution for you"*

---

## 6. 90-Day Roadmap & KPIs

| Month | Actions | KPI Target |
|-------|---------|-----------|
| **Month 1** | ICP finalization, Clay setup, first 100 leads enriched, sequence A/B test | Open rate >40%, Reply rate >3% |
| **Month 2** | Scale to 300 leads/month, optimize top-performing sequence variant | 8+ new meetings booked |
| **Month 3** | Full cadence, add LinkedIn touchpoints, SDR reviews and personalizes Tier A leads | 10–12 new meetings/month |

**North Star metric:** Qualified demos from cold outreach ≥ 10/month by Month 3 (doubling total pipeline to 18–20).

---

## 7. Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| GDPR compliance on cold email | Use legitimate interest basis; always include unsubscribe; target professional emails only |
| Domain reputation damage from bulk send | Warm up new sending domain (Instantly auto-warmup); cap at 30 emails/day initially |
| Clay trial expiring | Python fallback pipeline covers core enrichment logic |
| SDR capacity bottleneck | Tier A leads get manual review (max 20/week); Tiers B/C are fully automated |
