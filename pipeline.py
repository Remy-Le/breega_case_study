"""
Northstar Cold Outreach — Lead Enrichment Pipeline
====================================================
Turns a raw prospect list into an enriched, scored, personalized CSV
ready to plug into Instantly / Lemlist.

Pipeline stages:
  1. Load raw prospects (CSV or generate sample dataset)
  2. Enrich with company & tech stack signals
  3. Score each lead (ICP fit 0–10)
  4. Generate personalized opening lines via Claude API
  5. Export enriched CSV (tiered, sorted by score)

Usage:
  python pipeline.py                         # runs on built-in sample dataset
  python pipeline.py --input leads.csv       # runs on your own CSV
  python pipeline.py --input leads.csv --api-key sk-ant-...  # with real AI personalization
"""

import argparse
import csv
import json
import os
import random
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
import urllib.request
import urllib.parse

# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class RawProspect:
    first_name: str
    last_name: str
    title: str
    company: str
    company_domain: str
    linkedin_url: str = ""
    email: str = ""

@dataclass
class EnrichedLead:
    # Identity
    first_name: str
    last_name: str
    title: str
    company: str
    company_domain: str
    email: str
    linkedin_url: str

    # Enrichment signals
    tech_stack: list = field(default_factory=list)
    funding_round: str = ""
    funding_amount_m: float = 0.0
    months_since_funding: int = 99
    headcount: int = 0
    headcount_growth_pct: int = 0
    data_team_size: int = 0
    hiring_data_engineers: bool = False
    recent_linkedin_post: str = ""

    # Scoring
    icp_score: int = 0
    tier: str = "C"
    score_breakdown: dict = field(default_factory=dict)

    # Personalization
    personalization_line: str = ""
    email_subject: str = ""


# ─────────────────────────────────────────────
# SAMPLE DATASET (realistic mock data)
# ─────────────────────────────────────────────

SAMPLE_PROSPECTS = [
    RawProspect("Sophie", "Martin", "Head of Data", "Pennylane", "pennylane.tech", "linkedin.com/in/sophiemartin"),
    RawProspect("Lucas", "Müller", "Data Engineering Manager", "Spendesk", "spendesk.com", "linkedin.com/in/lucasmuller"),
    RawProspect("Emma", "Dubois", "VP Analytics", "Alan", "alan.com", "linkedin.com/in/emmadubois"),
    RawProspect("Jan", "Van Berg", "Head of Data Engineering", "Mollie", "mollie.com", "linkedin.com/in/janvanberg"),
    RawProspect("Marie", "Leclerc", "CDO", "Doctolib", "doctolib.fr", "linkedin.com/in/marieleclerc"),
    RawProspect("Thomas", "Schmidt", "Analytics Lead", "N26", "n26.com", "linkedin.com/in/thomasschmidt"),
    RawProspect("Clara", "Rossi", "Data Platform Lead", "Satispay", "satispay.com", "linkedin.com/in/clararossi"),
    RawProspect("Antoine", "Bernard", "Head of Data", "Qonto", "qonto.com", "linkedin.com/in/antoinebernard"),
    RawProspect("Lena", "Fischer", "Senior Data Engineer", "Gorillas", "gorillas.io", "linkedin.com/in/lenafischer"),
    RawProspect("Pablo", "Garcia", "VP Data", "Holded", "holded.com", "linkedin.com/in/pablogarcia"),
    RawProspect("Ingrid", "Svensson", "Data Engineering Manager", "Klarna", "klarna.com", "linkedin.com/in/ingridsvensson"),
    RawProspect("Romain", "Petit", "Head of BI", "Payfit", "payfit.com", "linkedin.com/in/romainpetit"),
    RawProspect("Sophia", "Andersen", "Chief Data Officer", "Pleo", "pleo.io", "linkedin.com/in/sophiaandersen"),
    RawProspect("Markus", "Weber", "Analytics Engineering Lead", "Personio", "personio.com", "linkedin.com/in/markusweber"),
    RawProspect("Julie", "Moreau", "Head of Data", "Lunchr", "swile.co", "linkedin.com/in/juliemoreau"),
    RawProspect("Carlos", "López", "Data Platform Manager", "Factorial", "factorialhr.com", "linkedin.com/in/carloslopez"),
    RawProspect("Anna", "Kowalski", "VP Data & Analytics", "Brainly", "brainly.com", "linkedin.com/in/annakowalski"),
    RawProspect("Pierre", "Durand", "Head of Data Engineering", "Deezer", "deezer.com", "linkedin.com/in/pierredurand"),
    RawProspect("Henrik", "Nielsen", "Analytics Manager", "Vivino", "vivino.com", "linkedin.com/in/henriknielsen"),
    RawProspect("Laura", "Bianchi", "Head of Data", "Musixmatch", "musixmatch.com", "linkedin.com/in/laurabianchi"),
]

