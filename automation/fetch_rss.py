#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Any
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
FEEDS_FILE = ROOT / "feeds.json"
RAW_FILE = ROOT / "raw_feed_items.json"
UA = "SignalBytesReviewBot/1.0 (+https://signalbytes.in)"


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", unescape(text)).strip()
    return text


def first_text(parent: ET.Element, names: list[str]) -> str:
    for name in names:
        elem = parent.find(name)
        if elem is not None and elem.text:
            return elem.text.strip()
    return ""


def first_text_ns(parent: ET.Element, names: list[str]) -> str:
    for candidate in parent.iter():
        tag = candidate.tag.split("}")[-1] if "}" in candidate.tag else candidate.tag
        if tag in names and (candidate.text and candidate.text.strip()):
            return candidate.text.strip()
    return ""


def parse_datetime(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    fmts = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except ValueError:
            continue
    return value


def fetch_xml(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=25) as r:
        return r.read()


def parse_feed(xml_bytes: bytes, source_name: str, category_hint: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_bytes)
    items: list[dict[str, Any]] = []
    root_tag = root.tag.split("}")[-1]

    if root_tag == "rss" or root.find("channel") is not None:
        channel = root.find("channel") or root
        for item in channel.findall("item"):
            title = first_text(item, ["title"]) or first_text_ns(item, ["title"])
            link = first_text(item, ["link"]) or first_text_ns(item, ["link"])
            guid = first_text(item, ["guid"]) or link
            summary = (
                first_text(item, ["description"]) or first_text_ns(item, ["description", "encoded", "summary"])
            )
            published = parse_datetime(
                first_text(item, ["pubDate"]) or first_text_ns(item, ["published", "updated"])
            )
            if title and link:
                items.append({
                    "title": strip_html(title),
                    "link": link.strip(),
                    "summary": strip_html(summary),
                    "published": published,
                    "source": source_name,
                    "category_hint": category_hint,
                    "id": guid.strip() if guid else link.strip(),
                })
    else:  # atom-ish
        for entry in root.iter():
            if entry.tag.split("}")[-1] != "entry":
                continue
            title = first_text_ns(entry, ["title"])
            link = ""
            for child in entry:
                tag = child.tag.split("}")[-1]
                if tag == "link":
                    href = child.attrib.get("href", "")
                    rel = child.attrib.get("rel", "alternate")
                    if href and rel in {"alternate", ""}:
                        link = href
                        break
            summary = first_text_ns(entry, ["summary", "content"])
            published = parse_datetime(first_text_ns(entry, ["published", "updated"]))
            entry_id = first_text_ns(entry, ["id"]) or link
            if title and link:
                items.append({
                    "title": strip_html(title),
                    "link": link.strip(),
                    "summary": strip_html(summary),
                    "published": published,
                    "source": source_name,
                    "category_hint": category_hint,
                    "id": entry_id.strip() if entry_id else link.strip(),
                })
    return items


def is_recent(published: str, days: int) -> bool:
    if not published:
        return True
    try:
        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt >= datetime.now(timezone.utc) - timedelta(days=days)
    except ValueError:
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch RSS/Atom items for SignalBytes topic review.")
    parser.add_argument("--limit-per-feed", type=int, default=12)
    parser.add_argument("--days", type=int, default=10)
    args = parser.parse_args()

    config = json.loads(FEEDS_FILE.read_text(encoding="utf-8"))
    out: list[dict[str, Any]] = []
    errors: list[str] = []

    for feed in config.get("feeds", []):
        try:
            xml = fetch_xml(feed["url"])
            items = parse_feed(xml, feed["name"], feed.get("category_hint", ""))
            recent_items = [x for x in items if is_recent(x.get("published", ""), args.days)]
            out.extend(recent_items[: args.limit_per_feed])
        except (URLError, HTTPError, ET.ParseError, TimeoutError, KeyError) as exc:
            errors.append(f"{feed.get('name', 'Unknown')}: {exc}")

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "item_count": len(out),
        "errors": errors,
        "items": out,
    }
    RAW_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(out)} items to {RAW_FILE}")
    if errors:
        print("Feed warnings:")
        for error in errors:
            print(f"- {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
