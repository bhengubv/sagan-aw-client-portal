// Technical Specification generator — AW Client Report Portal
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, TabStopType, TabStopPosition,
  TableOfContents, HeadingLevel, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageNumber, PageBreak
} = require("docx");

// ---------- palette ----------
const NAVY = "1F3864", BLUE = "2E5E8C", HDRFILL = "1F4E79", ZEBRA = "F2F6FA";
const GREY = "595959", LIGHT = "CCCCCC", GREEN = "2E7D32", AMBER = "B26A00", RED = "B22222";
const CW = 9360; // content width, US Letter 1" margins

// ---------- helpers ----------
const T = (text, o = {}) => new TextRun({ text, ...o });
const run = (text, o = {}) => new TextRun({ text, ...o });
function P(content, o = {}) {
  const children = Array.isArray(content) ? content : [new TextRun(String(content))];
  return new Paragraph({ children, spacing: { after: 120, line: 276 }, ...o });
}
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [T(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [T(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [T(t)] });
function bullet(content, level = 0) {
  const children = Array.isArray(content) ? content : [new TextRun(String(content))];
  return new Paragraph({ numbering: { reference: "bullets", level }, spacing: { after: 60, line: 276 }, children });
}
function numItem(content) {
  const children = Array.isArray(content) ? content : [new TextRun(String(content))];
  return new Paragraph({ numbering: { reference: "nums", level: 0 }, spacing: { after: 60, line: 276 }, children });
}
const spacer = (n = 1) => new Paragraph({ children: [T("")], spacing: { after: 40 * n } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

function cell(content, w, opt = {}) {
  let runs;
  if (Array.isArray(content)) runs = content;
  else runs = [new TextRun({ text: String(content), bold: !!opt.bold, color: opt.color, size: opt.size })];
  const border = { style: BorderStyle.SINGLE, size: 1, color: LIGHT };
  return new TableCell({
    borders: { top: border, bottom: border, left: border, right: border },
    width: { size: w, type: WidthType.DXA },
    shading: opt.fill ? { fill: opt.fill, type: ShadingType.CLEAR } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    verticalAlign: VerticalAlign.CENTER,
    columnSpan: opt.span,
    children: (Array.isArray(opt.paras) ? opt.paras : [new Paragraph({ alignment: opt.align, spacing: { after: 0, line: 264 }, children: runs })]),
  });
}
// rows: array of arrays; each entry string | {t, bold, fill, color, align, paras, runs}
function table(colWidths, headers, rows) {
  const total = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => cell(h, colWidths[i], { fill: HDRFILL, bold: true, color: "FFFFFF" })),
  });
  const body = rows.map((r, ri) =>
    new TableRow({
      children: r.map((c, i) => {
        const zebra = ri % 2 === 1 ? ZEBRA : undefined;
        if (c && typeof c === "object" && !Array.isArray(c)) {
          const content = c.runs ? c.runs : (c.t !== undefined ? c.t : "");
          return cell(content, colWidths[i], { fill: c.fill || zebra, bold: c.bold, color: c.color, align: c.align, paras: c.paras, span: c.span });
        }
        return cell(c, colWidths[i], { fill: zebra });
      }),
    })
  );
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: colWidths, rows: [headerRow, ...body] });
}
// callout-style single-cell box
function callout(label, content, fill = "FFF8E1", barColor = AMBER) {
  const runs = [new TextRun({ text: label + "  ", bold: true, color: barColor }), ...(Array.isArray(content) ? content : [new TextRun(String(content))])];
  const border = { style: BorderStyle.SINGLE, size: 1, color: LIGHT };
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: [CW],
    rows: [new TableRow({ children: [new TableCell({
      borders: { top: border, bottom: border, right: border, left: { style: BorderStyle.SINGLE, size: 18, color: barColor } },
      shading: { fill, type: ShadingType.CLEAR },
      margins: { top: 100, bottom: 100, left: 160, right: 140 },
      children: [new Paragraph({ spacing: { after: 0, line: 276 }, children: runs })],
    })] })],
  });
}

const body = [];
const A = (...x) => body.push(...x);

// ============================================================ TITLE PAGE
A(
  new Paragraph({ spacing: { before: 1400, after: 0 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: BLUE, space: 8 } }, children: [
    new TextRun({ text: "TECHNICAL SPECIFICATION", bold: true, size: 56, color: NAVY }),
  ]}),
  new Paragraph({ spacing: { before: 200, after: 0 }, children: [ new TextRun({ text: "AW Client Report Portal", bold: true, size: 40, color: BLUE }) ]}),
  new Paragraph({ spacing: { before: 60, after: 600 }, children: [ new TextRun({ text: "Automated SACS (Cash-Flow) & TCC (Net-Worth) Reporting Platform", size: 26, color: GREY, italics: true }) ]}),
);
A(table([2600, 6760],
  ["Field", "Value"],
  [
    ["Document type", "Technical Specification — for executive evaluation & authorisation"],
    ["Product / project", "AW Client Report Portal (working name; traceable to PRD v1.0)"],
    ["Specification version", { t: "v1.0 (Draft for approval)", bold: true }],
    ["Date", "18 June 2026"],
    ["Prepared by", "Engineering (AI Practice)"],
    ["Prepared for", "Product Owner / Product Manager and Executive Sponsors"],
    ["Status", { t: "AWAITING AUTHORISATION", bold: true, color: AMBER }],
    ["Classification", { t: "CONFIDENTIAL — contains client & financial process detail", color: RED }],
    ["Source basis", "PRD v1.0 (2026-04-09) + discovery-call recording (2026-04-01) and a prior call"],
  ]
));
A(spacer(2));
A(callout("PURPOSE.",
  "This document translates the approved PRD into an engineering design and a phased delivery plan. It specifies the full target system — the immediately-authorised V1 build and the later phases that will be productised and released more broadly — so decision-makers can authorise V1 with full sight of where it leads. Sign-off page: Section 20.",
  "E8F1FA", BLUE));
A(pageBreak());

// ============================================================ DOC CONTROL
A(H1("Document Control"));
A(H2("Revision History"));
A(table([1400, 1700, 2600, 3660],
  ["Version", "Date", "Author", "Summary of change"],
  [
    ["0.1", "16 Jun 2026", "Engineering", "Initial structure from PRD"],
    ["0.9", "17 Jun 2026", "Engineering", "Full architecture, phasing, security sections"],
    [{ t: "1.0", bold: true }, "18 Jun 2026", "Engineering", { t: "Draft issued for executive evaluation & PM/Owner authorisation", bold: true }],
  ]
));
A(H2("Distribution List"));
A(table([3120, 3120, 3120],
  ["Name / Role", "Function", "Reason"],
  [
    ["Product Owner / PM", "Approval authority", "Authorise scope & phasing"],
    ["Executive Sponsor(s)", "Funding / strategy", "Evaluate value & commercial model"],
    ["Engineering Lead", "Delivery", "Confirm feasibility & estimates"],
    ["Compliance / Security", "Risk", "Confirm data-handling posture"],
    ["Client stakeholders", "Andrew, Rebecca, Maryann", "Validate business rules"],
  ]
));
A(H2("Approvals Required"));
A(P([T("This specification is not in force until the Authorisation block in ", {}), T("Section 20", { bold: true }), T(" is signed by the Product Owner / Owner. Executive sponsors evaluate; the Product Owner authorises.", {})]));
A(pageBreak());