# ─────────────────────────────────────────────
# MOCK ENRICHMENT DATABASE
# Each entry simulates what Clay / BuiltWith / Crunchbase would return
# ─────────────────────────────────────────────

MOCK_ENRICHMENT_DB = {
    "pennylane.tech":     {"tech": ["dbt", "Snowflake", "Fivetran", "Looker"],   "funding": "Series C", "amount": 57,  "months_ago": 8,  "hc": 600,  "hc_growth": 40, "data_team": 8,  "hiring_de": True,  "post": "Just wrapped migrating our entire data stack to dbt + Snowflake. Lessons learned incoming 🧵"},
    "spendesk.com":       {"tech": ["dbt", "BigQuery", "Airbyte"],               "funding": "Series C", "amount": 100, "months_ago": 14, "hc": 500,  "hc_growth": 25, "data_team": 6,  "hiring_de": True,  "post": "Hiring two Data Engineers to scale our analytics infra — DM if interested"},
    "alan.com":           {"tech": ["Snowflake", "dbt", "Tableau"],              "funding": "Series E", "amount": 183, "months_ago": 6,  "hc": 550,  "hc_growth": 20, "data_team": 10, "hiring_de": False, "post": "Data quality is becoming our #1 priority as we scale across 3 countries"},
    "mollie.com":         {"tech": ["Databricks", "dbt", "Looker"],              "funding": "Series C", "amount": 665, "months_ago": 18, "hc": 800,  "hc_growth": 15, "data_team": 12, "hiring_de": True,  "post": ""},
    "doctolib.fr":        {"tech": ["Redshift", "Airflow", "Tableau"],           "funding": "Series D", "amount": 500, "months_ago": 30, "hc": 3000, "hc_growth": 10, "data_team": 20, "hiring_de": False, "post": "Scaling data governance in healthcare is a unique challenge"},
    "n26.com":            {"tech": ["Snowflake", "dbt", "Fivetran", "Metabase"], "funding": "Series E", "amount": 900, "months_ago": 24, "hc": 1500, "hc_growth": 5,  "data_team": 15, "hiring_de": True,  "post": ""},
    "satispay.com":       {"tech": ["BigQuery", "Looker", "dbt"],                "funding": "Series C", "amount": 320, "months_ago": 10, "hc": 350,  "hc_growth": 35, "data_team": 5,  "hiring_de": True,  "post": "Our data team just doubled — now figuring out how to keep data consistent across 5 product lines"},
    "qonto.com":          {"tech": ["dbt", "Snowflake", "Airbyte", "Metabase"],  "funding": "Series D", "amount": 486, "months_ago": 12, "hc": 1200, "hc_growth": 30, "data_team": 14, "hiring_de": True,  "post": "Just posted: looking for a Data Governance Lead — first of its kind at Qonto"},
    "gorillas.io":        {"tech": ["MySQL", "Redash"],                          "funding": "Series C", "amount": 290, "months_ago": 36, "hc": 800,  "hc_growth": -10,"data_team": 3,  "hiring_de": False, "post": ""},
    "holded.com":         {"tech": ["BigQuery", "dbt", "Looker"],                "funding": "Series B", "amount": 18,  "months_ago": 9,  "hc": 200,  "hc_growth": 28, "data_team": 4,  "hiring_de": True,  "post": "Building our data platform from scratch after Series B — exciting and chaotic"},
    "klarna.com":         {"tech": ["Databricks", "dbt", "Snowflake", "Airflow"],"funding": "IPO",      "amount": 0,   "months_ago": 99, "hc": 5000, "hc_growth": 0,  "data_team": 40, "hiring_de": False, "post": ""},
    "payfit.com":         {"tech": ["BigQuery", "Fivetran", "Looker"],           "funding": "Series D", "amount": 90,  "months_ago": 16, "hc": 700,  "hc_growth": 12, "data_team": 8,  "hiring_de": False, "post": "BI stack migration in progress — moving off legacy Tableau"},
    "pleo.io":            {"tech": ["Snowflake", "dbt", "Airbyte"],              "funding": "Series C", "amount": 150, "months_ago": 11, "hc": 450,  "hc_growth": 22, "data_team": 6,  "hiring_de": True,  "post": "Our Head of Data just wrote a great post on why we're investing in data contracts"},
    "personio.com":       {"tech": ["dbt", "BigQuery", "Looker", "Airflow"],     "funding": "Series E", "amount": 200, "months_ago": 20, "hc": 2000, "hc_growth": 15, "data_team": 18, "hiring_de": True,  "post": "Analytics engineering is the fastest-growing function at Personio right now"},
    "swile.co":           {"tech": ["BigQuery", "dbt"],                          "funding": "Series C", "amount": 200, "months_ago": 15, "hc": 400,  "hc_growth": 18, "data_team": 5,  "hiring_de": False, "post": ""},
    "factorialhr.com":    {"tech": ["Snowflake", "Fivetran", "Metabase"],        "funding": "Series C", "amount": 80,  "months_ago": 7,  "hc": 300,  "hc_growth": 32, "data_team": 4,  "hiring_de": True,  "post": "Scaling fast after Series C — data quality becoming a board-level concern"},
    "brainly.com":        {"tech": ["Redshift", "Airflow", "Tableau"],           "funding": "Series F", "amount": 80,  "months_ago": 40, "hc": 900,  "hc_growth": 5,  "data_team": 10, "hiring_de": False, "post": ""},
    "deezer.com":         {"tech": ["BigQuery", "dbt", "Looker"],                "funding": "IPO",      "amount": 0,   "months_ago": 99, "hc": 800,  "hc_growth": 0,  "data_team": 9,  "hiring_de": False, "post": ""},
    "vivino.com":         {"tech": ["Snowflake", "Looker"],                      "funding": "Series D", "amount": 155, "months_ago": 22, "hc": 250,  "hc_growth": 8,  "data_team": 3,  "hiring_de": False, "post": ""},
    "musixmatch.com":     {"tech": ["BigQuery", "dbt", "Metabase"],              "funding": "Series B", "amount": 9,   "months_ago": 5,  "hc": 120,  "hc_growth": 20, "data_team": 2,  "hiring_de": True,  "post": "Building our first proper data platform — dbt is a game changer"},
}

