# SignalBytes Automation

This folder contains a lightweight topic discovery system for manual editorial use.

- `fetch_rss.py` downloads recent feed items into `raw_feed_items.json`.
- `build_review_queue.py` turns those items into `review_queue.json` and a readable `review_queue.md`.

Recommended workflow:

1. Run the **Review Queue Refresh** GitHub Action.
2. Open `automation/review_queue.md` in the repo.
3. Pick one topic you genuinely want to cover.
4. Ask AI for the full HTML article.
5. Paste that article into the repo manually.
