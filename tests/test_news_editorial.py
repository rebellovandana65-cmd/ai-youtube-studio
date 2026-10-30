from models import GenerateRequest
from pipeline import build_package
from studio import build_package as build_studio_package


def test_api_package_is_news_explainer_not_fiction_template():
    pkg = build_package(GenerateRequest(idea="India announces a new public transport policy"))
    assert len(pkg.titles) == 5
    assert len(pkg.scenes) >= 12
    assert len(pkg.shorts) == 5
    assert "why it matters" in pkg.titles[0].lower()
    assert "verified" in pkg.script.lower()
    assert any("source" in item.lower() for item in pkg.quality_check)
    assert all("verified" in scene.narration.lower() for scene in pkg.scenes)


def test_scheduled_package_has_news_editorial_gates():
    pkg = build_studio_package("A global technology regulation update")
    assert "India + Global News Explained" in pkg["channel_direction"]
    assert "DRAFT" in pkg["editorial_status"]
    assert len(pkg["titles"]) == 5
    assert "source_requirements" in pkg
    assert any("human" in item.lower() for item in pkg["quality_gate"])
    assert "not a completed factual script" in pkg["script"].lower()