GOVERNANCE_TECH = {"dbt", "Snowflake", "BigQuery", "Databricks", "Fivetran", "Airbyte"}
TIER_A_TITLES = {"head of data", "vp data", "vp analytics", "cdo", "chief data officer",
                 "data engineering manager", "head of data engineering"}

# ─────────────────────────────────────────────
# STAGE 1 — LOAD PROSPECTS
# ─────────────────────────────────────────────

def load_prospects(filepath: Optional[str]) -> list[RawProspect]:
    if filepath and os.path.exists(filepath):
        prospects = []
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prospects.append(RawProspect(
                    first_name=row.get("first_name", ""),
                    last_name=row.get("last_name", ""),
                    title=row.get("title", ""),
                    company=row.get("company", ""),
                    company_domain=row.get("company_domain", ""),
                    linkedin_url=row.get("linkedin_url", ""),
                    email=row.get("email", ""),
                ))
        print(f"✅ Loaded {len(prospects)} prospects from {filepath}")
        return prospects
    else:
        print(f"ℹ️  Using built-in sample dataset ({len(SAMPLE_PROSPECTS)} prospects)")
        return SAMPLE_PROSPECTS

# ─────────────────────────────────────────────
# STAGE 2 — ENRICHMENT
# ─────────────────────────────────────────────

