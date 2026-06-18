"""Convert a Claude Code session .jsonl transcript into a readable Markdown conversation.

The dialogue (human prompts + Claude's replies) is included in full; tool calls are shown
as compact one-liners and tool results are truncated (they are machine I/O, not 'the
interaction'). Internal reasoning (thinking) is omitted.
"""
import json
import re

SRC = r"C:\Users\tbeng\.claude\projects\C--Dev-Solutions-com-bhengubv\ea2be807-3eea-41c7-85d1-9f2598289011.jsonl"
OUT = r"C:\Users\tbeng\Downloads\SAGAN_AW_Portal_Conversation.md"

SYS_MARKERS = ("<task-notification", "[SYSTEM NOTIFICATION", "<system-reminder", "Caveat:")
RESULT_TRUNC = 400


def msg_blocks(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return [{"type": "text", "text": c}]
    return [b for b in (c or []) if isinstance(b, dict)]


def is_system_text(t):
    s = (t or "").lstrip()
    return any(m in s[:80] for m in SYS_MARKERS)


def one_line(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def truncate(s, n):
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f" …[+{len(s)-n} chars]"


def result_to_text(content):
    if isinstance(content, str):
        return content
    parts = []
    for b in (content or []):
        if isinstance(b, dict):
            if b.get("type") == "text":
                parts.append(b.get("text", ""))
            elif b.get("type") == "image":
                parts.append("[image]")
            else:
                parts.append(b.get("type", ""))
        else:
            parts.append(str(b))
    return " ".join(p for p in parts if p)


def tool_desc(inp):
    if not isinstance(inp, dict):
        return one_line(str(inp))
    for k in ("description", "command", "file_path", "pattern", "skill", "prompt",
              "name", "title", "query", "url"):
        if inp.get(k):
            return one_line(str(inp[k]))
    return one_line(truncate(inp, 160))


events = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass

out, n_user, n_tools = [], 0, 0
title = next((e.get("aiTitle") for e in events if e.get("type") == "ai-title" and e.get("aiTitle")), None)

out.append("# Conversation Transcript")
out.append("")
out.append(f"**Session:** `ea2be807-3eea-41c7-85d1-9f2598289011`  ")
if title:
    out.append(f"**Title:** {title}  ")
out.append("**Project:** SAGAN AW Client Portal  ")
out.append("**Exported:** 2026-06-18")
out.append("")
out.append("> The human/Claude dialogue is verbatim. Tool calls are shown as compact lines "
          "(`🔧 Tool — summary`) and tool results are truncated — they are machine I/O, not part "
          "of the conversation. Internal reasoning is omitted.")
out.append("")

for o in events:
    t = o.get("type")
    if t not in ("user", "assistant"):
        continue
    blks = msg_blocks(o.get("message") or {})

    if t == "user":
        results = [b for b in blks if b.get("type") == "tool_result"]
        texts = [b for b in blks if b.get("type") == "text"]
        if results:
            for b in results:
                s = one_line(result_to_text(b.get("content")))
                if s:
                    out.append(f"<sub>↳ result: {truncate(s, RESULT_TRUNC)}</sub>")
                    out.append("")
            continue
        joined = " ".join(b.get("text", "") for b in texts)
        if texts and (o.get("promptSource") or not is_system_text(joined)):
            out.append("")
            out.append("---")
            out.append("")
            out.append("## 🧑 User")
            out.append("")
            for b in texts:
                if not is_system_text(b.get("text", "")):
                    out.append(b.get("text", ""))
            out.append("")
            n_user += 1
        elif "task-notification" in joined or "SYSTEM NOTIFICATION" in joined:
            out.append("<sub>⚙ (background task notification)</sub>")
            out.append("")
        continue

    # assistant
    texts = [b for b in blks if b.get("type") == "text"]
    tools = [b for b in blks if b.get("type") == "tool_use"]
    if texts and any(b.get("text", "").strip() for b in texts):
        out.append("## 🤖 Claude")
        out.append("")
        for b in texts:
            if b.get("text", "").strip():
                out.append(b["text"])
        out.append("")
    for b in tools:
        n_tools += 1
        out.append(f"<sub>🔧 **{b.get('name')}** — {truncate(tool_desc(b.get('input')), 200)}</sub>")
        out.append("")

# header stats — place within the metadata block (before the Exported line)
out.insert(5, f"**Turns:** {n_user} user prompts · {n_tools} tool calls  ")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"wrote {OUT}")
print(f"user prompts: {n_user}, tool calls: {n_tools}, total lines: {len(out)}")