// ============================================================ TOC
A(H1("Table of Contents"));
A(new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }));
A(P([T("If the contents above appear empty, open in Word and choose ", {}), T("Update Field", { italics: true }), T(" (the document is configured to refresh on open).", {})], { spacing: { before: 120 } }));
A(pageBreak());

// ============================================================ 1. EXEC SUMMARY
A(H1("1. Executive Summary"));
A(P("The firm produces two client-facing financial reports each quarter — a cash-flow summary (SACS) and a net-worth overview (TCC) — by manually gathering balances from several systems and assembling them in Canva and Word. The process takes roughly one full day per client meeting and is error-prone. This specification defines a secure web portal that reduces that preparation from a day to under an hour, eliminates manual arithmetic, and produces consistent, presentation-quality PDFs."));
A(H2("1.1 The recommendation"));
A(P([T("Authorise ", {}), T("Phase 1 (V1)", { bold: true }), T(" now: a single-firm portal for client setup, guided quarterly data entry, a deterministic calculation engine, and pixel-stable SACS & TCC PDF generation with export. V1 deliberately uses ", {}), T("no external integrations and no AI", { bold: true }), T(" — all data is entered by the team — which keeps it low-risk, fast, and fully within compliance constraints.", {})]));
A(H2("1.2 The forward vision (designed now, released later)"));
A(P("Per direction, this document also fully designs the later phases so the architecture chosen for V1 deliberately enables them with no rework: automated data integration (Phase 2), an AI agent layer for onboarding and data extraction (Phase 3), and a multi-tenant, productised release to other advisory firms (Phase 4). These are specified but not authorised by this document; each is its own funding decision. Designing them now means V1 is built multi-tenant-ready and integration-ready from day one."));
A(H2("1.3 What executives are being asked to decide"));
A(numItem([T("Authorise the V1 build", { bold: true }), T(" and its acceptance criteria (Sections 8–9, 18).", {})]));
A(numItem([T("Note and steer the phased roadmap", { bold: true }), T(" (Section 4 & 15) — including the intent to productise later phases for public release.", {})]));
A(numItem([T("Resolve the open decisions", { bold: true }), T(" in Section 19 (e.g., Canva export priority, report storage, hosting region).", {})]));
A(numItem([T("Accept the security & compliance posture", { bold: true }), T(" in Section 13.", {})]));
A(H2("1.4 Headline figures"));
A(table([3120, 3120, 3120],
  ["Metric", "Today", "With the portal"],
  [
    ["Prep time / client / quarter", "~1 day", "< 1 hour (target)"],
    ["Manual math", "All totals by hand", "Fully automated"],
    ["Report consistency", "Canva drift / misalignment", "Fixed, pixel-stable layout"],
    ["Scale ceiling (no new hires)", "~6 clients", "12+ clients (V1); unbounded (Phase 4)"],
    ["External data risk (V1)", "n/a", "None — manual entry only"],
  ]
));
A(pageBreak());

// ============================================================ 2. BACKGROUND
A(H1("2. Background & Context"));
A(H2("2.1 The client and the problem"));
A(P("A lean, three-person financial-planning firm (principal Andrew; planner Rebecca, who holds Schwab access and compliance responsibility; and executive assistant Maryann) serves roughly six high- and ultra-high-net-worth households on retainer, with quarterly review meetings plus assets under management. Clients expect high professionalism and accuracy."));
A(P([T("For every quarterly meeting the team hand-builds two reports, pulling data from ", {}), T("Pinnacle Bank, Charles Schwab, RightCapital and Zillow", { bold: true }), T(", then assembling the figures in Canva and Word. The work is slow, repetitive, and a recurring source of arithmetic and alignment errors.", {})]));
A(H2("2.2 How this specification was derived"));
A(P("This document is the engineering response to an approved PRD (v1.0, 2026-04-09), which was itself synthesised from a recorded requirements call (2026-04-01) and a prior call. Requirements below are traceable to those sources; a traceability matrix is provided in Appendix C. Where the PRD recorded ambiguity, it is surfaced here as an open decision or an assumption to confirm rather than silently resolved."));
A(callout("ASSUMPTION TO CONFIRM.",
  "Certain identifiers in the PRD (the firm name, legal entity, and city) were attributed to third-party web research and were not stated on the call. They are treated here as unverified placeholders and must be confirmed before any client-facing or contractual use. See Section 17.2.",
  "FFF8E1", AMBER));
A(pageBreak());

// ============================================================ 3. GOALS
A(H1("3. Goals, Non-Goals & Success Metrics"));
A(H2("3.1 Business goals"));
A(bullet("Cut quarterly report preparation from ~1 day to under 1 hour per client."));
A(bullet("Eliminate manual calculation errors through a single deterministic engine."));
A(bullet("Produce consistent, branded, presentation-quality PDFs with a fixed layout."));
A(bullet("Enable the firm to grow its client base without adding headcount."));
A(bullet("Consolidate scattered data (Excel, Dropbox, PreciseFP) into one source of truth."));
A(H2("3.2 Technical goals"));
A(bullet("Deterministic, auditable calculations — no AI in the V1 numeric path."));
A(bullet("Pixel-stable PDF rendering independent of value length or account count."));
A(bullet("An architecture that admits later integrations and multi-tenancy without rework."));
A(bullet("Strong protection of PII and financial data, by design."));
A(H2("3.3 Non-goals (for V1)"));
A(bullet("No automated pulling from RightCapital, Schwab, Pinnacle, or Zillow (Phase 2)."));
A(bullet("No AI reasoning, classification, or generation in the report path (Phase 3)."));
A(bullet("No client-facing access; the portal is internal-only in V1 (Phase 3/4)."));
A(bullet("No redesign of Andrew's report templates — visual parity only, with light polish."));
A(H2("3.4 Success metrics (KPIs)"));
A(table([3700, 2830, 2830],
  ["KPI", "Baseline", "Target (90 days post-launch)"],
  [
    ["Median prep time / report", "~1 day", "< 60 min"],
    ["Calculation errors / quarter", "Recurring", "0"],
    ["Reports generated via portal", "0%", "100% of quarterly reports"],
    ["Re-work due to layout drift", "Frequent", "Eliminated"],
    ["Clients served per staff member", "~2", "≥ 4"],
  ]
));
A(pageBreak());

