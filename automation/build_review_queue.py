#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
RAW_FILE = ROOT / "raw_feed_items.json"
JSON_OUT = ROOT / "review_queue.json"
MD_OUT = ROOT / "review_queue.md"
README_OUT = ROOT / "README.md"

CATEGORIES = ["AI Guide", "Creator Workflows", "Future Living", "Cybersecurity"]

SITE_ARTICLES = {
    "AI Guide": [
        "gemini-india-guide.html",
        "best-ai-coding-prompting-guide-2026.html",
        "best-ai-image-editing-tools-2026.html",
        "best-ai-office-productivity-tools-2026.html",
        "best-ai-powerpoint-presentation-tools-2026.html",
        "best-ai-video-editing-tools-2026.html",
        "best-ai-writing-assistants-2026.html",
        "ai-tools-drafting-planning-scheduling.html",
        "human-ai-prompts.html",
    ],
    "Creator Workflows": [
        "creator-workflow-month-1-content-foundation.html",
        "creator-workflow-month-2-editing-publishing-system.html",
        "filmora-100-tiktoks-in-1-hour-workflow.html",
        "hidden-iphone-camera-settings-dslr-look.html",
        "best-free-lightroom-mobile-alternatives-2026.html",
    ],
    "Future Living": [
        "smart-home-beginners-guide-2026.html",
        "smart-home-ecosystems-2026.html",
        "best-smart-home-routines-automation-ideas-2026.html",
        "best-smart-home-security-devices-2026.html",
        "best-smart-home-sensors-2026.html",
        "best-smart-lighting-systems-2026.html",
        "best-smart-thermostats-climate-automation-2026.html",
    ],
    "Cybersecurity": [
        "cybersecurity-checklist.html",
    ],
}

CATEGORY_KEYWORDS = {
    "AI Guide": ["ai", "model", "llm", "chatgpt", "gemini", "copilot", "automation", "agent"],
    "Creator Workflows": ["creator", "editing", "video", "camera", "youtube", "workflow", "filmora", "photos", "adobe"],
    "Future Living": ["home", "smart", "lighting", "security camera", "appliance", "thermostat", "robot", "wearable"],
    "Cybersecurity": ["security", "cyber", "breach", "phishing", "malware", "ransomware", "vulnerability", "patch", "cisa"],
}

UNSPLASH_THEMES = {
    "AI Guide": "artificial intelligence workstation interface",
    "Creator Workflows": "video editing creator desk setup",
    "Future Living": "modern smart home interior automation",
    "Cybersecurity": "cybersecurity network operations center",
}

ANGLE_TEXT = {
    "AI Guide": "Explain what changed, who benefits, and which real-world tasks this affects right now.",
    "Creator Workflows": "Translate the update into a practical workflow gain, time saving, or creator tool decision.",
    "Future Living": "Focus on practical usefulness, household convenience, setup friction, and cost-to-value.",
    "Cybersecurity": "Focus on user risk, what should be checked now, and the plain-English defensive takeaway.",
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text).strip("-")
    return text[:80].rstrip("-")


def clean_domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def choose_category(title: str, summary: str, hint: str) -> str:
    blob = f"{title} {summary}".lower()
    scores = {category: 0 for category in CATEGORIES}
    if hint in scores:
        scores[hint] += 2
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in blob:
                scores[category] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else (hint if hint in CATEGORIES else "AI Guide")


