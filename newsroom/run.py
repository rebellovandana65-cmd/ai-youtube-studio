"""Run the free RSS-based newsroom and write a JSON editorial queue."""
import json
from pathlib import Path
from .agents import ChiefAgent


def main() -> None:
    report = ChiefAgent().run()
    output = Path("output")
    output.mkdir(parents=True, exist_ok=True)
    target = output / "newsroom_report.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "india_stories": report["india"]["story_count"],
        "global_stories": report["global"]["story_count"],
        "errors": report["errors"],
        "output": str(target),
    }, indent=2))
    if report["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
