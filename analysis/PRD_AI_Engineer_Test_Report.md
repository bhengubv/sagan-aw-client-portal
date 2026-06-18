# Document Report — *PRD AI Engineer Test.pdf*

**Prepared:** 2026-06-18
**Source file:** `C:\Users\tbeng\Downloads\PRD AI Engineer Test.pdf`
**Basis:** Full text extraction (PyMuPDF) of all 14 pages. The PDF is a pure-text document (no embedded images), generated from **Google Docs**, internal title *"PRD AI Engineer Test."*

---

## 1. Executive Summary

The document is a **Product Requirements Document (PRD v1.0, dated 2026-04-09)** for a software build called the **"AW Client Report Portal."** It specifies a web app that lets a small financial-advisory firm enter client data into structured forms and auto-generate two polished quarterly PDF reports — **SACS** (cashflow) and **TCC** (net worth) — "in minutes instead of a full day."

**The key insight:** this PRD is the **direct downstream output of the video call** analyzed earlier (`AW - AI Test Project.mp4`). It is almost certainly **auto-generated from the call transcript(s)** — it quotes participants with precise timestamps (e.g., 25:36, 33:34, 48:14) that match the transcript, references screen-share screenshots by timestamp, and its closing *Audit Notes* state that every requirement was *"traced to specific transcript moments across both calls."*