def compute_score(title: str, summary: str, source: str, category: str) -> float:
    score = 0.35
    text = f"{title} {summary}".lower()
    keyword_hits = sum(1 for kw in CATEGORY_KEYWORDS[category] if kw in text)
    score += min(keyword_hits * 0.08, 0.32)
    if len(summary.split()) >= 18:
        score += 0.1
    if any(token in text for token in ["launch", "update", "new", "release", "guide", "tips", "security"]):
        score += 0.08
    if source.lower() in {"openai news", "google ai blog", "cisa news", "krebsonsecurity", "bleepingcomputer"}:
        score += 0.05
    return round(min(score, 0.98), 2)


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = slugify(item.get("title", ""))
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def build_item(item: dict[str, Any]) -> dict[str, Any]:
    title = item.get("title", "").strip()
    summary = item.get("summary", "").strip() or "Recent update worth reviewing for SignalBytes."
    category = choose_category(title, summary, item.get("category_hint", ""))
    slug = slugify(title)
    score = compute_score(title, summary, item.get("source", ""), category)
    why = summary if len(summary.split()) <= 38 else " ".join(summary.split()[:38]) + "…"
    return {
        "title": title,
        "source": item.get("source", ""),
        "source_domain": clean_domain(item.get("link", "")),
        "link": item.get("link", ""),
        "published": item.get("published", ""),
        "category": category,
        "score": score,
        "suggested_slug": slug,
        "summary": why,
        "why_it_matters": f"{why} {ANGLE_TEXT[category]}",
        "editorial_angle": ANGLE_TEXT[category],
        "unsplash_query": UNSPLASH_THEMES[category],
        "related_internal_links": SITE_ARTICLES[category][:3],
        "status": "manual_pick",
    }


def load_raw() -> list[dict[str, Any]]:
    if not RAW_FILE.exists():
        return []
    payload = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    return payload.get("items", [])


def build_markdown(items: list[dict[str, Any]], generated_at: str) -> str:
    lines = [
        "# SignalBytes Review Queue",
        "",
        f"Generated: {generated_at}",
        "",
        "Use this file in GitHub only as a readable topic shortlist.",
        "Pick one topic you like, then ask AI for the full HTML article and paste it into the repo manually.",
        "",
        "---",
        "",
    ]
    if not items:
        lines.append("No recent topics were found in the current feed fetch.")
        lines.append("")
        return "\n".join(lines)

    for idx, item in enumerate(items, start=1):
        lines.extend([
            f"## {idx}. {item['title']}",
            "",
            f"- **Category:** {item['category']}",
            f"- **Source:** {item['source']} ({item['source_domain']})",
            f"- **Published:** {item['published'] or 'Unknown'}",
            f"- **Score:** {item['score']}",
            f"- **Suggested slug:** `{item['suggested_slug']}`",
            f"- **Suggested image theme:** `{item['unsplash_query']}`",
            f"- **Related internal links:** {', '.join(item['related_internal_links'])}",
            "",
            f"**Summary**  ",
            f"{item['summary']}",
            "",
            f"**Why it matters**  ",
            f"{item['why_it_matters']}",
            "",
            f"**Read source**  ",
            f"{item['link']}",
            "",
            "---",
            "",
        ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build readable SignalBytes review queue files.")
    parser.add_argument("--max-items", type=int, default=18)
    parser.add_argument("--min-score", type=float, default=0.45)
    args = parser.parse_args()

    raw_items = dedupe(load_raw())
    processed = [build_item(item) for item in raw_items]
    processed.sort(key=lambda x: (x["score"], x.get("published", "")), reverse=True)
    processed = [item for item in processed if item["score"] >= args.min_score][: args.max_items]

    generated_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "generated_at": generated_at,
        "item_count": len(processed),
        "items": processed,
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    MD_OUT.write_text(build_markdown(processed, generated_at), encoding="utf-8")
    README_OUT.write_text(
        "# SignalBytes Automation\n\n"
        "This folder contains a lightweight topic discovery system for manual editorial use.\n\n"
        "- `fetch_rss.py` downloads recent feed items into `raw_feed_items.json`.\n"
        "- `build_review_queue.py` turns those items into `review_queue.json` and a readable `review_queue.md`.\n\n"
        "Recommended workflow:\n\n"
        "1. Run the **Review Queue Refresh** GitHub Action.\n"
        "2. Open `automation/review_queue.md` in the repo.\n"
        "3. Pick one topic you genuinely want to cover.\n"
        "4. Ask AI for the full HTML article.\n"
        "5. Paste that article into the repo manually.\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(processed)} items to {JSON_OUT} and {MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
