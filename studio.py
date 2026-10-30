"""CLI production blueprint for the India + Global news explainer channel.

No live news research or MP4 rendering happens in this module. It prepares
an evidence-led editorial plan and marks missing verification clearly.
"""
from pathlib import Path
import json
import re


def clean(text):
    return re.sub(r"\\s+", " ", text.strip()).rstrip(".!?")


def score_topic(topic, demand=70, growth=65, curiosity=80, competition=55, visuals=80, depth=80, monetization=75):
    """Heuristic placeholder only; these defaults are not measured market data."""
    score = round(demand*.18 + growth*.17 + curiosity*.22 + competition*.10 + visuals*.12 + depth*.13 + monetization*.08)
    return {"topic": topic, "score": score, "verdict": "HEURISTIC ONLY — validate with real audience data"}


def build_package(idea, duration=10, shorts=5):
    topic = clean(idea)
    if not topic:
        raise ValueError("A specific news topic is required.")

    titles = [
        f"{topic}: What Happened and Why It Matters",
        f"{topic} Explained: Facts, Context and What Comes Next",
        f"What {topic} Could Mean — The Full Story",
        f"{topic}: The Key Details You Need to Understand",
        f"Inside the Story: {topic}",
    ]
    beats = [
        ("Lead", "State the confirmed development, date and location. Explain why it matters now."),
        ("Facts", "Separate confirmed information from allegations, estimates and early reports."),
        ("Timeline", "Explain what happened first, what changed and what is known now."),
        ("People affected", "Identify who is affected and explain the real-world consequences."),
        ("Background", "Give only the context needed to understand the development."),
        ("Evidence", "Show primary documents, official statements, attributable reporting or data."),
        ("Explanation", "Explain the mechanism in plain English and define unfamiliar terms."),
        ("What it does not mean", "Correct likely misunderstandings without overstating certainty."),
        ("Perspectives", "Attribute relevant responses and include material disagreement."),
        ("What happens next", "Identify the next confirmed decision, deadline or data release."),
        ("Unknowns", "Clearly label unanswered questions and facts not yet verified."),
        ("Takeaway", "Summarise significance without giving personal financial or legal advice."),
    ]
    count = max(12, min(24, duration * 2))
    total = duration * 60
    base, remainder = divmod(total, count)
    scenes = []
    for i in range(count):
        beat, goal = beats[i % len(beats)]
        scenes.append({
            "scene": i + 1,
            "duration_seconds": base + (1 if i < remainder else 0),
            "beat": beat,
            "narration_goal": f"[ADD VERIFIED FACTS] {goal} Topic: {topic}. Never invent facts, figures or quotes.",
            "visual_goal": f"Story-specific evidence visual for {topic}: original chart, timeline, map, document close-up or rights-cleared footage. Beat: {beat}.",
            "edit": "Advance the story with purposeful visual changes; use readable mobile-safe captions and concise labels.",
            "audio": "Narration stays clear and dominant; original/licensed music is subtle and automatically ducked under speech.",
        })

    script = f"""EDITORIAL SCRIPT PLAN — NOT VERIFIED NEWS COPY

TOPIC: {topic}

OPEN (0:00–0:20)
Lead with the most important confirmed development, its date and why viewers should care.

WHAT HAPPENED
[Insert the confirmed event in 2–3 plain-English sentences.]
[Name the primary source and its publication/update time.]

WHY IT MATTERS
[Explain the real-world consequence and who is affected.]
[Explain necessary background in simple language.]

WHAT THE EVIDENCE SHOWS
[Add attributable facts, data or official statements.]
[Separate confirmed facts, estimates, allegations and analysis.]

WHAT HAPPENS NEXT
[State the next confirmed milestone and what remains unknown.]

CLOSE
Give a concise evidence-based takeaway and promise the next verified update.

EDITORIAL GATE
This is a structure, not a completed factual script. Fill every bracket from reliable sources and complete human review before publication.
"""
    angles = [
        "The one confirmed fact that changes the story",
        "Why this development matters",
        "The timeline in under a minute",
        "What is confirmed — and what is not",
        "What happens next",
    ]
    shorts_out = []
    for i in range(shorts):
        angle = angles[i % len(angles)]
        shorts_out.append({
            "title": f"{topic}: {angle}",
            "hook": f"Here is the key detail about {topic} that puts the headline in context.",
            "angle": angle,
            "structure": "Hook → one verified fact → plain-English explanation → source label → useful next step.",
            "visual_plan": "Vertical 9:16; one clear visual per idea; readable captions; original charts or rights-cleared footage.",
            "cta": "Follow for the next verified update and the full explanation.",
        })

    return {
        "channel_direction": "India + Global News Explained: original, source-led reporting that explains what happened, why it matters, who is affected and what happens next.",
        "editorial_status": "DRAFT — source verification and human review required",
        "idea": topic,
        "recommended_duration_minutes": duration,
        "hook": f"What changed, who is affected, and what should viewers understand about {topic}? This episode separates confirmed facts from uncertainty and explains the context.",
        "titles": titles,
        "description_template": f"{topic} explained: what happened, why it matters, the evidence, and what comes next. Add a concise factual summary, the reporting date, and source links before publishing.",
        "thumbnail_concepts": [
            "One recognisable subject, one clear focal point and 3–5 factual words.",
            "A source-based timeline or comparison with a single important number.",
            "A clean map/document/chart treatment; no unrelated stock imagery or exaggerated claims.",
        ],
        "script": script,
        "long_form_structure": scenes,
        "shorts": shorts_out,
        "source_requirements": [
            "At least one primary source where available.",
            "A second independent reliable source for consequential or disputed claims.",
            "Record source URL, publisher, publication time and last-checked time.",
            "Do not publish unsupported breaking claims; label developing information clearly.",
        ],
        "quality_gate": [
            "The script explains the story; it does not merely read headlines or article text.",
            "Every factual claim is sourced and checked; dates, names and numbers are verified.",
            "Facts, allegations, estimates and analysis are clearly distinguished.",
            "Visuals directly illustrate the story and have commercial-use rights.",
            "Music and sound effects have documented commercial-use rights.",
            "Captions are synchronised and readable on a phone.",
            "Title and thumbnail accurately represent the episode.",
            "Human editorial approval is required before upload.",
        ],
    }


def save_package(package, output="output"):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "production_package.json"
    path.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


if __name__ == "__main__":
    print(save_package(build_package("A major India or global news development that needs clear explanation")))
