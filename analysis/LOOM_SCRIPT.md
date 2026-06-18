# Loom Walkthrough Script — "How we approached your portal"

**Target:** under 2 minutes (~250 words of narration; the on-screen clicks fill the rest).
**Audience:** the client (the advisory firm). **Presenter:** Sagan.
**Goal:** show the working portal — the live demo is the proof — and close with a simple ask.

---

## Before you record (≈2 min of setup)

1. Start the two servers (two terminals):
   ```powershell
   cd C:\Dev\Solutions\aw-client-report-portal
   .\.venv\Scripts\python.exe run_sandbox.py     # provider sandbox :5050 (powers the auto-fill)
   ```
   ```powershell
   cd C:\Dev\Solutions\aw-client-report-portal
   .\.venv\Scripts\python.exe run.py             # portal :5000
   ```
2. In the browser, open **http://127.0.0.1:5000**, sign in as `owner@firm.test` / `changeme123`,
   and stop on the **Clients** list — that's your opening shot.
3. Full-screen the browser, hide the bookmarks bar, close other tabs/notifications.
4. Do **one silent dry-run** following the script to confirm it lands under 2:00 and the auto-fill fires.

---

## The script

**[0:00–0:12 · webcam / portal home]**
> "Hi [Rebecca, Maryann] — thanks again for walking me through your process. Here's a quick
> two-minute look at what we built and how we approached it."

**[0:12–0:30 · talk over the Clients list]**
> "You told us one client report eats the better part of a day — pulling balances from Pinnacle,
> Schwab, RightCapital and Zillow, then doing the math by hand in Canva and Word. Our whole goal
> was to take that day down to minutes — without changing how Andrew's reports look."

**[0:30–0:48 · gesture at the portal]**
> "So we built one secure portal. Your client data lives in one place, your templates stay exactly
> as they are, and it's all locked down — your data stays yours. And we built it one brick at a
> time, starting with the report you run most."

**[0:48–1:25 · click *Generate report* → the form auto-fills]**
> "Here's the part I'm excited about. I pick a client, hit Generate report — and watch: it pulls
> the balances from your connected accounts automatically, and tells me exactly where each number
> came from. Anything it can't reach, it flags for you to type. One quick entry… and generate."

**[1:25–1:42 · the SACS + TCC PDFs on screen]**
> "There's your cash-flow and net-worth reports — same format you use today, the math done for you,
> everything aligned. From here, download them, email them to the client, or drop them straight
> into Dropbox."

**[1:42–1:55 · back to webcam]**
> "That's version one. The next bricks could pull even more automatically, or handle new-client
> onboarding. Have a look — and just reply with a thumbs-up when you're ready for us to roll it
> out. Thanks!"

---

## Delivery tips

- **Do the clicks while you talk.** The auto-fill animation and the PDF reveal are the "wow" —
  pause and let them breathe instead of narrating over them.
- **Lead with the demo, not features.** It's already loaded; the proof is live.
- **Open/close on webcam, middle on screen-share** (Loom switches naturally).
- If you run long, shorten the 0:12 list to *"from your banks and custodians."*
- The single most persuasive beat is the form **auto-filling ~9 fields from the providers** — give
  it a full second of silence.

---

## How to record & send (Loom)

1. Loom desktop app (or Chrome extension) → **Screen + Cam** → record the **browser window**
   (not the whole desktop), cam bubble in a corner.
2. Dry-run once silently, then record — **click slowly**. One take is fine; Loom lets you restart instantly.
3. **Trim** dead air off the start/end in Loom.
4. Copy the **share link** and paste it into your email to the client (Loom also gives an embed + thumbnail).

> Note: Loom records your screen + voice locally — the portal running on `localhost` is all you need
> to show. No deployment required just to record the walkthrough.