def enrich_prospect(prospect: RawProspect) -> EnrichedLead:
    """
    In production: calls Clay, BuiltWith, Crunchbase, Hunter APIs.
    Here: lookups against mock DB with fallback randomization.
    """
    domain = prospect.company_domain.lower()
    db = MOCK_ENRICHMENT_DB.get(domain, {})

    # Email generation (in prod: Hunter.io lookup)
    email = prospect.email
    if not email and domain:
        patterns = [
            f"{prospect.first_name.lower()}.{prospect.last_name.lower()}@{domain}",
            f"{prospect.first_name.lower()[0]}{prospect.last_name.lower()}@{domain}",
        ]
        email = patterns[0]  # In prod: verify with Hunter

    return EnrichedLead(
        first_name=prospect.first_name,
        last_name=prospect.last_name,
        title=prospect.title,
        company=prospect.company,
        company_domain=domain,
        email=email,
        linkedin_url=prospect.linkedin_url,
        tech_stack=db.get("tech", []),
        funding_round=db.get("funding", "Unknown"),
        funding_amount_m=db.get("amount", 0),
        months_since_funding=db.get("months_ago", 99),
        headcount=db.get("hc", 0),
        headcount_growth_pct=db.get("hc_growth", 0),
        data_team_size=db.get("data_team", 0),
        hiring_data_engineers=db.get("hiring_de", False),
        recent_linkedin_post=db.get("post", ""),
    )

# ─────────────────────────────────────────────
# STAGE 3 — SCORING
# ─────────────────────────────────────────────

def score_lead(lead: EnrichedLead) -> EnrichedLead:
    """
    ICP scoring model (0–10 points).
    Each signal reflects genuine buying intent or fit.
    """
    score = 0
    breakdown = {}

    # Tech stack — modern data stack = governance pain
    governance_tools = [t for t in lead.tech_stack if t in GOVERNANCE_TECH]
    if len(governance_tools) >= 2:
        score += 2
        breakdown["modern_data_stack"] = f"+2 ({', '.join(governance_tools[:3])})"
    elif len(governance_tools) == 1:
        score += 1
        breakdown["modern_data_stack"] = f"+1 ({governance_tools[0]})"

    # dbt specifically = highest governance signal
    if "dbt" in lead.tech_stack:
        score += 1
        breakdown["dbt_signal"] = "+1 (dbt users feel governance gaps acutely)"

    # Funding recency — budget unlocked
    if lead.months_since_funding <= 12:
        score += 2
        breakdown["recent_funding"] = f"+2 ({lead.funding_round}, {lead.months_since_funding}mo ago)"
    elif lead.months_since_funding <= 24:
        score += 1
        breakdown["recent_funding"] = f"+1 ({lead.funding_round}, {lead.months_since_funding}mo ago)"

    # Headcount sweet spot (50–500)
    if 50 <= lead.headcount <= 300:
        score += 1
        breakdown["headcount_fit"] = f"+1 ({lead.headcount} employees, sweet spot)"
    elif 300 < lead.headcount <= 500:
        score += 0
        breakdown["headcount_fit"] = f"0 ({lead.headcount} employees, upper range)"

    # Hiring data engineers = team scaling = governance needed
    if lead.hiring_data_engineers:
        score += 2
        breakdown["hiring_signal"] = "+2 (actively hiring data engineers)"

    # Persona tier
    title_lower = lead.title.lower()
    if any(t in title_lower for t in TIER_A_TITLES):
        score += 2
        breakdown["persona_tier"] = f"+2 (Tier A decision maker: {lead.title})"
    else:
        score += 1
        breakdown["persona_tier"] = f"+1 (Tier B influencer: {lead.title})"

    # Recent LinkedIn activity = warm signal
    if lead.recent_linkedin_post:
        score += 1
        breakdown["linkedin_active"] = "+1 (active on LinkedIn recently)"

    lead.icp_score = min(score, 10)  # cap at 10
    lead.score_breakdown = breakdown

    if lead.icp_score >= 7:
        lead.tier = "A"
    elif lead.icp_score >= 4:
        lead.tier = "B"
    else:
        lead.tier = "C"

    return lead

# ─────────────────────────────────────────────
# STAGE 4 — PERSONALIZATION
# ─────────────────────────────────────────────

def build_personalization_context(lead: EnrichedLead) -> str:
    """Builds a context string to feed the AI for personalization."""
    signals = []
    if lead.recent_linkedin_post:
        signals.append(f"Recent LinkedIn post: '{lead.recent_linkedin_post}'")
    if lead.hiring_data_engineers:
        signals.append(f"Currently hiring Data Engineers")
    if lead.months_since_funding <= 18:
        signals.append(f"Recently raised {lead.funding_round} (${lead.funding_amount_m}M, {lead.months_since_funding} months ago)")
    if "dbt" in lead.tech_stack:
        signals.append(f"Uses dbt in their data stack")
    if lead.tech_stack:
        signals.append(f"Tech stack: {', '.join(lead.tech_stack[:4])}")
    if lead.headcount_growth_pct > 20:
        signals.append(f"Company growing fast (+{lead.headcount_growth_pct}% headcount)")
    return "; ".join(signals) if signals else "No specific signals available"

