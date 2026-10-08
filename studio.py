from pathlib import Path
import json
import re


def clean(text):
    return re.sub(r"\s+", " ", text.strip()).rstrip(".!?")


def score_topic(topic, demand=70, growth=65, curiosity=80, competition=55, visuals=80, depth=80, monetization=75):
    score = round(demand*.18 + growth*.17 + curiosity*.22 + competition*.10 + visuals*.12 + depth*.13 + monetization*.08)
    verdict = "MAKE NOW" if score >= 85 else "WATCH / TEST" if score >= 70 else "SKIP"
    return {"topic": topic, "score": score, "verdict": verdict}


def build_package(idea, duration=10, shorts=6):
    idea = clean(idea)
    beats = ["cold open", "setup", "first clue", "why it matters", "obvious explanation", "contradiction", "escalation", "new evidence", "context", "turning point", "explanation", "aftermath", "final implication"]
    scene_count = max(24, duration * 4)
    scenes = []
    per_scene = max(2, (duration * 60) // scene_count)
    for i in range(scene_count):
        beat = beats[i % len(beats)]
        scenes.append({"scene": i + 1, "duration_seconds": per_scene, "beat": beat, "narration_goal": f"Add one concrete new fact or consequence about {idea}.", "visual_goal": f"Create a distinct documentary visual for {idea}: {beat}. Use original graphics, generated visuals, maps, diagrams, or properly licensed references.", "edit": "Vary framing and pacing; slow down for important evidence.", "audio": "Natural narration, subtle ambience, restrained music, brief silence before major reveals."})
    angles = ["the strangest clue", "the moment everything changed", "the obvious explanation was wrong", "the detail people missed", "the surprising consequence", "the unanswered question"]
    shorts_out = []
    for i in range(shorts):
        angle = angles[i % len(angles)]
        shorts_out.append({"title": f"{idea}: {angle.title()}", "angle": angle, "hook": f"Almost everyone misses this part of the story about {idea}.", "structure": "Hook -> evidence -> escalation -> curiosity gap -> Related Video CTA.", "cta": "The full story is linked as the Related Video."})
    return {"channel_direction": "Curiosity Files: original English documentary stories about strange business, technology, internet, consumer and real-world phenomena.", "idea": idea, "recommended_duration_minutes": duration, "hook": f"What if the thing everyone thought was ordinary was hiding a much bigger story? That is exactly what happened with {idea}.", "titles": [f"{idea}: The Part Nobody Saw Coming", f"How {idea} Became Much Stranger Than It Looked", f"The Hidden Story Behind {idea}", f"Everyone Missed This About {idea}", f"{idea} — And Then Everything Changed"], "thumbnail_concepts": ["One striking subject, one unexplained detail, minimal text.", "Evidence-style composition with the key mystery enlarged.", "Before/after visual showing the surprising change."], "long_form_structure": scenes, "shorts": shorts_out, "quality_gate": ["Original angle and narration.", "Verify factual claims before publication.", "Do not invent evidence, quotes, experts, statistics or events.", "Use only footage/assets with appropriate rights or create original visuals.", "Avoid repetitive slideshow templates.", "Human review before publishing."]}


def save_package(package, output="output"):
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "production_package.json"
    path.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


if __name__ == "__main__":
    print(save_package(build_package("A tiny company quietly changed an entire industry")))
