import React, { useState, useMemo } from "react";

const LEADS = [
  { tier:"A", score:10, first:"Sophie",  last:"Martin",   title:"Head of Data",             company:"Pennylane",  domain:"pennylane.tech",  email:"sophie.martin@pennylane.tech",  tech:["dbt","Snowflake","Fivetran","Looker"],   funding:"Series C", amount:57,  months:8,  hc:600,  hcg:40, de_hiring:true,  post:"Just wrapped migrating our entire data stack to dbt + Snowflake. Lessons learned incoming 🧵", opener:"Your post about the data stack migration at Pennylane caught my attention — teams going through that transition are usually the first to feel governance gaps.", subject:"the Pennylane data stack", breakdown:{"modern_data_stack":"+2 (dbt, Snowflake, Fivetran)","dbt_signal":"+1","recent_funding":"+2 (Series C, 8mo ago)","hiring_signal":"+2","persona_tier":"+2 (Head of Data)","linkedin_active":"+1"}},
  { tier:"A", score:10, first:"Antoine", last:"Bernard",  title:"Head of Data",             company:"Qonto",      domain:"qonto.com",       email:"antoine.bernard@qonto.com",     tech:["dbt","Snowflake","Airbyte","Metabase"], funding:"Series D", amount:486, months:12, hc:1200, hcg:30, de_hiring:true,  post:"Just posted: looking for a Data Governance Lead — first of its kind at Qonto", opener:"Saw your post on data governance at Qonto — that exact challenge is what Northstar was built for.", subject:"your data governance post", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+2 (Series D, 12mo ago)","hiring_signal":"+2","persona_tier":"+2","linkedin_active":"+1"}},
  { tier:"A", score:10, first:"Pablo",   last:"Garcia",   title:"VP Data",                  company:"Holded",     domain:"holded.com",      email:"pablo.garcia@holded.com",       tech:["BigQuery","dbt","Looker"],              funding:"Series B", amount:18,  months:9,  hc:200,  hcg:28, de_hiring:true,  post:"Building our data platform from scratch after Series B — exciting and chaotic", opener:"Building a data platform post-Series B is exciting until data quality incidents start compounding faster than the team can handle.", subject:"scaling Holded's data platform", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+2","headcount_fit":"+1","hiring_signal":"+2","persona_tier":"+2"}},
  { tier:"A", score:10, first:"Sophia",  last:"Andersen", title:"Chief Data Officer",       company:"Pleo",       domain:"pleo.io",         email:"sophia.andersen@pleo.io",       tech:["Snowflake","dbt","Airbyte"],            funding:"Series C", amount:150, months:11, hc:450,  hcg:22, de_hiring:true,  post:"Our Head of Data just wrote a great post on why we're investing in data contracts", opener:"Loved Pleo's post on data contracts — teams investing there are usually the first to need solid governance underneath it.", subject:"data contracts at Pleo", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+2","headcount_fit":"+1","hiring_signal":"+2","persona_tier":"+2"}},
  { tier:"A", score:10, first:"Laura",   last:"Bianchi",  title:"Head of Data",             company:"Musixmatch", domain:"musixmatch.com",  email:"laura.bianchi@musixmatch.com",  tech:["BigQuery","dbt","Metabase"],            funding:"Series B", amount:9,   months:5,  hc:120,  hcg:20, de_hiring:true,  post:"Building our first proper data platform — dbt is a game changer", opener:"Your post on dbt at Musixmatch resonated — the teams that go from 0 to dbt fastest are also the first to hit governance blind spots.", subject:"dbt governance at Musixmatch", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+2","headcount_fit":"+1","hiring_signal":"+2","persona_tier":"+2"}},
  { tier:"A", score:9,  first:"Clara",   last:"Rossi",    title:"Data Platform Lead",       company:"Satispay",   domain:"satispay.com",    email:"clara.rossi@satispay.com",      tech:["BigQuery","Looker","dbt"],              funding:"Series C", amount:320, months:10, hc:350,  hcg:35, de_hiring:true,  post:"Our data team just doubled — now figuring out how to keep data consistent across 5 product lines", opener:"Doubling a data team across 5 product lines is exactly when inconsistencies compound — saw your post on that challenge.", subject:"data consistency at Satispay", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+2","hiring_signal":"+2","persona_tier":"+1","linkedin_active":"+1"}},
  { tier:"A", score:9,  first:"Lucas",   last:"Müller",   title:"Data Engineering Manager", company:"Spendesk",   domain:"spendesk.com",    email:"lucas.muller@spendesk.com",     tech:["dbt","BigQuery","Airbyte"],             funding:"Series C", amount:100, months:14, hc:500,  hcg:25, de_hiring:true,  post:"Hiring two Data Engineers to scale our analytics infra — DM if interested", opener:"Saw you're hiring two Data Engineers at Spendesk — teams that double data capacity in under a year almost always hit the same data quality wall.", subject:"scaling data at Spendesk", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+1","hiring_signal":"+2","persona_tier":"+2","linkedin_active":"+1"}},
  { tier:"A", score:9,  first:"Carlos",  last:"López",    title:"Data Platform Manager",    company:"Factorial",  domain:"factorialhr.com", email:"carlos.lopez@factorialhr.com",  tech:["Snowflake","Fivetran","Metabase"],      funding:"Series C", amount:80,  months:7,  hc:300,  hcg:32, de_hiring:true,  post:"Scaling fast after Series C — data quality becoming a board-level concern", opener:"Data quality becoming a board concern post Series C is almost universal — and it usually means the governance layer hasn't caught up yet.", subject:"data quality at Factorial", breakdown:{"modern_data_stack":"+1","recent_funding":"+2","headcount_fit":"+1","hiring_signal":"+2","persona_tier":"+1","linkedin_active":"+1"}},
  { tier:"A", score:8,  first:"Emma",    last:"Dubois",   title:"VP Analytics",             company:"Alan",       domain:"alan.com",        email:"emma.dubois@alan.com",          tech:["Snowflake","dbt","Tableau"],            funding:"Series E", amount:183, months:6,  hc:550,  hcg:20, de_hiring:false, post:"Data quality is becoming our #1 priority as we scale across 3 countries", opener:"Scaling data quality across 3 countries is a genuinely hard governance problem — saw your post and it resonated.", subject:"data quality across Alan's markets", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+2","persona_tier":"+2","linkedin_active":"+1"}},
  { tier:"A", score:8,  first:"Markus",  last:"Weber",    title:"Analytics Engineering Lead","company":"Personio", domain:"personio.com",    email:"markus.weber@personio.com",     tech:["dbt","BigQuery","Looker","Airflow"],    funding:"Series E", amount:200, months:20, hc:2000, hcg:15, de_hiring:true,  post:"Analytics engineering is the fastest-growing function at Personio right now", opener:"Analytics engineering growing fastest at Personio makes sense — that's also when the gap between transformation logic and data contracts starts to show.", subject:"analytics engineering at Personio", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","hiring_signal":"+2","persona_tier":"+1","linkedin_active":"+1"}},
  { tier:"A", score:8,  first:"Jan",     last:"Van Berg", title:"Head of Data Engineering", company:"Mollie",     domain:"mollie.com",      email:"jan.vanberg@mollie.com",        tech:["Databricks","dbt","Looker"],            funding:"Series C", amount:665, months:18, hc:800,  hcg:15, de_hiring:true,  post:"", opener:"Mollie runs Databricks + dbt at scale — that combination is where governance gaps tend to emerge earliest.", subject:"data governance for Databricks + dbt", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","recent_funding":"+1","hiring_signal":"+2","persona_tier":"+2"}},
  { tier:"A", score:7,  first:"Marie",   last:"Leclerc",  title:"CDO",                      company:"Doctolib",   domain:"doctolib.fr",     email:"marie.leclerc@doctolib.fr",     tech:["Redshift","Airflow","Tableau"],         funding:"Series D", amount:500, months:30, hc:3000, hcg:10, de_hiring:false, post:"Scaling data governance in healthcare is a unique challenge", opener:"Healthcare data governance is a uniquely constrained problem — regulatory pressure compounds everything. Would love to show you how Northstar addresses that.", subject:"healthcare data governance", breakdown:{"recent_funding":"+1","persona_tier":"+2","linkedin_active":"+1"}},
  { tier:"B", score:6,  first:"Sophia",  last:"Andersen", title:"Head of BI",               company:"Payfit",     domain:"payfit.com",      email:"romain.petit@payfit.com",       tech:["BigQuery","Fivetran","Looker"],         funding:"Series D", amount:90,  months:16, hc:700,  hcg:12, de_hiring:false, post:"BI stack migration in progress — moving off legacy Tableau", opener:"Mid-migration off Tableau is one of the messiest data governance moments — data definitions drift before anyone notices.", subject:"Payfit's BI migration", breakdown:{"modern_data_stack":"+1","recent_funding":"+1","persona_tier":"+2","linkedin_active":"+1"}},
  { tier:"B", score:6,  first:"Thomas",  last:"Schmidt",  title:"Analytics Lead",           company:"N26",        domain:"n26.com",         email:"thomas.schmidt@n26.com",        tech:["Snowflake","dbt","Fivetran","Metabase"],"funding":"Series E", amount:900, months:24, hc:1500, hcg:5,  de_hiring:true,  post:"", opener:"N26 runs a mature dbt + Snowflake stack — at that scale, lineage and access control tend to be the next frontier.", subject:"data governance at N26 scale", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","hiring_signal":"+2","persona_tier":"+1"}},
  { tier:"B", score:5,  first:"Ingrid",  last:"Svensson", title:"Data Engineering Manager", company:"Klarna",     domain:"klarna.com",      email:"ingrid.svensson@klarna.com",    tech:["Databricks","dbt","Snowflake","Airflow"],"funding":"IPO",    amount:0,   months:99, hc:5000, hcg:0,  de_hiring:false, post:"", opener:"Klarna's scale with Databricks + dbt is impressive — enterprise-grade governance at that breadth is a genuinely interesting problem.", subject:"data governance at Klarna", breakdown:{"modern_data_stack":"+2","dbt_signal":"+1","persona_tier":"+2"}},
  { tier:"B", score:5,  first:"Anna",    last:"Kowalski", title:"VP Data & Analytics",      company:"Brainly",    domain:"brainly.com",     email:"anna.kowalski@brainly.com",     tech:["Redshift","Airflow","Tableau"],         funding:"Series F", amount:80,  months:40, hc:900,  hcg:5,  de_hiring:false, post:"", opener:"VP Data at Brainly's scale — you're probably navigating the tension between data democratization and access control.", subject:"data governance at Brainly", breakdown:{"persona_tier":"+2"}},
  { tier:"B", score:5,  first:"Julie",   last:"Moreau",   title:"Head of Data",             company:"Swile",      domain:"swile.co",        email:"julie.moreau@swile.co",         tech:["BigQuery","dbt"],                       funding:"Series C", amount:200, months:15, hc:400,  hcg:18, de_hiring:false, post:"", opener:"Swile runs BigQuery + dbt — that's usually when data teams start needing a governance layer to match the stack maturity.", subject:"data governance for dbt teams", breakdown:{"modern_data_stack":"+1","dbt_signal":"+1","recent_funding":"+1","headcount_fit":"+1","persona_tier":"+1"}},
  { tier:"C", score:3,  first:"Lena",    last:"Fischer",  title:"Senior Data Engineer",     company:"Gorillas",   domain:"gorillas.io",     email:"lena.fischer@gorillas.io",      tech:["MySQL","Redash"],                       funding:"Series C", amount:290, months:36, hc:800,  hcg:-10,de_hiring:false, post:"", opener:"", subject:"", breakdown:{"persona_tier":"+1"}},
  { tier:"C", score:2,  first:"Henrik",  last:"Nielsen",  title:"Analytics Manager",        company:"Vivino",     domain:"vivino.com",      email:"henrik.nielsen@vivino.com",     tech:["Snowflake","Looker"],                   funding:"Series D", amount:155, months:22, hc:250,  hcg:8,  de_hiring:false, post:"", opener:"", subject:"", breakdown:{"modern_data_stack":"+1","headcount_fit":"+1"}},
  { tier:"C", score:2,  first:"Pierre",  last:"Durand",   title:"Head of Data Engineering", company:"Deezer",     domain:"deezer.com",      email:"pierre.durand@deezer.com",      tech:["BigQuery","dbt","Looker"],              funding:"IPO",      amount:0,   months:99, hc:800,  hcg:0,  de_hiring:false, post:"", opener:"", subject:"", breakdown:{"modern_data_stack":"+1","dbt_signal":"+1"}},
];

const TECH_COLORS = {
  dbt: "#FF694B", Snowflake: "#29B5E8", BigQuery: "#4285F4", Databricks: "#FF3621",
  Fivetran: "#0073FF", Airbyte: "#615EFF", Looker: "#4285F4", Metabase: "#509EE3",
  Airflow: "#017CEE", Tableau: "#E97627", Redshift: "#8C4FFF", Redash: "#888",
};

const TIER_CONFIG = {
  A: { bg: "bg-emerald-950", border: "border-emerald-500", badge: "bg-emerald-500", text: "Tier A", label: "Priority outreach" },
  B: { bg: "bg-amber-950", border: "border-amber-500", badge: "bg-amber-500", text: "Tier B", label: "Semi-personalized" },
  C: { bg: "bg-zinc-900", border: "border-zinc-600", badge: "bg-zinc-500", text: "Tier C", label: "Deprioritize" },
};

function ScoreBar({ score }) {
  const pct = (score / 10) * 100;
  const color = score >= 7 ? "#10b981" : score >= 4 ? "#f59e0b" : "#71717a";
  return (
    <div className="flex items-center gap-2 mt-1">
      <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        <div style={{ width: `${pct}%`, backgroundColor: color }} className="h-full rounded-full transition-all" />
      </div>
      <span style={{ color }} className="text-xs font-bold tabular-nums w-8 text-right">{score}/10</span>
    </div>
  );
}

function TechBadge({ tech }) {
  const color = TECH_COLORS[tech] || "#888";
  return (
    <span style={{ backgroundColor: color + "22", color, border: `1px solid ${color}44` }}
      className="text-[10px] px-1.5 py-0.5 rounded font-mono font-medium">
      {tech}
    </span>
  );
}

function LeadCard({ lead, onClick, selected }) {
  const cfg = TIER_CONFIG[lead.tier];
  return (
    <div onClick={() => onClick(lead)}
      className={`cursor-pointer rounded-lg border p-3 transition-all hover:scale-[1.01] ${cfg.border} ${selected ? cfg.bg : "bg-zinc-900 hover:bg-zinc-800"}`}
      style={{ boxShadow: selected ? `0 0 0 2px ${lead.tier === "A" ? "#10b981" : lead.tier === "B" ? "#f59e0b" : "#71717a"}40` : "none" }}>
      <div className="flex items-start justify-between gap-2 mb-1">
        <div className="min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold text-white ${cfg.badge}`}>{cfg.text}</span>
            <span className="font-semibold text-white text-sm truncate">{lead.first} {lead.last}</span>
          </div>
          <div className="text-zinc-400 text-xs truncate">{lead.title}</div>
          <div className="text-zinc-300 text-xs font-medium">{lead.company}</div>
        </div>
      </div>
      <ScoreBar score={lead.score} />
      <div className="flex flex-wrap gap-1 mt-2">
        {lead.tech.slice(0, 3).map(t => <TechBadge key={t} tech={t} />)}
        {lead.tech.length > 3 && <span className="text-[10px] text-zinc-500">+{lead.tech.length - 3}</span>}
      </div>
    </div>
  );
}

function DetailPanel({ lead, onClose }) {
  if (!lead) return (
    <div className="flex items-center justify-center h-full text-zinc-600 text-sm">
      <div className="text-center">
        <div className="text-4xl mb-3">←</div>
        <div>Select a lead to see details</div>
      </div>
    </div>
  );

  const cfg = TIER_CONFIG[lead.tier];
  return (
    <div className="h-full overflow-y-auto p-5 space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-0.5">
            <span className={`text-xs px-2 py-0.5 rounded font-bold text-white ${cfg.badge}`}>{cfg.text} — {cfg.label}</span>
          </div>
          <h2 className="text-xl font-bold text-white">{lead.first} {lead.last}</h2>
          <div className="text-zinc-400 text-sm">{lead.title} · {lead.company}</div>
          <div className="text-zinc-500 text-xs mt-0.5">{lead.email}</div>
        </div>
        <button onClick={onClose} className="text-zinc-500 hover:text-white text-lg leading-none mt-1">✕</button>
      </div>

      <div>
        <div className="text-zinc-400 text-xs uppercase tracking-widest mb-2 font-semibold">ICP Score</div>
        <ScoreBar score={lead.score} />
        <div className="mt-2 space-y-1">
          {Object.entries(lead.breakdown).map(([k, v]) => (
            <div key={k} className="flex items-start gap-2 text-xs">
              <span className="text-emerald-400 font-mono flex-shrink-0">{v.startsWith("+") ? "✓" : "·"}</span>
              <span className="text-zinc-400">{v}</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <div className="text-zinc-400 text-xs uppercase tracking-widest mb-2 font-semibold">Enrichment Signals</div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            ["Funding", `${lead.funding}${lead.amount ? ` ($${lead.amount}M)` : ""}`],
            ["Raised", lead.months < 99 ? `${lead.months}mo ago` : "—"],
            ["Headcount", `${lead.hc.toLocaleString()} (${lead.hcg > 0 ? "+" : ""}${lead.hcg}%)`],
            ["Data Team", `${lead.de_hiring ? "🔥 Hiring DEs" : `${lead.domain}`}`],
          ].map(([k, v]) => (
            <div key={k} className="bg-zinc-800 rounded p-2">
              <div className="text-zinc-500 mb-0.5">{k}</div>
              <div className="text-white font-medium">{v}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <div className="text-zinc-400 text-xs uppercase tracking-widest mb-2 font-semibold">Tech Stack</div>
        <div className="flex flex-wrap gap-1.5">
          {lead.tech.map(t => <TechBadge key={t} tech={t} />)}
        </div>
      </div>

      {lead.post && (
        <div>
          <div className="text-zinc-400 text-xs uppercase tracking-widest mb-2 font-semibold">Recent LinkedIn Signal</div>
          <div className="bg-zinc-800 border border-zinc-700 rounded p-3 text-sm text-zinc-300 italic">
            "{lead.post}"
          </div>
        </div>
      )}

      {lead.opener && (
        <div>
          <div className="text-zinc-400 text-xs uppercase tracking-widest mb-2 font-semibold">Generated Email</div>
          <div className="bg-zinc-800 border border-emerald-900 rounded p-3 space-y-2">
            <div>
              <span className="text-zinc-500 text-xs">Subject: </span>
              <span className="text-emerald-300 text-sm font-medium">{lead.subject}</span>
            </div>
            <div className="border-t border-zinc-700 pt-2">
              <span className="text-zinc-500 text-xs">Opening line:</span>
              <p className="text-zinc-200 text-sm mt-1 leading-relaxed">{lead.opener}</p>
            </div>
          </div>
        </div>
      )}

      {!lead.opener && lead.tier === "C" && (
        <div className="bg-zinc-800 border border-zinc-700 rounded p-3 text-sm text-zinc-500 text-center">
          Tier C — deprioritized. No personalization generated.
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [selected, setSelected] = useState(LEADS[0]);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");

  const tierCounts = useMemo(() => ({
    A: LEADS.filter(l => l.tier === "A").length,
    B: LEADS.filter(l => l.tier === "B").length,
    C: LEADS.filter(l => l.tier === "C").length,
  }), []);

  const filtered = useMemo(() => {
    return LEADS.filter(l => {
      if (filter !== "All" && l.tier !== filter) return false;
      if (search) {
        const q = search.toLowerCase();
        return l.first.toLowerCase().includes(q) || l.last.toLowerCase().includes(q) ||
          l.company.toLowerCase().includes(q) || l.title.toLowerCase().includes(q) ||
          l.tech.some(t => t.toLowerCase().includes(q));
      }
      return true;
    });
  }, [filter, search]);

  return (
    <div style={{ fontFamily: "'DM Mono', 'Courier New', monospace", backgroundColor: "#0a0a0a", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@700;800&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #111; } ::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
        .stat-card { background: linear-gradient(135deg, #111 0%, #0d0d0d 100%); }
      `}</style>

      {/* Header */}
      <div style={{ borderBottom: "1px solid #1f1f1f", background: "linear-gradient(180deg, #0f0f0f 0%, #0a0a0a 100%)" }}
        className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div style={{ background: "linear-gradient(135deg, #10b981, #059669)", width: 32, height: 32, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ color: "white", fontSize: 16 }}>★</span>
          </div>
          <div>
            <div style={{ fontFamily: "'Syne', sans-serif", color: "white", fontSize: 16, fontWeight: 800, letterSpacing: "-0.02em" }}>
              NORTHSTAR
            </div>
            <div style={{ color: "#52525b", fontSize: 10, letterSpacing: "0.15em" }}>OUTREACH PIPELINE</div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div style={{ color: "#52525b", fontSize: 11 }}>
            {LEADS.length} leads · {tierCounts.A} priority
          </div>
          <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "#10b981", boxShadow: "0 0 6px #10b981" }} />
        </div>
      </div>

      {/* Stats */}
      <div className="px-6 py-4 grid grid-cols-4 gap-3">
        {[
          { label: "Total Leads", value: LEADS.length, sub: "enriched & scored", color: "#e4e4e7" },
          { label: "Tier A", value: tierCounts.A, sub: "priority outreach", color: "#10b981" },
          { label: "Tier B", value: tierCounts.B, sub: "semi-personalized", color: "#f59e0b" },
          { label: "Tier C", value: tierCounts.C, sub: "deprioritized", color: "#71717a" },
        ].map(s => (
          <div key={s.label} className="stat-card rounded-lg p-3" style={{ border: "1px solid #1f1f1f" }}>
            <div style={{ color: s.color, fontSize: 24, fontWeight: 700, lineHeight: 1 }}>{s.value}</div>
            <div style={{ color: "#e4e4e7", fontSize: 12, marginTop: 2 }}>{s.label}</div>
            <div style={{ color: "#52525b", fontSize: 10 }}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Main */}
      <div className="flex" style={{ height: "calc(100vh - 160px)" }}>
        {/* Left Panel */}
        <div style={{ width: 340, borderRight: "1px solid #1f1f1f", flexShrink: 0, display: "flex", flexDirection: "column" }}>
          <div className="px-3 py-2 space-y-2" style={{ borderBottom: "1px solid #1f1f1f" }}>
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search leads, companies, tech..."
              style={{ width: "100%", background: "#111", border: "1px solid #2a2a2a", borderRadius: 6, padding: "6px 10px", color: "#e4e4e7", fontSize: 12, outline: "none" }}
            />
            <div className="flex gap-1">
              {["All", "A", "B", "C"].map(t => (
                <button key={t} onClick={() => setFilter(t)}
                  style={{
                    flex: 1, padding: "4px 0", borderRadius: 5, fontSize: 11, fontWeight: 600, cursor: "pointer",
                    border: filter === t ? "1px solid #10b981" : "1px solid #2a2a2a",
                    background: filter === t ? "#10b98122" : "#111",
                    color: filter === t ? "#10b981" : "#71717a"
                  }}>
                  {t === "All" ? `All (${LEADS.length})` : `${TIER_CONFIG[t].text} (${tierCounts[t]})`}
                </button>
              ))}
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {filtered.map(lead => (
              <LeadCard key={lead.email} lead={lead}
                selected={selected?.email === lead.email}
                onClick={setSelected} />
            ))}
            {filtered.length === 0 && (
              <div className="text-center text-zinc-600 text-sm py-8">No leads match your filter</div>
            )}
          </div>
        </div>

        {/* Right Panel */}
        <div className="flex-1 overflow-hidden">
          <DetailPanel lead={selected} onClose={() => setSelected(null)} />
        </div>
      </div>
    </div>
  );
}
