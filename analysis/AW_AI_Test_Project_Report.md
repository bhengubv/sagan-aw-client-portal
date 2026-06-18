# Video Content Report — *AW - AI Test Project.mp4*

**Prepared:** 2026-06-18
**Source file:** `C:\Users\tbeng\Downloads\AW - AI Test Project.mp4`
**Basis:** Technical metadata, full-resolution frame extraction, on-screen document capture, and a full automated transcript of the 55-minute audio track (faster-whisper `small.en`, 575 segments / ~11,200 words).

---

## 1. Executive Summary

The file is a **~55-minute recording of a video conference call**, recorded **2026-04-01**. It is a **requirements-discovery / scoping call run by an AI-development agency, "Sagan,"** with a prospective/early client — a **small (3-person) financial-advisory firm serving high-net-worth clients.**

The purpose of the call is for Sagan to understand the firm's manual financial-report-production process so it can **build a custom AI web app ("agent") to automate it.** The firm currently hand-builds two financial reports per client (a cashflow system "SACS" and a net-worth "circle chart" called "TCC") in Canva/Word, pulling data from multiple sources — a process that takes ~1 day per report and is error-prone.

By the end of the call, a **version-1 scope is verbally agreed**: a secure portal that stores client data, auto-fills and does the math for the reports, prompts for missing fields, and outputs a polished PDF (with Canva export). Clear **next steps and commercial terms** are stated (see §8–9).

> The content is **financial-advisory and confidential**, including **partial client PII** (DOB, last-four SSN, account balances). See §10.

---

## 2. Technical Metadata

| Property | Value |
|---|---|
| Container | QuickTime / MOV (`.mp4`) |
| Duration | 3,313 s (**55 min 13 s**) |
| Video | H.264, **1600 × 800**, 25 fps |
| Audio | AAC, 48 kHz, stereo |
| File size | 160.4 MB |
| Recorded (creation_time) | **2026-04-01 17:00:30 UTC** |
| Speech | English (detected p = 1.00) |

Format (2:1 frame, small webcam tiles over a shared screen, Zoom in the macOS dock) is consistent with a recorded **Zoom** call. The recording begins ~1:48 before the first speech.

---

## 3. Participants & Roles

**The vendor — Sagan (AI agency):**
- **Zaki Mahomed** — "runs the **AI practice at Sagan**," only a few days into the role. Leads the call, gathers requirements, proposes the solution and pricing.
- *(Referenced, not present)* **John** and **Zach** — Sagan colleagues from an earlier call with this client.

**The client — a 3-person financial-advisory firm:**
- **Rebecca Pomeranz** — advisor; co-built the report templates; one of two people authorized to pull Schwab data.
- **Maryam Pashang** (addressed on the call as **"Marianne"**) — assistant; prepares the reports; originally from Mexico, living in France.
- *(Referenced, not present)* **Andrew** — the firm's **boss/owner**; created the report templates and is protective of their look; final approver. *(The "AW" in the filename may be his initials.)*

---

## 4. The Client's Business & Problem

- A **lean wealth-management practice** (3 people) with **~6 retainer clients**, all **high-net-worth ("millionaires")**; revenue from monthly fees + AUM fees. Deliberately few clients, high fees.
- For each client they produce, **quarterly (and per-meeting)**, two hand-built reports. Preparation takes **~1 day**, involves **heavy manual data entry and manual math**, and is **error-prone** (they cite repeated mistakes, especially with past assistants).
- Everything lives in **scattered tools** — Canva, Word, Excel — which the firm finds stressful. They want a **single source of truth**.

---

## 5. The Two Reports (on-screen artifacts)

### A. SACS — "Simple Automated CashFlow System" (the simpler report)
A 3-circle cashflow model:
- **Inflow** (green) = client's post-tax salary (changes rarely — raises, tax changes).
- **Outflow** (red) = a fixed monthly figure from the client's **budget/expense worksheet**, deliberately **rounded up** to create a buffer ("mental state of abundance"). An automatic bank transfer (inflow→outflow) is set up for this amount.
- **Private Reserve** (blue) = the excess (inflow − outflow), a high-yield savings account. Has a **Target** = 6+ months of expenses + all insurance deductibles.
- Worked example on screen: Inflow **$15,000**, Outflow **$12,000**, with a **$1,000 floor** per account.

### B. TCC — the "circle chart" / net-worth report (the complex one)
A personalized bubble chart of the client's entire net worth:
- **Green bubbles** = the two spouses (name, age, DOB, last-four SSN).
- **Top half = retirement accounts** (401k, IRA, Roth IRA, pension) — **cannot be joint**; subtotaled per client in a gray box.
- **Bottom half = non-retirement accounts** (brokerage, savings, checking, options/E-Trade) — **can be joint**; one subtotal box.
- **Center = a Trust**, usually funded with the client's **house** — valued each meeting via **Zillow "zestimate."**
- **Liabilities** (mortgage, auto loans) — listed with interest rate & balance, **totaled separately** (not subtracted from net worth).
- **Grand total net worth** = client-1 retirement + client-2 retirement + non-retirement + trust (liabilities shown separately).
- Each account bubble shows last-four account number, type, balance, and cash balance. **All totals are currently calculated by hand.**

---

## 6. Data Sources & Cadence

