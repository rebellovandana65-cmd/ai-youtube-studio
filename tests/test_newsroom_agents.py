from newsroom.agents import ChiefAgent, DeduplicationAgent, Story, parse_rss

SAMPLE = """<?xml version="1.0"?>
<rss version="2.0"><channel>
<item><title>India announces a new programme</title><link>https://example.com/a</link><source>Example News</source><pubDate>Sat, 31 Oct 2026 10:00:00 GMT</pubDate><description>Officials announced a programme.</description></item>
<item><title>India announces a new programme</title><link>https://example.com/b</link><source>Other News</source><pubDate>Sat, 31 Oct 2026 10:05:00 GMT</pubDate></item>
</channel></rss>"""


def test_parse_rss_extracts_source_and_date():
    stories = parse_rss(SAMPLE, "india")
    assert len(stories) == 2
    assert stories[0].publisher == "Example News"
    assert stories[0].url == "https://example.com/a"
    assert stories[0].published_at


def test_dedupe_removes_same_headline():
    stories = parse_rss(SAMPLE, "india")
    assert len(DeduplicationAgent().run(stories)) == 1


def test_chief_keeps_regions_separate_and_records_feed_failure():
    xml = SAMPLE.replace("India announces a new programme", "Global leaders meet")
    def fake_fetch(url, region):
        if region == "global":
            raise TimeoutError("test timeout")
        return parse_rss(SAMPLE, region)
    report = ChiefAgent().run(fetcher=fake_fetch, per_region=8)
    assert report["status"] == "PARTIAL_FAILURE"
    assert report["india"]["story_count"] == 1
    assert report["global"]["story_count"] == 0
    assert report["errors"][0]["agent"] == "global"
    assert report["india"]["stories"][0]["status"] == "READY_FOR_HUMAN_SOURCE_CHECK"