// ============================================================ 4. VISION & PHASING
A(H1("4. Product Vision & Phasing Strategy"));
A(P("The portal is designed as a platform delivered in four phases — built one block at a time, each shippable and valuable on its own, each enabled by the last. Phase 1 is authorised by this document; Phases 2–4 are designed here and authorised separately."));
A(table([1150, 2050, 3260, 2900],
  ["Phase", "Theme", "Capability", "Release posture"],
  [
    [{ t: "1", bold: true, fill: "E3F0E3" }, { t: "Portal MVP", bold: true }, "Client records, guided data entry, calc engine, SACS+TCC PDFs, export", "Internal to this firm — AUTHORISE NOW"],
    [{ t: "2", bold: true, fill: "E8F1FA" }, { t: "Automated data", bold: true }, "Read-only, consented pulls (Plaid/Zillow/PreciseFP; Schwab & RightCapital where permitted)", "Internal — later funding decision"],
    [{ t: "3", bold: true, fill: "FBF0E1" }, { t: "AI agents", bold: true }, "Onboarding agent, document/statement extraction, anomaly flagging — human-in-the-loop", "Internal — later funding decision"],
    [{ t: "4", bold: true, fill: "F3E8F3" }, { t: "SaaS platform", bold: true }, "Multi-tenant, self-serve onboarding, billing, admin", { t: "PUBLIC RELEASE to advisory firms", bold: true }],
  ]
));
A(spacer());
A(callout("WHY DESIGN IT ALL NOW.",
  "The expensive mistakes in V1 would be single-tenant data models, credential handling that can't be hardened, and a calc/render core entangled with the UI. By specifying Phases 2–4 up front, V1 is built with a tenant boundary, a credential vault seam, and a headless calculation+rendering core — so the future is a matter of funding, not re-architecture.",
  "E8F1FA", BLUE));
A(pageBreak());

// ============================================================ 5. SCOPE
A(H1("5. Scope"));
A(H2("5.1 In scope — Phase 1 (authorised by this document)"));
A(bullet("Client profile & account-structure management (lightweight CRM)."));
A(bullet("One-click quarterly report workflow with a guided, validated data-entry form."));
A(bullet("Deterministic calculation engine implementing all SACS & TCC rules (Section 9)."));
A(bullet("SACS and TCC PDF generation matching the existing templates (fixed layout)."));
A(bullet("PDF download; Canva export subject to the decision in Section 19."));
A(bullet("Internal authentication, role-based access, and an audit log."));
A(bullet("Report history (re-download previous quarters), subject to storage decision (Section 19)."));
A(H2("5.2 Designed here, authorised later — Phases 2–4"));
A(bullet("Integration layer: PreciseFP, Plaid, Zillow, Schwab, RightCapital, Pinnacle, Dropbox, Canva, email."));
A(bullet("AI agent layer: client-onboarding agent; statement/document data-extraction agent; anomaly flagging."));
A(bullet("Client-facing surfaces: onboarding forms, expense-worksheet capture, monthly report distribution."));
A(bullet("Multi-tenancy, tenant administration, metered billing, and public self-serve onboarding."));
A(H2("5.3 Explicitly out of scope (all phases, unless re-scoped)"));
A(bullet("Redesigning the report templates' visual identity."));
A(bullet("Acting as a system of record for trading, custody, or money movement."));
A(bullet("Tax advice, financial advice logic, or portfolio decisions — the portal reports; it does not advise."));
A(bullet([T("Podcast-production assistance — noted in the source as a separate ", {}), T("hiring", { italics: true }), T(" request, not a software build.", {})]));
A(pageBreak());

// ============================================================ 6. ARCHITECTURE
A(H1("6. System Architecture"));
A(H2("6.1 Architectural principles"));
A(numItem([T("Deterministic core. ", { bold: true }), T("Calculations and rendering are a pure, headless library, independently testable and reusable by any future caller (API, agent, batch).", {})]));
A(numItem([T("Tenant-aware from day one. ", { bold: true }), T("Every record carries a tenant key even though V1 has one tenant — Phase 4 becomes configuration, not migration.", {})]));
A(numItem([T("Integration seam, unused in V1. ", { bold: true }), T("A provider interface and a credential vault boundary exist as the single place future data sources plug in.", {})]));
A(numItem([T("Secure by default. ", { bold: true }), T("Least privilege, encryption everywhere, full audit, no third-party data egress that compliance forbids.", {})]));
A(numItem([T("Simple where it can be. ", { bold: true }), T("Three users today; the UI is clean and server-rendered, with no heavy front-end framework.", {})]));
A(H2("6.2 Logical components"));
A(table([2700, 4360, 2300],
  ["Component", "Responsibility", "Phase"],
  [
    [{ t: "Web UI", bold: true }, "Client list, profile editor, report workflow, review & export screens", "1"],
    [{ t: "Application / API", bold: true }, "Auth, request handling, orchestration, validation", "1"],
    [{ t: "Calculation engine", bold: true }, "All SACS/TCC math; pure & deterministic", "1"],
    [{ t: "Rendering engine", bold: true }, "SACS/TCC PDF templates; fixed layout, variable bubbles", "1"],
    [{ t: "Data store", bold: true }, "Clients, accounts, liabilities, report runs, audit", "1"],
    [{ t: "Auth & RBAC", bold: true }, "Identity, roles, sessions, MFA", "1"],
    [{ t: "Audit log", bold: true }, "Immutable record of access & generation", "1"],
    [{ t: "Credential vault (seam)", bold: true, fill: "E8F1FA" }, "Encrypted store for provider credentials/tokens", "2"],
    [{ t: "Integration providers", bold: true, fill: "E8F1FA" }, "Pluggable read-only data fetchers", "2"],
    [{ t: "Agent runtime", bold: true, fill: "FBF0E1" }, "Onboarding & extraction agents, human-in-the-loop", "3"],
    [{ t: "Tenant admin & billing", bold: true, fill: "F3E8F3" }, "Provisioning, metering, self-serve onboarding", "4"],
  ]
));
A(H2("6.3 Technology stack"));
A(table([1900, 2400, 5060],
  ["Layer", "Choice", "Rationale"],
  [
    ["Hosting", "Railway (single region)", "Team default; simple web app, low compute; region pinned for compliance"],
    ["Frontend", "Server-rendered HTML/CSS/JS (light templating)", "Three internal users; clean & fast; no SPA overhead"],
    ["Backend", "Python (FastAPI or Flask)", "Strong PDF & data libraries; simple, well-understood"],
    ["Calc engine", "Pure Python module", "Deterministic, unit-testable in isolation"],
    ["PDF", "WeasyPrint (HTML/CSS templates) — ReportLab fallback", "HTML/CSS gives precise, maintainable fixed layouts; see Section 10"],
    ["Database", "SQLite (V1) on a Railway volume → PostgreSQL (Phase 2+)", "6 clients = trivial volume; Postgres when concurrency/multi-tenant arrives"],
    ["AuthN/Z", "Session cookies + hashed passwords + TOTP MFA", "Simple, standard, compliance-friendly"],
    ["Secrets", "Railway env vars (V1) → managed vault (Phase 2)", "No secrets in code; vault seam ready"],
    ["AI", "None in V1 → governed model access (Phase 3)", "V1 is deterministic; AI gated behind no-training terms"],
  ]
));
A(P([T("Environment variables (V1): ", {}), T("RAILWAY_DATABASE_PATH", { font: "Consolas" }), T(", and ", {}), T("CANVA_API_KEY", { font: "Consolas" }), T(" only if Canva export is authorised.", {})]));
A(H2("6.4 Request flow (quarterly report)"));
A(numItem("User selects a client and clicks Generate Report."));
A(numItem("App loads the client profile, pre-fills static fields, and presents a validated entry form for current balances."));
A(numItem("On submit, the app validates completeness, then calls the calculation engine (pure function: inputs → totals)."));
A(numItem("Computed values feed the rendering engine, which returns SACS and TCC PDFs."));
A(numItem("User reviews on-screen, then downloads PDFs and/or exports to Canva; the run is recorded in the audit log."));
A(H2("6.5 How V1 enables later phases"));
A(table([2600, 3380, 3380],
  ["Future need", "Enabled by this V1 decision", "Phase"],
  [
    ["Automated data pulls", "Manual entry sits behind the same provider interface a fetcher will implement", "2"],
    ["Credential security", "Vault seam + read-only token model designed in from the start", "2"],
    ["AI extraction", "Calc/render core is headless, so an agent can call it exactly as the UI does", "3"],
    ["Public multi-tenant SaaS", "Tenant key on every row; Postgres migration path; RBAC already present", "4"],
  ]
));
A(pageBreak());

