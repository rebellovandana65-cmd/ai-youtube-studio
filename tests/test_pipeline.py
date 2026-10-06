from models import GenerateRequest
from pipeline import build_package

def test_build_package():
    pkg=build_package(GenerateRequest(idea='A photograph from tomorrow appeared on every phone.'))
    assert len(pkg.titles)==5
    assert len(pkg.scenes)>=12
    assert len(pkg.shorts)==5
