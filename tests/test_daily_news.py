from scripts.build_daily_news import clean, wrap
from PIL import Image, ImageDraw, ImageFont


def test_clean_removes_html_and_collapses_whitespace():
    assert clean("<b>Breaking</b>   news &amp; updates") == "Breaking news & updates"


def test_clean_handles_empty_values():
    assert clean(None) == ""


def test_wrap_keeps_words_in_lines():
    image = Image.new("RGB", (400, 100))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    lines = wrap(draw, "one two three four five", font, 80)
    assert len(lines) > 1
    assert " ".join(lines).split() == ["one", "two", "three", "four", "five"]