// ============================================================ 7. DATA MODEL
A(H1("7. Data Architecture & Model"));
A(H2("7.1 Core entities"));
A(table([2300, 5100, 1960],
  ["Entity", "Key attributes", "Notes"],
  [
    [{ t: "Tenant", bold: true }, "id, name, branding, region", "One row in V1; spine of Phase 4"],
    [{ t: "User", bold: true }, "id, tenant_id, name, email, role, mfa_secret, password_hash", "Roles: Owner, Planner, Assistant"],
    [{ t: "Client (Household)", bold: true }, "id, tenant_id, display_name, status, created_at", "A household, not a person"],
    [{ t: "Person", bold: true }, "id, client_id, role (C1/C2), name, dob, ssn_last4", "1–2 per household"],
    [{ t: "Account", bold: true }, "id, client_id, owner (C1/C2/Joint), category (retirement/non-retirement), type, acct_last4, has_cash_balance", "Drives TCC bubbles"],
    [{ t: "Trust", bold: true }, "id, client_id, property_address, last_value, source", "House value (Zillow in P2)"],
    [{ t: "Liability", bold: true }, "id, client_id, type, interest_rate, balance", "0–3 typically"],
    [{ t: "StaticFinancials", bold: true }, "client_id, monthly_salary, monthly_expense_budget, reserve_target_inputs, floor", "Changes rarely"],
    [{ t: "ReportRun", bold: true }, "id, client_id, period, entered_values(json), computed_values(json), created_by, created_at", "One per quarterly generation"],
    [{ t: "AuditEvent", bold: true }, "id, tenant_id, user_id, action, entity, timestamp, ip", "Immutable"],
    [{ t: "ProviderCredential", bold: true, fill: "E8F1FA" }, "id, tenant_id, provider, encrypted_token, scope, status", "Phase 2 — vault-encrypted"],
  ]
));
A(H2("7.2 Relationships (summary)"));
A(bullet("A Tenant has many Users and Clients."));
A(bullet("A Client (household) has 1–2 Persons, many Accounts, 0–1 Trust, 0–N Liabilities, one StaticFinancials, and many ReportRuns."));
A(bullet("A ReportRun snapshots both the entered balances and the computed outputs, so any past report is exactly reproducible."));
A(H2("7.3 Data lifecycle & retention"));
A(bullet("Static profile data is entered once and edited on change (new job, raise, new account)."));
A(bullet("Dynamic balances are captured per ReportRun; the previous run seeds each field as a reference (“use last value”)."));
A(bullet("ReportRuns are retained per the storage decision in Section 19 (default: retain, to power history & audit)."));
A(bullet("Retention, export, and deletion honour the firm's compliance policy; PII fields are minimised (only SSN last-4 is stored)."));
A(pageBreak());

// ============================================================ 8. FUNCTIONAL DESIGN
A(H1("8. Functional Design"));
A(P("Each module below lists its purpose, key behaviour, and acceptance signals. Modules 8.1–8.6 are Phase 1; 8.7–8.11 are designed for later phases."));

A(H2("8.1 Client & Account Management (Phase 1)"));
A(bullet("Create/edit a household: names, DOB, auto-calculated age, SSN last-4, single or married (C1/C2)."));
A(bullet("Define account structure: retirement accounts (IRA, Roth IRA, 401k, pension — never joint), non-retirement accounts (brokerage, joint, options), trust (property address), liabilities (type, rate)."));
A(bullet("Enter static financials once: monthly after-tax salary, agreed expense budget, private-reserve target inputs."));
A(bullet("Client list view with last-report date; edit on change."));
A(callout("RULE.", "Retirement accounts cannot be joint; non-retirement accounts may be joint. The UI enforces this when accounts are added.", "F0F4F8", BLUE));

A(H2("8.2 Quarterly Report Workflow (Phase 1)"));
A(bullet("One-click Generate Report from a client profile."));
A(bullet("A single form, grouped by report section (SACS fields, then TCC fields), pre-filled with static data."));
A(bullet("Each dynamic field shows its last known value and a “use last value” option; manual override always available."));
A(bullet("Incomplete required fields are highlighted; a report cannot be generated until all required fields are filled."));
A(bullet("Clear field labels (e.g., “Roth IRA Balance”, “Schwab Brokerage Balance”, “Private Reserve Balance”, “Zillow Home Value”)."));

A(H2("8.3 Calculation Engine (Phase 1)"));
A(P([T("A pure module that takes entered + static values and returns every total in real time. Full rules in ", {}), T("Section 9", { bold: true }), T(". It performs no I/O and is covered by exhaustive unit tests.", {})]));

A(H2("8.4 PDF Generation (Phase 1)"));
A(bullet("SACS: green Inflow circle, red Outflow circle, blue Private Reserve, connecting arrows; header with client name & date; page 2 with reserve, Schwab investment balance, target."));
A(bullet("TCC: green client-info bubbles (name, age, DOB, SSN last-4); retirement (top), non-retirement (bottom), trust (centre), liabilities (separate); gray total boxes; variable bubble count per client."));
A(bullet("Layout is fixed — nothing shifts or misaligns regardless of number size or account count; brand colours applied. See Section 10."));

