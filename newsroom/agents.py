"""Deterministic newsroom agents. No paid model/API is required for this first milestone."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from typing import Iterable
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


@dataclass
class Story:
    region: str
    title: str
    url: str
    publisher: str
    published_at: str
    summary: str
    story_id: str
    verification_status: str = "PENDING_HUMAN_VERIFICATION"
    source_count: int = 1


def google_news_rss(query: str, region: str) -> str:
    if region == "india":
        params = "hl=en-IN&gl=IN&ceid=IN:en"
    else:
        params = "hl=en-US&gl=US&ceid=US:en"
    return f"https://news.google.com/rss/search?q={quote(query)}&{params}"


FEEDS = {
    "india": [google_news_rss("India top news when:1d", "india"),
              google_news_rss("India politics economy technology when:1d", "india")],
    "global": [google_news_rss("world top news when:1d", "global"),
               google_news_rss("world politics economy technology when:1d", "global")],
}


def _text(node: ET.Element, path: str) -> str:
    child = node.find(path)
    return (child.text or "").strip() if child is not None else ""


def parse_rss(xml_text: str, region: str) -> list[Story]:
    root = ET.fromstring(xml_text)
    stories: list[Story] = []
    for item in root.findall("./channel/item"):
        title = _text(item, "title")
        link = _text(item, "link")
        if not title or not link:
            continue
        publisher = _text(item, "source") or "Publisher not supplied"
        published = _text(item, "pubDate")
        try:
            dt = parsedate_to_datetime(published)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            published = dt.astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError, OverflowError):
            published = ""
        summary = _text(item, "description")
        key = " ".join(title.casefold().split())
        story_id = sha256((region + "|" + key).encode("utf-8")).hexdigest()[:16]
        stories.append(Story(region, title, link, publisher, published, summary, story_id))
    return stories


def fetch_feed(url: str, region: str, timeout: int = 20) -> list[Story]:
    request = Request(url, headers={"User-Agent": "NewsroomResearchBot/1.0"})
    with urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8", errors="replace")
    return parse_rss(payload, region)


class IndiaResearchAgent:
    name = "india_research"
    def run(self, fetcher=fetch_feed) -> list[Story]:
        return [story for feed in FEEDS["india"] for story in fetcher(feed, "india")]


class GlobalResearchAgent:
    name = "global_research"
    def run(self, fetcher=fetch_feed) -> list[Story]:
        return [story for feed in FEEDS["global"] for story in fetcher(feed, "global")]


class DeduplicationAgent:
    name = "deduplication"
    def run(self, stories: Iterable[Story]) -> list[Story]:
        seen: set[str] = set()
        result = []
        for story in stories:
            key = " ".join(story.title.casefold().split())
            if key and key not in seen:
                seen.add(key)
                result.append(story)
        return result


class VerificationAgent:
    """Checks metadata completeness; it does NOT claim a story is factually verified."""
    name = "verification"
    def run(self, stories: Iterable[Story]) -> list[Story]:
        for story in stories:
            story.verification_status = (
                "READY_FOR_HUMAN_SOURCE_CHECK"
                if story.title and story.url.startswith("http") and story.publisher
                else "INSUFFICIENT_SOURCE_METADATA"
            )
        return list(stories)


class ScriptAgent:
    name = "script"
    def run(self, stories: list[Story], limit: int = 8) -> dict:
        selected = stories[:limit]
        rundown = []
        for index, story in enumerate(selected, 1):
            rundown.append({
                "order": index,
                "headline": story.title,
                "region": story.region,
                "publisher": story.publisher,
                "source_url": story.url,
                "published_at": story.published_at,
                "summary_from_feed": story.summary,
                "status": story.verification_status,
                "narration_draft": (
                    f"Here is a developing story: {story.title}. "
                    f"This report is based on coverage from {story.publisher}. "
                    "The details should be checked against the original report and an independent source before narration."
                ),
            })
        return {"story_count": len(rundown), "stories": rundown}


class ChiefAgent:
    """Coordinates the newsroom. Each region is isolated so one feed failure won't erase the other."""
    def __init__(self):
        self.india = IndiaResearchAgent()
        self.global_news = GlobalResearchAgent()
        self.dedupe = DeduplicationAgent()
        self.verify = VerificationAgent()
        self.script = ScriptAgent()

    def run(self, fetcher=fetch_feed, per_region: int = 8) -> dict:
        errors = []
        collected: list[Story] = []
        for label, agent in (("india", self.india), ("global", self.global_news)):
            try:
                collected.extend(agent.run(fetcher=fetcher))
            except Exception as exc:  # recorded, never silently treated as a successful empty feed
                errors.append({"agent": label, "error": f"{type(exc).__name__}: {exc}"})
        unique = self.dedupe.run(collected)
        checked = self.verify.run(unique)
        india = [s for s in checked if s.region == "india"]
        global_stories = [s for s in checked if s.region == "global"]
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "system": "Newsroom Agent Network - Foundation",
            "status": "PARTIAL_FAILURE" if errors else "RESEARCH_COMPLETE_REQUIRES_EDITORIAL_REVIEW",
            "agents": ["india_research", "global_research", "deduplication", "verification", "script", "chief"],
            "errors": errors,
            "india": self.script.run(india, per_region),
            "global": self.script.run(global_stories, per_region),
            "editorial_rules": [
                "A feed headline is a lead, not proof that every claim is true.",
                "Do not publish until an editor checks the original source and a second independent source.",
                "Do not invent quotes, numbers, causes, motives, dates or missing context.",
                "Use rights-cleared footage, images, music and graphics only.",
                "If sources conflict or details are developing, label the uncertainty and hold publication."
            ],
        }


def story_to_dict(story: Story) -> dict:
    return asdict(story)
