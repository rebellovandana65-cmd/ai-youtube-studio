import wave

from scripts.render_news_preview import NARRATION, make_music


def test_preview_narration_is_explicitly_a_design_preview():
    assert "production preview" in NARRATION.lower()
    assert "verified sources" in NARRATION.lower()


def test_original_music_bed_is_valid_wav(tmp_path):
    target = tmp_path / "music.wav"
    make_music(target, seconds=0.25, sample_rate=8000)
    with wave.open(str(target), "rb") as audio:
        assert audio.getnchannels() == 1
        assert audio.getframerate() == 8000
        assert audio.getnframes() == 2000