A(H2("8.5 Export (Phase 1)"));
A(bullet("Download SACS and TCC as separate, print-ready PDFs."));
A(bullet("Optional “Export to Canva” into the team workspace for last-minute visual edits (subject to Section 19)."));
A(bullet("Report history: re-download prior quarters (subject to storage decision)."));

A(H2("8.6 Authentication & Access Control (Phase 1)"));
A(bullet("Email + password (hashed) with TOTP MFA; session cookies; idle timeout."));
A(bullet("Roles: Owner (full), Planner (full client + report), Assistant (data entry + generate)."));
A(bullet("Every login, view of client PII, and report generation is written to the audit log."));

A(H2("8.7 Integration Layer (Phase 2 — designed)"));
A(P("A uniform read-only provider interface (fetch balances/values, return normalised fields, report freshness). Each source is an adapter behind that interface; the UI's manual entry is simply the “manual provider.” Adapters are added without touching the calc or render core."));
A(table([2200, 2400, 4760],
  ["Source", "Method", "Design notes"],
  [
    ["PreciseFP", "API (one-time import)", "Profile/onboarding data; map to Person/StaticFinancials"],
    ["Plaid", "Aggregation API", "Preferred path for bank/investment balances; consented, read-only"],
    ["Zillow", "Zestimate lookup", "Trust property value; clearly flagged as estimate"],
    ["Schwab", "Authorised-user access", { runs: [T("Compliance-gated: per-user, read-only, "), T("never a shared agent login", { bold: true })] }],
    ["RightCapital", "API (guarded)", "Known-unreliable; force-refresh then verify; treated as low-trust"],
    ["Pinnacle Bank", "Secure email today", "Manual until a secure channel exists; do not automate insecurely"],
  ]
));
A(callout("COMPLIANCE GUARDRAIL.", "No source is automated unless access is consented, read-only, attributable to a permitted user, and free of forbidden data egress. Where those cannot be met (e.g., a shared/third-party login), the field stays manual. This is a design rule, not a limitation to engineer around.", "FFF8E1", AMBER));

A(H2("8.8 AI Agent Layer (Phase 3 — designed)"));
A(bullet([T("Onboarding agent: ", { bold: true }), T("emails the client the onboarding/expense forms, chases reminders, escalates to staff after a threshold, and lands structured data into the profile.", {})]));
A(bullet([T("Extraction agent: ", { bold: true }), T("reads uploaded statements/PDFs and proposes balances for human confirmation — never auto-commits to a report.", {})]));
A(bullet([T("Anomaly flagging: ", { bold: true }), T("highlights values that moved implausibly versus last quarter for staff review.", {})]));
A(P([T("All agents are ", {}), T("human-in-the-loop", { bold: true }), T(" and sit outside the deterministic numeric path: they propose, a person disposes. Governance in Section 12.", {})]));

A(H2("8.9 Client-Facing Expense Worksheet (Phase 3/4 — designed)"));
A(bullet("Replaces the emailed Excel sheet with a secure link clients complete; results flow into StaticFinancials with staff approval."));

A(H2("8.10 Report Distribution (Phase 3/4 — designed)"));
A(bullet("Optional scheduled email delivery of finished reports (e.g., monthly) — off by default; the firm currently reports quarterly."));
A(bullet("Optional auto-save of generated reports to the firm's Dropbox (subject to Section 19)."));

A(H2("8.11 Multi-Tenancy, Admin & Billing (Phase 4 — designed)"));
A(bullet("Tenant provisioning, per-tenant branding, self-serve onboarding for new advisory firms."));
A(bullet("Usage metering and billing (cost-plus on data/compute); admin console for support."));
A(bullet([T("This is the ", {}), T("public-release", { bold: true }), T(" form of the product: the same headless core, exposed to many firms.", {})]));
A(pageBreak());

// ============================================================ 9. BUSINESS RULES
A(H1("9. Calculation Engine — Business Rules"));
A(P("These rules are the deterministic heart of the system and must be implemented exactly. They are covered by unit tests with worked examples drawn from the source material."));
A(H2("9.1 SACS (cash-flow)"));
A(table([4680, 4680],
  ["Output", "Rule"],
  [
    ["Excess to Private Reserve", "Excess = Inflow − Outflow"],
    ["Private Reserve Target", "Target = (6 × monthly expenses) + Σ insurance deductibles"],
    ["Outflow", "Agreed monthly budget (rounded up to create a buffer); auto-transferred inflow→outflow"],
    ["Floor", "$1,000 minimum retained per bank account (constant)"],
  ]
));
A(H2("9.2 TCC (net worth)"));
A(table([4680, 4680],
  ["Output", "Rule"],
  [
    ["Client 1 Retirement Total", "Σ of Client 1 retirement account balances"],
    ["Client 2 Retirement Total", "Σ of Client 2 retirement account balances"],
    ["Non-Retirement Total", { runs: [T("Σ of all non-retirement balances "), T("(excludes the trust)", { bold: true })] }],
    ["Grand Total Net Worth", "C1 Retirement + C2 Retirement + Non-Retirement + Trust"],
    ["Liabilities Total", { runs: [T("Σ of liabilities, shown "), T("separately — NOT subtracted", { bold: true }), T(" from net worth")] }],
    ["Account balance vs cash", "Investment account balance already includes its cash sub-balance (cash is shown, not added again)"],
  ]
));
A(callout("CRITICAL.", "Two rules were emphasised repeatedly by the client and must be exact: the trust is NOT included in the non-retirement total (only in the grand total), and liabilities are NEVER subtracted from net worth. Unit tests assert both.", "FDECEC", RED));
A(H2("9.3 Worked example (TCC, illustrative)"));
A(P("Retirement: IRA $11,000 + Roth IRA $15,000 = $26,000. Non-retirement: brokerage $50,000. Trust: house $450,000. Grand total = $526,000. Liability: mortgage $200,000 shown separately (net worth remains $526,000)."));
A(pageBreak());

// ============================================================ 10. PDF RENDERING
A(H1("10. PDF Rendering Approach"));
A(P("The reports must match Andrew's existing templates exactly, never shift, and handle a variable number of account bubbles. The recommended approach is HTML/CSS templates rendered to PDF by WeasyPrint."));
A(table([3120, 6240],
  ["Decision", "Rationale"],
  [
    ["HTML/CSS templates → WeasyPrint", "Precise, maintainable fixed layouts; easy brand styling; deterministic output"],
    ["Absolute-positioned SACS diagram", "Bubbles & arrows pinned to coordinates so nothing reflows with value length"],
    ["Grid-driven TCC bubbles", "A fixed grid with N slots per quadrant; empty slots collapse cleanly; 1–6 accounts/spouse supported"],
    ["Server-side fonts & colours", "Brand blue baked in; identical rendering across machines"],
    ["ReportLab as fallback", "If any layout proves hard in HTML, drop to programmatic drawing for that element"],
  ]
));
A(bullet("Numbers are placed into fixed visual positions; long values shrink-to-fit within their box rather than pushing layout."));
A(bullet("Header carries client name and report date on both reports."));
A(bullet([T("Acceptance is visual parity against ", {}), T("sample PDFs requested from the team", { bold: true }), T(" — these are the source of truth for exact placement.", {})]));
A(pageBreak());