def generate_personalization_rule_based(lead: EnrichedLead) -> tuple[str, str]:
    """
    Rule-based personalization (fallback when no API key).
    Produces genuinely signal-driven openers, not generic lines.
    """
    first = lead.first_name

    # Priority 1: LinkedIn post (highest relevance signal)
    if lead.recent_linkedin_post:
        post = lead.recent_linkedin_post
        if "governance" in post.lower():
            return (
                f"Saw your post on data governance at {lead.company} — that exact challenge (keeping governance in sync as the team scales) is what Northstar was built for.",
                f"your data governance post"
            )
        elif "dbt" in post.lower() or "snowflake" in post.lower() or "stack" in post.lower():
            return (
                f"Your post about the data stack migration at {lead.company} caught my attention — teams going through that transition are usually the first to feel governance gaps.",
                f"the {lead.company} data stack"
            )
        elif "hir" in post.lower():
            return (
                f"Saw you're scaling the data team at {lead.company} — that growth phase is usually when data quality incidents start compounding faster than the team can handle.",
                f"scaling data at {lead.company}"
            )
        else:
            return (
                f"Noticed your recent post about {lead.company}'s data work — the challenges you're describing are exactly the ones that tend to surface at your stage.",
                f"your post on {lead.company}"
            )

    # Priority 2: Hiring signal
    if lead.hiring_data_engineers:
        if lead.months_since_funding <= 18:
            return (
                f"You raised {lead.funding_round} {lead.months_since_funding} months ago and are now hiring Data Engineers — that's usually when data governance becomes urgent before it becomes painful.",
                f"scaling data at {lead.company} post-{lead.funding_round}"
            )
        return (
            f"Saw {lead.company} is hiring Data Engineers — teams that double their data function in under 12 months almost always hit the same data quality wall.",
            f"your data hiring at {lead.company}"
        )

    # Priority 3: Recent funding
    if lead.months_since_funding <= 12:
        return (
            f"Congrats on the {lead.funding_round} at {lead.company} — at that stage, data governance tends to move from 'nice to have' to 'blocker' faster than expected.",
            f"{lead.company}'s {lead.funding_round} and data infrastructure"
        )

    # Priority 4: dbt signal
    if "dbt" in lead.tech_stack:
        return (
            f"Noticed {lead.company} runs dbt — teams at that maturity level usually start feeling the gap between transformation logic and access control / lineage pretty quickly.",
            f"data governance for dbt teams"
        )

    # Priority 5: Modern stack
    if len([t for t in lead.tech_stack if t in GOVERNANCE_TECH]) >= 2:
        stack_str = " + ".join(lead.tech_stack[:2])
        return (
            f"Saw {lead.company} runs {stack_str} — that stack combination is usually where data teams start needing proper governance before the data catalog alone can cover it.",
            f"data governance for {stack_str} teams"
        )

    # Fallback: title-based
    return (
        f"As {lead.title} at {lead.company}, you're probably fielding increasing questions about data reliability as the company scales — that's exactly what Northstar addresses.",
        f"data governance at {lead.company}"
    )

def generate_personalization_ai(lead: EnrichedLead, api_key: str) -> tuple[str, str]:
    """
    AI-powered personalization via Claude API.
    Returns (personalization_line, email_subject).
    """
    context = build_personalization_context(lead)
    prompt = f"""You are a B2B cold email copywriter for Northstar, a data governance SaaS for European scale-ups.

Prospect: {lead.first_name} {lead.last_name}, {lead.title} at {lead.company}
Signals: {context}

Write:
1. A single opening sentence for a cold email (max 25 words). Must reference a SPECIFIC signal above. Do not mention "data governance" or "Northstar" by name. Sound human, not salesy.
2. A short email subject line (max 8 words). Must be specific to this prospect. No clickbait.

Respond ONLY with JSON in this exact format:
{{"opener": "...", "subject": "..."}}"""

    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["content"][0]["text"].strip()
            parsed = json.loads(text)
            return parsed.get("opener", ""), parsed.get("subject", "")
    except Exception as e:
        print(f"  ⚠️  AI call failed for {lead.first_name} {lead.last_name}: {e} — falling back to rule-based")
        return generate_personalization_rule_based(lead)