Together, the two files form an **"AI Engineer Test"**: a recorded requirements call (input) → a structured, buildable PRD (output) → engineering stories written *for an assigned engineer to implement*. It demonstrates an AI pipeline (Sagan's) that converts a messy sales/discovery call into a developer-ready spec — and/or serves as a take-home brief to evaluate an AI engineer.

---

## 2. Document Metadata

| Property | Value |
|---|---|
| Title | AW Client Report Portal — PRD v1.0 |
| PRD date | **2026-04-09** (8 days after the call) |
| Build type | New |
| Pages | 14 |
| Producer | Google Docs (Skia/PDF renderer) |
| Embedded images | 0 (text-only) |
| Author of the *product* | **Sagan** (AI agency from the call) |

---

## 3. Relationship to the Video (the central finding)

| | Video — *AW - AI Test Project.mp4* | PDF — *PRD AI Engineer Test* |
|---|---|---|
| Role | **Input**: requirements/discovery call | **Output**: developer-ready spec |
| Date | 2026-04-01 | 2026-04-09 |
| Content | Sagan (Zaki) interviews the firm (Rebecca, Maryann) | Structured PRD distilled from that + an earlier call |
| Evidence of link | — | Quotes the same lines at the same timestamps; lists screen-share screenshots (04:52, 05:18, 13:08, 20:52, 26:26, 29:14); "traced … across both calls" |

The PRD even references a **prior call** ("Andrew and John and Zach had talked about" zero manual data entry) — matching the video, where Zaki mentions reviewing an earlier call "with John and Zach." So the source material was **two calls**, and this PRD synthesizes both.

---

## 4. The Product — "AW Client Report Portal"

**One-line (verbatim):** *"A portal where the team enters client financial data into a structured form and generates polished quarterly SACS (cashflow) and TCC (net worth) PDF reports in minutes instead of a full day."*

**Core flow:**
1. **One-time client setup** — a lightweight CRM record (names, DOB, age, last-4 SSN, account structure, salary, expense budget, reserve target). Replaces scattered Excel/Dropbox/PreciseFP storage.
2. **Quarterly report run** — click *Generate Report* → structured form pre-filled with static data, blanks for current balances, "use last value" + manual override per field, incomplete fields flagged.
3. **Automatic math** — all totals computed deterministically (no manual arithmetic).
4. **PDF output** — pixel-perfect SACS + TCC PDFs matching the firm's existing templates; **download PDF** or **export to Canva**.

---

## 5. Client / Company Context (as stated in the PRD)

- Firm referred to as **"EF"**, a financial-planning firm based in **Atlanta**, serving **high- and ultra-high-net-worth families**. Legal/planning entity: **"Windbrook Solutions."**
- **Team of three:** **Andrew** (owner, template creator), **Rebecca** (financial planner; Schwab access; compliance), **Maryann** (executive assistant, *"recently hired through Sagan"*).
- **~6 retainer clients**, quarterly meetings, plus AUM revenue. Clients are millionaires expecting high accuracy.
- **Current pain:** report prep takes **a full day per client**, pulling data manually from **Pinnacle Bank, Charles Schwab, RightCapital, Zillow** and assembling in **Canva + Word** — error-prone.

> Note: these proper nouns (**EF, Windbrook Solutions, "AW," Atlanta**) do **not** appear in the portion of the call analyzed and are flagged "Researched from the customer's website." They may be the real entity names or **anonymized/test identifiers** — worth verifying (see §11).

---

## 6. Engineering Scope (User Stories)

The PRD lays out four user stories with explicit acceptance criteria (and repeatedly notes **"AI/Models: None"** — V1 is deterministic):

- **US1 — Client profile management:** add/edit clients (single or married → Client 1 / Client 2), define account structure (retirement / non-retirement / trust / liabilities w/ interest rates), enter static financials; client list with last-report date. *Serves as a lightweight CRM.*
- **US2 — Quarterly data entry + auto-calculation:** one-click report form, pre-filled static data, dynamic balance fields with last-known values, "use last value," override, completeness enforcement; **all math automatic and real-time.**
- **US3 — Polished PDF generation:** SACS (green Inflow / red Outflow / blue Private Reserve bubbles + arrows; page 2 = reserve, Schwab, target) and TCC (variable account bubbles, gray total boxes, separate liabilities); **fixed layout — nothing shifts.**
- **US4 — Export:** download SACS+TCC PDFs, optional Canva export, report history / re-download.

### Exact calculation rules (business logic the engineer must honor)
- SACS: **Excess = Inflow − Outflow**
- SACS: **Private Reserve Target = (6 × monthly expenses) + Σ insurance deductibles**
- TCC: **Client-1 Retirement Total**, **Client-2 Retirement Total**, **Non-Retirement Total** (excludes trust)
- TCC: **Grand Total Net Worth = C1 Retirement + C2 Retirement + Non-Retirement + Trust**
- TCC: **Liabilities Total displayed separately — NOT subtracted from net worth**

---

## 7. Recommended Technical Stack

| Layer | Choice | Rationale (per PRD) |
|---|---|---|
| Hosting | **Railway** | "Standard Sagan default" — simple web app |
| Frontend | **HTML + CSS + JS** | 3 users; simple/beautiful; no framework overhead |
| Backend | **Python** | PDF gen, form handling, calculations |
| Database | **SQLite** (Railway volume) | ~6 clients, minimal volume |
| PDF | **ReportLab or WeasyPrint** | Pixel-perfect fixed-layout templates |
| AI | **None for V1** | Pure data entry + arithmetic + PDF; no reasoning needed |

Env vars: `CANVA_API_KEY` (if Canva export), `RAILWAY_DATABASE_PATH`. **No external API integrations in V1** — intentional, due to RightCapital unreliability, Schwab compliance limits, and Pinnacle's email-only flow.

---

## 8. Data Sources, V2, and Out-of-Scope

- **V1 sources:** Manual form entry (primary); PreciseFP onboarding data (one-time manual transfer); Canva (optional, out-bound export).
- **V2 (deferred):** RightCapital API, Schwab auto-pull (compliance-gated), Pinnacle auto-request, Zillow Zestimate API, possible **Plaid** integration.
- **Out of scope / future "LEGO bricks":** client-facing expense worksheet in the portal; onboarding-automation agent; monthly email distribution; **podcast-production help** (noted as a *hiring* request from Andrew, not an agent build).
- **Discussed-but-unconfirmed (flagged for the engineer to verify):** Canva export priority (Rebecca: "we don't want to do it in either [Canva or Word], ideally"), Dropbox auto-save, monthly email distribution.

---

## 9. Key Domain Definitions (captured in the PRD)

- **SACS** — Simple Automated Cash Flow: one-page diagram of money flow (Inflow → Outflow → Private Reserve).
- **TCC** — Total Client Chart: one-page net-worth overview (retirement / non-retirement / trust / liabilities).
- **Inflow** (take-home pay), **Outflow** (agreed monthly budget, rounded up for buffer), **Private Reserve** (excess savings; target = 6mo expenses + deductibles), **Trust** (house value via Zillow), **Floor** ($1,000 min per account).
- **Pinnacle Bank** (balances via secure email), **RightCapital** (aggregator, unreliable API), **PreciseFP** (onboarding questionnaire / closest thing to a CRM).

---

## 10. PRD's Self-Assessment ("Confidence Score")

| Dimension | Score | Reason |
|---|---|---|
| Scope Definition | **5/5** | Two calls + a "Data Point List" doc + sample PDFs define exact fields/outputs |
| Technical Feasibility | **5/5** | Form → calc → PDF; no APIs, no AI; only challenge is exact visual layout |
| Customer Impact | **4/5** | Day→hour prep, error elimination; but only 6 clients (~24 person-days/yr saved). Bigger value = scale without hiring |
| **Overall** | **4/5** | Constrained by Customer Impact |

PRD verdict: *"Excellent build. Extremely well-defined scope with sample documents provided. Zero technical risk … Rebecca and Maryann are engaged, detail-oriented, and will be excellent collaborators."*

---

## 11. Notable Observations

1. **It's an auto-generated artifact.** The structure (One-line → Context → Developer Brief → Stack → Screenshots → Definitions → User Stories → Data Sources → Discussed/Out-of-scope → Confidence → Audit Notes) and the transcript-timestamp citations indicate a **templated AI pipeline** that turns call recordings into PRDs. The *Audit Notes* and *Discussed But Not Confirmed* sections are essentially the model showing its work and hedging on ambiguous items.
2. **New identifiers vs. the call.** "EF," "Windbrook Solutions," "Atlanta," and the project codename "AW" are not spoken in the analyzed call; the PRD attributes them to website research. They could be genuine or **anonymized test data** — verify before relying on them. (The call's only stated locations were Zaki in **Austin** and Maryann in **France**.)
3. **Minor numeric drift.** The SACS example shows **Inflow $15,000 → Outflow $11,000** here vs. **$12,000** on the frame I captured from the video — different example values on different template versions; not material.
4. **Name spelling varies** across sources: webcam label "maryam pashang," spoken "Marianne," PRD "Maryann." Likely the same person.
5. **Sagan does staffing too.** Maryann was "recently hired through Sagan," implying Sagan offers both AI builds *and* talent placement.

---

## 12. What This Reveals — the "AI Engineer Test"

Read together, the filename pair (*AI Test Project* → *PRD AI Engineer Test*) plus the engineer-directed language (*"the assigned engineer will review the transcript independently and make their own implementation decisions"*) point to one of two purposes — possibly both:

- **A test of an AI system** that ingests a sales/discovery call and emits a developer-ready PRD (Sagan's productized workflow), and/or
- **A take-home/evaluation brief** handed to an **AI engineer candidate**, who must build the AW Client Report Portal from this spec.

Either way, the document is a strong worked example of **call-to-spec automation**: a high-fidelity, buildable PRD with explicit acceptance criteria, exact business rules, a confidence score, and an audit trail — all derived from conversation.

---

## 13. Privacy / PII Notice ⚠️

The PRD contains business-sensitive detail (firm name, staff names, client process, financial logic) and references to client PII categories (DOB, last-4 SSN, balances) — though the sample figures appear illustrative. Treat as **confidential**. All processing was performed **locally**; extracted text is saved at `Downloads\_aw_test_frames\prd_text.txt`.