// ============================================================ 11. INTEGRATION ARCH
A(H1("11. Integration Architecture (Phases 2+)"));
A(P("Integrations are deliberately absent from V1 and introduced behind the provider interface and credential vault described in Section 6. The sequence is risk-ordered: easiest and safest first."));
A(table([1150, 3300, 2900, 2010],
  ["Order", "Integration", "Why this order", "Phase"],
  [
    ["1", "PreciseFP one-time import", "Read-only profile data; low risk", "2"],
    ["2", "Zillow Zestimate", "Single value; clearly an estimate", "2"],
    ["3", "Plaid aggregation", "Consented, read-only, replaces fragile RightCapital path", "2"],
    ["4", "Schwab authorised-user read", "High value but compliance-gated; per-user only", "2/3"],
    ["5", "RightCapital (guarded)", "Low-trust; only if Plaid migration is incomplete", "2/3"],
    ["6", "Dropbox / Canva / email", "Output-side conveniences", "3"],
  ]
));
A(P([T("Credential handling: read-only scopes, per-user attribution, encrypted at rest in the vault, rotatable, revocable, and ", {}), T("never shared with an AI agent as a standing login", { bold: true }), T(". A failed or stale pull degrades gracefully to manual entry with a clear flag.", {})]));
A(pageBreak());

// ============================================================ 12. AI ARCH
A(H1("12. AI & Agent Architecture (Phase 3)"));
A(H2("12.1 Where AI is — and is not"));
A(bullet([T("AI is ", {}), T("never", { bold: true }), T(" in the numeric path. Totals are always deterministic and auditable.", {})]));
A(bullet("AI assists at the edges: chasing onboarding inputs, extracting candidate values from documents, and flagging anomalies for human review."));
A(H2("12.2 Governance & guardrails"));
A(bullet([T("No-training guarantee: ", { bold: true }), T("client data is processed under terms that prohibit using it to train third-party models.", {})]));
A(bullet([T("Human-in-the-loop: ", { bold: true }), T("agents propose; staff confirm before anything reaches a report.", {})]));
A(bullet([T("Least data: ", { bold: true }), T("agents receive only the fields needed for their task.", {})]));
A(bullet([T("Full audit: ", { bold: true }), T("every agent action and human decision is logged.", {})]));
A(bullet([T("Compliance-aligned hosting: ", { bold: true }), T("no model provider or tool forbidden by the firm's policy (e.g., consumer Google tooling) is used.", {})]));
A(pageBreak());

// ============================================================ 13. SECURITY
A(H1("13. Security, Privacy & Compliance"));
A(H2("13.1 Data sensitivity"));
A(P([T("The system holds PII and financial data: names, DOB, ", {}), T("SSN last-4 only", { bold: true }), T(" (never full SSN), account types with last-4 numbers, balances, and net worth. It is a confidential system throughout.", {})]));
A(H2("13.2 Controls"));
A(table([2600, 6760],
  ["Area", "Control"],
  [
    ["In transit", "TLS everywhere; HSTS"],
    ["At rest", "Encrypted database volume; sensitive columns additionally encrypted (Phase 2 vault for credentials)"],
    ["Access", "Role-based; least privilege; MFA on every account"],
    ["Audit", "Immutable log of logins, PII views, report generations, and (Phase 3) agent actions"],
    ["Secrets", "Never in code; env vars (V1) → managed vault (Phase 2); rotatable"],
    ["Data egress", "No data sent to services the firm's compliance policy forbids"],
    ["Backups", "Encrypted, region-pinned, tested restore"],
    ["Tenancy", "Tenant key enforced in every query; isolation tested before Phase 4"],
  ]
));
A(H2("13.3 Compliance posture"));
A(bullet([T("Honour the firm's stated constraints: ", {}), T("no forbidden consumer tooling", { bold: true }), T("; Schwab/RightCapital credentials are not shared with agents; bank data stays on secure channels.", {})]));
A(bullet("Hosting region pinned to satisfy data-residency expectations (confirm in Section 19)."));
A(bullet([T("A path to ", {}), T("SOC 2 Type II", { bold: true }), T(" is assumed for the Phase 4 public release; controls above are chosen to be compatible.", {})]));
A(bullet("The portal reports facts; it does not provide financial or tax advice, keeping it outside advice-specific regulatory scope."));
A(pageBreak());

// ============================================================ 14. NFRs
A(H1("14. Non-Functional Requirements"));
A(table([2300, 7060],
  ["Attribute", "Requirement"],
  [
    ["Performance", "Report generation (both PDFs) in < 10 s; form interactions feel instant"],
    ["Availability", "V1: business-hours reliability on a single region. Phase 4: 99.9% target"],
    ["Scalability", "V1: tens of clients, 3 users. Architecture scales to thousands of clients across tenants"],
    ["Usability", "A non-technical assistant completes a report unaided; clear validation and “use last value”"],
    ["Accessibility", "Legible type, sufficient contrast, keyboard-navigable forms"],
    ["Maintainability", "Headless calc/render core with high unit-test coverage; templates editable without code changes"],
    ["Observability", "Health checks, error logging, uptime monitoring (team-hosted)"],
    ["Portability", "SQLite→PostgreSQL migration path defined; no lock-in on the render core"],
  ]
));
A(pageBreak());

// ============================================================ 15. DELIVERY
A(H1("15. Delivery Plan & Milestones"));
A(P("Indicative, assuming one engineer with part-time review; calendar starts on authorisation. Phases 2–4 are planning estimates for the forward view, not part of this authorisation."));
A(table([1100, 2500, 4100, 1660],
  ["Phase", "Milestone", "Deliverables", "Indicative"],
  [
    [{ t: "1", bold: true }, "M1 Foundations", "Data model, auth/RBAC, client & account CRUD", "Wk 1–2"],
    [{ t: "1", bold: true }, "M2 Engine", "Calculation engine + full unit tests (Section 9)", "Wk 2–3"],
    [{ t: "1", bold: true }, "M3 Reports", "SACS & TCC PDF templates to visual parity", "Wk 3–5"],
    [{ t: "1", bold: true }, "M4 Workflow", "Guided entry, validation, history, export", "Wk 5–6"],
    [{ t: "1", bold: true, fill: "E3F0E3" }, { t: "M5 V1 Launch", bold: true }, "Hardening, UAT with the team, go-live", "Wk 6–7"],
    [{ t: "2", fill: "E8F1FA" }, "Integrations", "PreciseFP, Zillow, Plaid; vault; Schwab (gated)", "+4–6 wk"],
    [{ t: "3", fill: "FBF0E1" }, "Agents", "Onboarding & extraction agents; distribution", "+6–8 wk"],
    [{ t: "4", fill: "F3E8F3" }, "SaaS", "Multi-tenancy, billing, self-serve, SOC 2 path", "Quarter-scale"],
  ]
));
A(P([T("Prototype of V1 can be demonstrated within roughly ", {}), T("one week", { bold: true }), T(" of authorisation, with full V1 around six to seven weeks.", {})]));
A(pageBreak());