def personalize_lead(lead: EnrichedLead, api_key: Optional[str] = None) -> EnrichedLead:
    if api_key:
        opener, subject = generate_personalization_ai(lead, api_key)
        time.sleep(0.5)  # rate limit courtesy
    else:
        opener, subject = generate_personalization_rule_based(lead)

    lead.personalization_line = opener
    lead.email_subject = subject
    return lead

# ─────────────────────────────────────────────
# STAGE 5 — EXPORT
# ─────────────────────────────────────────────

EXPORT_COLUMNS = [
    "tier", "icp_score",
    "first_name", "last_name", "email", "title", "company", "company_domain", "linkedin_url",
    "funding_round", "funding_amount_m", "months_since_funding",
    "headcount", "headcount_growth_pct", "data_team_size",
    "tech_stack", "hiring_data_engineers", "recent_linkedin_post",
    "personalization_line", "email_subject",
    "score_breakdown",
]

def export_csv(leads: list[EnrichedLead], output_path: str):
    sorted_leads = sorted(leads, key=lambda l: (-l.icp_score, l.tier))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        for lead in sorted_leads:
            row = asdict(lead)
            row["tech_stack"] = ", ".join(row["tech_stack"])
            row["score_breakdown"] = json.dumps(row["score_breakdown"])
            writer.writerow({k: row[k] for k in EXPORT_COLUMNS})
    print(f"\n✅ Exported {len(leads)} enriched leads → {output_path}")

def print_summary(leads: list[EnrichedLead]):
    tier_a = [l for l in leads if l.tier == "A"]
    tier_b = [l for l in leads if l.tier == "B"]
    tier_c = [l for l in leads if l.tier == "C"]

    print("\n" + "═" * 60)
    print("  NORTHSTAR — ENRICHMENT PIPELINE RESULTS")
    print("═" * 60)
    print(f"  Total leads processed : {len(leads)}")
    print(f"  Tier A (score 7–10)   : {len(tier_a)} leads  ← priority outreach")
    print(f"  Tier B (score 4–6)    : {len(tier_b)} leads  ← semi-personalized")
    print(f"  Tier C (score 0–3)    : {len(tier_c)} leads  ← deprioritize")
    print("═" * 60)

    print("\n  TOP 5 LEADS:\n")
    top5 = sorted(leads, key=lambda l: -l.icp_score)[:5]
    for i, lead in enumerate(top5, 1):
        print(f"  {i}. [{lead.tier}] {lead.first_name} {lead.last_name} — {lead.title} @ {lead.company}")
        print(f"     Score: {lead.icp_score}/10 | Stack: {', '.join(lead.tech_stack[:3])}")
        print(f"     📧 Subject: {lead.email_subject}")
        print(f"     ✉️  Opener:  {lead.personalization_line}")
        if i < 5:
            print()
    print("\n" + "═" * 60)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Northstar Cold Outreach Lead Enrichment Pipeline")
    parser.add_argument("--input", help="Path to input CSV file (optional, uses sample data if omitted)")
    parser.add_argument("--output", default="enriched_leads.csv", help="Output CSV path")
    parser.add_argument("--api-key", help="Anthropic API key for AI personalization (optional)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        print("🤖 AI personalization: ENABLED (Claude API)")
    else:
        print("📐 AI personalization: rule-based (pass --api-key to enable AI)")

    print("\n── Stage 1: Loading prospects ──────────────────────────")
    prospects = load_prospects(args.input)

    print("\n── Stage 2: Enriching ──────────────────────────────────")
    leads = [enrich_prospect(p) for p in prospects]
    print(f"   Enriched {len(leads)} prospects")

    print("\n── Stage 3: Scoring ────────────────────────────────────")
    leads = [score_lead(l) for l in leads]
    print(f"   Scored {len(leads)} leads")

    print("\n── Stage 4: Personalizing ──────────────────────────────")
    for i, lead in enumerate(leads):
        print(f"   [{i+1}/{len(leads)}] {lead.first_name} {lead.last_name} @ {lead.company}...", end=" ")
        leads[i] = personalize_lead(lead, api_key)
        print("✓")

    print("\n── Stage 5: Exporting ──────────────────────────────────")
    export_csv(leads, args.output)
    print_summary(leads)

if __name__ == "__main__":
    main()