| Source | Used for | Notes / constraints |
|---|---|---|
| **Monthly expense worksheet** (Excel) | SACS outflow; agreed inflow | Client-filled; firm keeps a copy; not in any central system |
| **Pinnacle Bank** | Bank-account balances | Requested by **secure email** from clients' personal bankers ~2 days before meetings |
| **Charles Schwab** | Investment-account balances | Only **Rebecca or Andrew** authorized (compliance); per-user login, not a team login |
| **Right Capital** | Aggregated accounts, liabilities | **Unreliable** (sync delays, unlinked accounts, uses **Plaid**); login isn't even theirs — belongs to a former associate of Andrew's; **cannot be shared with an agent** |
| **Precise FP** | Client profile/questionnaire (closest thing to a CRM) | DOB, family, advisors; filled during onboarding |
| **Zillow** | House value for the trust | "Zestimate"; approximate but tracks market direction |
| Others | E-Trade (stock options, updated yearly via 409A valuation), Fidelity, Edward Jones | Held-away accounts |

Reports are generated **quarterly** once a client is established (more often during onboarding).

---

## 7. The Discussion — Key Points

- **Why automate:** Manual entry + manual math is slow (~1 day/report) and error-prone; the team is tiny and wants to **scale clients (6 → 12+) without hiring**.
- **Andrew's templates are sacred:** No visual/format changes — only a UX "paint job" (alignment, polish). Bubbles in Canva are deliberately locked so nothing shifts.
- **What can be automated easily:** SACS math and inflow/outflow logic; net-worth totals; auto-updating ages; flagging stale figures.
- **What's hard / deferred:** Live data pulls from Schwab, Pinnacle, and especially Right Capital (untrusted, third-party login). These become **v2+**, possibly via secure read-only credentials/tokens or **Plaid**, perhaps migrating clients off Right Capital.
- **Compliance is a hard constraint:** **No Google** tools (Google Data Studio explicitly rejected); must be secure. Zaki's reassurance: Sagan's AI **stores nothing for training** (unlike consumer AI). Schwab/Right Capital credential handling discussed carefully.
- **Agreed mental model:** "Build a Lego city one brick at a time" — ship one tightly-scoped agent first, then add more. ("An employee is a collection of agents.")

---

## 8. Agreed Version-1 Scope (the build)

A **secure, hosted web portal/app** that:
1. Lets the firm **add a client once** (manually or imported from Precise FP) — intake data + their list of accounts (types + last-four).
2. Provides a **"Create New Report"** button that auto-pulls the static/known data and **does all the math** via baked-in rules (Inflow − Outflow = Private Reserve; net-worth totals).
3. Shows a **checklist of missing fields** for the user to fill (data it can't yet fetch live), with **manual-override** on any value.
4. **Generates a polished PDF** — same format, better aligned — and can **export to Canva** (to move bubbles/edit) or **download directly**.
5. Centralizes everything in one place (vs scattered Canva/Word/Excel); possibly **auto-saves to the firm's Dropbox** and hosts an **SOP** reference.
   - Reports aren't stored server-side; user downloads or sends to Canva.

**Future directions (agents 2, 3, 4…):** automatic secure data pulls (Schwab/Plaid); an **onboarding agent** (emails clients the form, auto-reminders, escalates to Andrew); automated **monthly report emails** to clients; client-facing expense-worksheet link.

---

## 9. Commercial Terms (as stated by Sagan)

- **Flat fee per build = "one credit" ≈ $500** (one-time, not recurring). Client mentions having ~2 credits.
- Sagan **hosts the app**, monitors uptime, fixes bugs.
- Ongoing cost = **usage only** (data + AI tokens) at **cost + 20%** — framed as "tens of dollars/month, not hundreds."
- Tied to **Sagan membership** (monthly).

---

## 10. Action Items / Next Steps

| # | Owner | Action | Timing |
|---|---|---|---|
| 1 | **Zaki (Sagan)** | Send a **build spec** (one-liner + 3–4 bullets of exactly what will be built) by email | **By tomorrow** |
| 2 | **Rebecca / Maryam** | Review internally **with Andrew**; reply with a **"thumbs up"** to approve | After spec |
| 3 | **Sagan** | On approval, **burn 1 credit (~$500)** and start development | On approval |
| 4 | **Sagan** | Deliver a **working prototype** | **~1 week** after approval |
| 5 | **Zaki** | Connect directly with **Andrew** to walk through the agreement | "By end of week" |
| 6 | **Client** | Send Zaki a **final example PDF** (with client goal + date) for visual alignment | — |

---

## 11. Privacy / PII Notice ⚠️

The materials shown contain **partial client PII and financial data**: DOB, **last-four SSN**, account balances, salary/expense figures, brokerage/bank details, and sample-client account structures. Although the on-screen files were described as "cleared" samples, treat the video and all extracted artifacts as **confidential**. All processing in this analysis was performed **locally**; nothing was transmitted off-machine.

---

## 12. Methodology

1. **Probe** — `ffprobe` for streams/duration/metadata.
2. **Visual overview** — `ffmpeg` contact-sheet (1 frame / 120 s) to map the call's arc.
3. **Detail** — full-resolution frame extraction at points of interest; region **crop + lanczos upscale** to make document text legible.
4. **Audio** — extracted 16 kHz mono WAV; transcribed locally with **faster-whisper** (`small.en`, CPU/int8); 575 timestamped segments.

Tooling installed for this task: **FFmpeg 8.1.1** (winget) and **faster-whisper 1.2.1** (pip).

---

## 13. Appendix — Extracted Artifacts

All under `C:\Users\tbeng\Downloads\_aw_test_frames\`:

- `contact_sheet.png` — 28-frame overview montage
- `fig_sacs_client_example.png` — SACS Client Example (Inflow/Outflow/Private Reserve)
- `fig_cashflow_flowchart.png` — `tcc_sample_client` net-worth chart
- `crop_doc_word_2700.png`, `crop_doc_gdoc_1860.png` — legible "Data Point List" document
- `full_0600s.png`, `full_1140s.png`, `full_1380s.png` — full-frame screen captures
- `audio16k.wav` — extracted audio
- `transcript.txt` / `transcript.srt` — full timestamped transcript (575 segments)