// ============================================================ 16. COST
A(H1("16. Effort, Cost & Commercial Model"));
A(P("Costs are indicative and should be confirmed against the prevailing commercial agreement."));
A(table([3120, 6240],
  ["Item", "Basis"],
  [
    ["V1 build", "Flat per-build fee (“one credit,” ≈ $500 under the current plan); ~6–7 weeks effort"],
    ["Hosting & ops", "Provider hosts, monitors uptime, and fixes defects (included in membership)"],
    ["Usage (Phase 2+)", "Metered data/compute at cost + ~20%; framed as tens of dollars/month at this scale"],
    ["Membership", "Monthly plan under which credits are issued and apps are hosted"],
    ["Phases 2–4", "Each is a separate build/credit decision; estimated in Section 15"],
  ]
));
A(callout("VALUE FRAME.", "At ~6 clients × 4 quarters, V1 saves on the order of 20+ staff-days/year and removes a recurring error class. The larger prize is capacity: serving 12+ clients (and, via Phase 4, an external market) without proportional hiring.", "E8F1FA", BLUE));
A(pageBreak());

// ============================================================ 17. RISKS
A(H1("17. Risks, Assumptions & Dependencies"));
A(H2("17.1 Risk register"));
A(table([2700, 1400, 1400, 3860],
  ["Risk", "Likelihood", "Impact", "Mitigation"],
  [
    ["Exact visual parity with templates is fiddly", "Med", "Med", "Request sample PDFs up front; HTML/CSS + ReportLab fallback; UAT sign-off on layout"],
    ["Unverified firm/identity details", "Med", "Low", "Treat as placeholders; confirm before client-facing use (17.2)"],
    ["Scope creep from “dreaming big” items", "Med", "Med", "Phase boundaries; one block at a time; Section 19 decisions"],
    ["Compliance limits on data sources", "High", "Low", "By design, those stay manual until safe; no forced automation"],
    ["RightCapital data unreliable", "High", "Low", "Low-trust adapter; prefer Plaid; manual override always"],
    ["PII exposure", "Low", "High", "Encryption, RBAC, MFA, audit, SSN last-4 only, region pinning"],
    ["Single-engineer key-person risk", "Med", "Med", "High test coverage; documented headless core; simple stack"],
  ]
));
A(H2("17.2 Assumptions to confirm"));
A(bullet("Firm name, legal entity, and city (attributed to web research, not stated on the call) are unverified placeholders."));
A(bullet("Sample SACS/TCC PDFs and the “Data Point List” document will be provided as the layout source of truth."));
A(bullet("Current cadence is quarterly; monthly distribution is a future option, off by default."));
A(H2("17.3 Dependencies"));
A(bullet("Timely access to the team for UAT and business-rule confirmation."));
A(bullet("Provider accounts/credentials for Phase 2 (Plaid, PreciseFP, etc.) when those phases are authorised."));
A(pageBreak());

// ============================================================ 18. ACCEPTANCE
A(H1("18. Acceptance Criteria & Definition of Done (V1)"));
A(numItem("A client (single or married) can be created with full profile, accounts, liabilities, trust, and static financials."));
A(numItem("Generate Report pre-fills static data and presents a validated entry form with “use last value” and override."));
A(numItem("A report cannot be generated with missing required fields."));
A(numItem("All SACS & TCC totals match Section 9 exactly, verified by unit tests including the emphasised rules (trust handling; liabilities not subtracted)."));
A(numItem("SACS and TCC PDFs match the sample templates to the team's visual satisfaction; layout is stable across value sizes and account counts (1–6 per spouse)."));
A(numItem("PDFs download cleanly; Canva export works if authorised; prior reports can be re-downloaded if storage is enabled."));
A(numItem("Auth, RBAC, MFA, and audit logging are in place; security checklist (Section 13) passes."));
A(numItem("The team completes a real quarterly report end-to-end in under an hour during UAT."));
A(pageBreak());

// ============================================================ 19. DECISIONS
A(H1("19. Open Decisions Requiring Authorisation"));
A(P("These are product/owner calls. Defaults are proposed so silence does not block the build."));
A(table([3000, 4360, 2000],
  ["Decision", "Options / proposed default", "Owner"],
  [
    ["Canva export", "Build now vs defer. Default: defer; portal PDF first (client said they’d rather not use Canva/Word at all)", "PM/Owner"],
    ["Report storage", "Store report history vs generate-and-forget. Default: store (enables history & audit)", "PM/Owner"],
    ["Dropbox auto-save", "In V1 vs later. Default: later (lightweight to add once confirmed)", "PM/Owner"],
    ["Monthly email distribution", "Build vs defer. Default: defer (firm reports quarterly)", "PM/Owner"],
    ["Hosting region", "Confirm region for data residency/compliance", "Owner + Compliance"],
    ["Identity placeholders", "Confirm firm name/entity/city before client-facing use", "Owner"],
    ["Phase 2 trigger", "When to authorise automated integrations", "Exec Sponsor"],
  ]
));
A(pageBreak());

// ============================================================ 20. SIGN-OFF
A(H1("20. Authorisation & Sign-Off"));
A(P([T("By signing below, the Product Owner / Owner authorises the ", {}), T("Phase 1 (V1)", { bold: true }), T(" build as scoped in Sections 5, 8, 9 and 18, acknowledges the forward roadmap (Sections 4 & 15) including the intent to productise later phases for public release, and records decisions on the items in Section 19. Executive sponsors sign to confirm evaluation and funding support.", {})]));
A(spacer());
const sgn = { paras: [ new Paragraph({ spacing: { before: 220, after: 0 }, children: [T("")] }) ] };
A(table([2600, 2600, 2480, 1680],
  ["Role", "Name", "Signature", "Date"],
  [
    [{ t: "Product Owner / Owner", bold: true }, "", sgn, ""],
    [{ t: "Product Manager", bold: true }, "", sgn, ""],
    [{ t: "Executive Sponsor", bold: true }, "", sgn, ""],
    [{ t: "Engineering Lead", bold: true }, "", sgn, ""],
    [{ t: "Compliance / Security", bold: true }, "", sgn, ""],
  ]
));
A(spacer());
A(H2("Authorisation decision"));
A(table([3120, 6240],
  ["Decision", "Mark one"],
  [
    [{ t: "APPROVED — proceed with V1", bold: true, color: GREEN }, "☐"],
    [{ t: "APPROVED WITH CHANGES (note below)", bold: true, color: AMBER }, "☐"],
    [{ t: "NOT APPROVED", bold: true, color: RED }, "☐"],
  ]
));
A(P([T("Notes / conditions:", { bold: true })], { spacing: { before: 160 } }));
A(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LIGHT, space: 6 } }, spacing: { before: 260 }, children: [T("")] }));
A(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LIGHT, space: 6 } }, spacing: { before: 260 }, children: [T("")] }));
A(pageBreak());

