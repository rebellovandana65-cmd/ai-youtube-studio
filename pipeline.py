"""News explainer production blueprint.

This module creates an editorial structure, not verified reporting. Every
claim, date, number, quote and source must be supplied and checked before
rendering or publication.
"""
try:
    from .models import GenerateRequest, ProductionPackage, Scene
except ImportError:
    from models import GenerateRequest, ProductionPackage, Scene


def build_package(req: GenerateRequest) -> ProductionPackage:
    topic = " ".join(req.idea.strip().split()).rstrip(".!?")
    if not topic:
        raise ValueError("A specific news topic is required.")

    titles = [
        f"{topic}: What Happened and Why It Matters",
        f"{topic} Explained: The Facts, Context and What Comes Next",
        f"What {topic} Could Mean — The Full Story",
        f"{topic}: The Key Details You Need to Understand",
        f"Inside the Story: {topic}",
    ]
    hook = (
        f"What changed, who is affected, and what should people understand "
        f"about {topic}? Here are the verified facts, the context behind them, "
        "and what remains uncertain."
    )
    thumbnail_concepts = [
        "One verified subject or location, a clear focal point, and a short factual headline (3–5 words).",
        "A clean before/after, timeline, or comparison graphic based only on sourced facts.",
        "A strong subject image with one meaningful number or question; no clutter or exaggerated claims.",
    ]

    beats = [
        ("The lead", "State the verified development, date and location. Explain why it is being reported now."),
        ("The confirmed facts", "Separate confirmed information from claims, estimates and early reports."),
        ("The timeline", "Show what happened first, what changed and what is known now."),
        ("The people affected", "Explain the groups, institutions or communities directly affected."),
        ("The background", "Give only the history needed to understand this development."),
        ("The evidence", "Show the primary document, official statement, data or attributable reporting."),
        ("The explanation", "Explain the mechanism in plain English; define unfamiliar terms."),
        ("What it does not mean", "Correct the most likely misunderstanding without overstating certainty."),
        ("Different perspectives", "Attribute relevant responses and include material disagreement."),
        ("What happens next", "List the next confirmed decision, deadline, data release or event to watch."),
        ("What remains unknown", "Clearly label unanswered questions and information not yet verified."),
        ("The takeaway", "Summarise the practical significance without giving personal financial or legal advice."),
    ]

    scene_count = max(12, min(24, req.duration_minutes * 2))
    total_seconds = req.duration_minutes * 60
    base = total_seconds // scene_count
    remainder = total_seconds % scene_count
    scenes = []
    for i in range(scene_count):
        beat, instruction = beats[i % len(beats)]
        scenes.append(Scene(
            number=i + 1,
            duration_seconds=base + (1 if i < remainder else 0),
            purpose=beat,
            narration=(
                f"[EDITORIAL DRAFT — add verified, attributed facts only] "
                f"{instruction} Topic: {topic}. Do not invent figures, quotes, motives or outcomes."
            ),
            visual_prompt=(
                f"News explainer visual for: {topic}. Beat: {beat}. Choose the evidence-led visual "
                "that fits this specific fact: original chart, labelled timeline, map, document close-up, "
                "location footage, or rights-cleared contextual footage. Avoid generic stock loops."
            ),
            camera="Use a mix of establishing shots, evidence close-ups, charts and purposeful motion; change only when the story advances.",
            sound="Clear narration first; subtle licensed/original music under speech; restrained transition sounds; no dramatic effect that implies unsupported danger.",
        ))

    script = f"""EDITORIAL SCRIPT PLAN — NOT VERIFIED NEWS COPY

TOPIC
{topic}

OPEN (0:00–0:20)
Lead with the most important confirmed development, its date and why viewers should care. No greeting or long channel intro.

WHAT HAPPENED
[Insert the confirmed event in 2–3 plain-English sentences.]
[Identify the primary source and publication/update time.]

WHY IT MATTERS
[Explain the real-world consequence. Identify who is affected and how.]
[Explain the relevant background or mechanism in simple language.]

WHAT THE EVIDENCE SHOWS
[Add attributable facts, data, document excerpts or official statements.]
[Distinguish confirmed facts, estimates, allegations and analysis.]

WHAT HAPPENS NEXT
[State the next confirmed milestone and what remains unknown.]

CLOSE
Give a concise evidence-based takeaway. Invite viewers to follow the next verified update; do not promise outcomes.

EDITORIAL RULE
This is a structure, not a completed factual script. Do not publish until every bracketed field is filled from reliable sources and checked by a human editor.
"""

    shorts = []
    angles = [
        "The one confirmed fact that changes the story",
        "Why this development matters",
        "The timeline in under a minute",
        "What is confirmed — and what is not",
        "What happens next",
    ]
    for i in range(req.shorts_count):
        angle = angles[i % len(angles)]
        shorts.append({
            "title": f"{topic}: {angle}",
            "hook": f"Here is the key detail about {topic} that puts the headline in context.",
            "script": (
                f"Explain this one angle: {angle}. Use one verified fact, explain its context, "
                "attribute the source on screen, and finish with what viewers should watch next. "
                "Do not cut off before delivering the promised explanation."
            ),
            "visual_plan": "Vertical 9:16; one clear visual per idea; readable captions; source label; original chart or rights-cleared footage.",
            "cta": "Follow for the next verified update and the full explanation.",
        })

    return ProductionPackage(
        concept=topic,
        titles=titles,
        hook=hook,
        thumbnail_concepts=thumbnail_concepts,
        script=script,
        scenes=scenes,
        editing_plan=[
            "Open with the confirmed development and its significance; skip greetings and long intros.",
            "Use a story-specific visual: original charts, timelines, maps, documents or rights-cleared footage.",
            "Explain what happened, why it matters, who is affected and what happens next.",
            "Keep on-screen text short; captions should not compete with dense paragraphs.",
            "Use a clean lower-third for names, locations, dates and source attribution.",
            "Keep music subtle under speech and duck it automatically; preserve natural pauses only when purposeful.",
            "Use accurate searchable titles and a thumbnail that represents the actual story.",
            "End with a concise takeaway and a useful next-update promise, not a generic engagement demand.",
        ],
        shorts=shorts,
        quality_check=[
            "Every factual claim has a reliable source and publication/update date.",
            "Primary sources are preferred; conflicting reports are clearly attributed.",
            "Facts, allegations, estimates and analysis are visibly distinguished.",
            "Narration explains significance and context; it is not a reading of headlines or articles.",
            "All footage, images, music and sound effects have documented commercial-use rights.",
            "Titles and thumbnails are accurate, specific and not misleading.",
            "Captions are synchronised, legible on mobile and checked for names/numbers.",
            "Human editorial review is completed before publishing.",
        ],
    )