// ============================================================ APPENDICES
A(H1("Appendix A — Glossary"));
A(table([2300, 7060],
  ["Term", "Meaning"],
  [
    ["SACS", "Simple Automated Cash Flow — one-page diagram of monthly money flow (Inflow → Outflow → Private Reserve)"],
    ["TCC", "Total Client Chart — one-page net-worth overview by account type"],
    ["Inflow", "Take-home pay deposited to the primary checking account"],
    ["Outflow", "Agreed monthly expense budget (rounded up) transferred from inflow"],
    ["Private Reserve", "High-yield savings holding the excess; target = 6 × expenses + insurance deductibles"],
    ["Trust", "Usually the client’s home; value from Zillow Zestimate"],
    ["Floor", "$1,000 minimum kept in each bank account"],
    ["Pinnacle Bank", "Preferred bank; balances via secure email 2 days before meetings"],
    ["RightCapital", "Planning aggregator; has an API but data is often stale/disconnected"],
    ["PreciseFP", "Onboarding questionnaire tool; closest existing thing to a CRM"],
    ["Plaid", "Bank/investment data aggregation API (preferred automation path)"],
  ]
));
A(H1("Appendix B — Data-Point to Source Mapping"));
A(table([2400, 2600, 4360],
  ["Field", "Report", "Source (V1 = manual entry)"],
  [
    ["Client salary (inflow)", "SACS", "Onboarding / expense worksheet"],
    ["Monthly expense budget (outflow)", "SACS", "Monthly expense worksheet (Excel)"],
    ["Private reserve balance", "SACS", "Bank balance (secure email, 2 days prior)"],
    ["Schwab investment balance", "SACS/TCC", "Schwab (authorised users only)"],
    ["Reserve target inputs", "SACS", "Agreed: 6× expenses + insurance deductibles"],
    ["Names, DOB, SSN last-4", "TCC", "PreciseFP / onboarding"],
    ["Retirement balances", "TCC", "RightCapital / statements / Schwab"],
    ["Non-retirement balances", "TCC", "RightCapital / statements"],
    ["Home value (trust)", "TCC", "Zillow Zestimate"],
    ["Liabilities (type, rate, balance)", "TCC", "RightCapital / client statements"],
  ]
));
A(H1("Appendix C — Traceability (requirement → source)"));
A(table([3400, 2480, 3480],
  ["Requirement", "PRD / call ref", "Spec section"],
  [
    ["One-time client setup / CRM-lite", "US1; call 35:44", "8.1, 7"],
    ["Guided entry + auto-calculation", "US2; call 25:36, 33:34", "8.2, 8.3, 9"],
    ["Exact calc rules (trust, liabilities)", "US2 notes; call 24:28, 26:15", "9.2"],
    ["Fixed-layout SACS & TCC PDFs", "US3; call 11:15, 13:57", "8.4, 10"],
    ["Export (PDF / Canva)", "US4; call 52:56", "8.5, 19"],
    ["No APIs / no AI in V1", "PRD stack note", "3.3, 6.3, 11, 12"],
    ["Automated pulls deferred", "Out-of-scope; call 48:14, 49:06", "8.7, 11"],
    ["Onboarding agent / distribution", "Future; call 16:15, 43:36", "8.8, 8.10"],
  ]
));
A(H1("Appendix D — Source Artifacts"));
A(bullet("PRD: “PRD AI Engineer Test.pdf” (v1.0, 2026-04-09) — 14 pages."));
A(bullet("Discovery call recording: “AW - AI Test Project.mp4” (2026-04-01, ~55 min) + a prior call referenced therein."));
A(bullet("Derived analysis reports: “AW_AI_Test_Project_Report.md” and “PRD_AI_Engineer_Test_Report.md”."));
A(spacer());
A(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240 }, border: { top: { style: BorderStyle.SINGLE, size: 6, color: BLUE, space: 8 } }, children: [
  new TextRun({ text: "END OF SPECIFICATION  •  CONFIDENTIAL", color: GREY, size: 18 }),
]}));

// ============================================================ DOCUMENT
const doc = new Document({
  creator: "Engineering (AI Practice)",
  title: "Technical Specification — AW Client Report Portal",
  description: "Exec-facing technical specification for the AW Client Report Portal",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: "Arial", size: 21 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, color: NAVY, font: "Arial" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 0, keepNext: true,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "BFD3E6", space: 4 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 25, bold: true, color: BLUE, font: "Arial" },
        paragraph: { spacing: { before: 200, after: 90 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, color: "3A3A3A", font: "Arial" },
        paragraph: { spacing: { before: 140, after: 70 }, outlineLevel: 2, keepNext: true } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 920, hanging: 260 } } } },
      ]},
      { reference: "nums", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 460, hanging: 260 } } } },
      ]},
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1300, right: 1440, bottom: 1300, left: 1440 } } },
    headers: { default: new Header({ children: [ new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: 9360 }],
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "DDDDDD", space: 4 } },
      spacing: { after: 60 },
      children: [ new TextRun({ text: "Technical Specification — AW Client Report Portal", color: GREY, size: 16 }),
                  new TextRun({ text: "\tCONFIDENTIAL", color: RED, size: 16, bold: true }) ],
    }) ] }) },
    footers: { default: new Footer({ children: [ new Paragraph({
      tabStops: [{ type: TabStopType.CENTER, position: 4680 }, { type: TabStopType.RIGHT, position: 9360 }],
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: "DDDDDD", space: 4 } },
      children: [ new TextRun({ text: "v1.0 — 18 Jun 2026", color: GREY, size: 16 }),
                  new TextRun({ text: "\tPage ", color: GREY, size: 16 }),
                  new TextRun({ children: [PageNumber.CURRENT], color: GREY, size: 16 }),
                  new TextRun({ text: " of ", color: GREY, size: 16 }),
                  new TextRun({ children: [PageNumber.TOTAL_PAGES], color: GREY, size: 16 }),
                  new TextRun({ text: "\tDraft for authorisation", color: GREY, size: 16 }) ],
    }) ] }) },
    children: body,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = "C:\\Users\\tbeng\\Downloads\\Technical_Spec_AW_Client_Report_Portal.docx";
  fs.writeFileSync(out, buf);
  console.log("WROTE", out, buf.length, "bytes");
});
