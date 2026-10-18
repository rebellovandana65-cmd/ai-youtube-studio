from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from engine import edit_video, make_srt

st.set_page_config(page_title="TradeCut AI", page_icon="🎬", layout="wide")

st.markdown("""
<style>
:root { color-scheme: light dark; }
.block-container { max-width: 1120px; padding-top: 2rem; }
.hero { padding: 1.4rem; border-radius: 18px; border: 1px solid rgba(128,128,128,.25);
        background: linear-gradient(120deg, rgba(30,64,175,.18), rgba(16,185,129,.10)); }
.small { opacity: .72; font-size: .9rem; }
</style>
<div class="hero">
<h1>🎬 TradeCut AI</h1>
<p>Raw trading commentary → cleaner, tighter, YouTube-ready video.</p>
<p class="small">Free/open-source MVP · No paid AI API key · Always review before publishing</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Edit settings")
    trim_silence = st.toggle("Shorten long silent gaps", value=True)
    normalize_voice = st.toggle("Balance voice volume", value=True)
    add_captions = st.toggle("Generate captions (local AI)", value=True)
    st.caption("Caption generation downloads a speech model on first use and may be slow on free hosting.")
    st.caption("Use only music you own or have permission to use.")

uploaded = st.file_uploader("Upload your raw recording", type=["mp4", "mov", "m4v", "webm"])
music = st.file_uploader("Optional: upload your licensed background music", type=["mp3", "wav", "m4a", "aac"])

if uploaded:
    st.video(uploaded)
    st.write(f"**File:** {uploaded.name} · **Size:** {uploaded.size / (1024*1024):.1f} MB")
    st.warning("Before upload, hide account numbers, client IDs, balances or other private financial details.")
    if st.button("✨ Auto-edit my video", type="primary", use_container_width=True):
        with st.spinner("Editing video… this may take a few minutes. Keep this page open."):
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    source = root / f"input{Path(uploaded.name).suffix.lower()}"
                    source.write_bytes(uploaded.getvalue())
                    music_path = None
                    if music:
                        music_path = str(root / f"music{Path(music.name).suffix.lower()}")
                        Path(music_path).write_bytes(music.getvalue())
                    output = root / "TradeCut_edited.mp4"
                    stats = edit_video(str(source), str(output), music_path,
                                       trim_silence=trim_silence,
                                       normalize_voice=normalize_voice)
                    srt_bytes = None
                    transcript = ""
                    if add_captions:
                        srt_path = root / "captions.srt"
                        try:
                            transcript = make_srt(str(output), str(srt_path))
                            srt_bytes = srt_path.read_bytes()
                        except Exception as e:
                            st.warning(f"Video edit succeeded, but captions could not be generated: {e}")

                    st.success("Your edited video is ready.")
                    st.video(output.read_bytes())
                    st.metric("Original length", f"{int(stats['original_seconds']//60)}:{int(stats['original_seconds']%60):02}")
                    st.metric("Edited length", f"{int(stats['edited_seconds']//60)}:{int(stats['edited_seconds']%60):02}")
                    st.caption(f"Shortened by {stats['seconds_removed']:.1f} seconds · {stats['segments_kept']} kept sections")
                    st.download_button("⬇️ Download edited MP4", output.read_bytes(),
                                       file_name="TradeCut_edited.mp4", mime="video/mp4",
                                       use_container_width=True)
                    if srt_bytes:
                        st.download_button("⬇️ Download captions (.srt)", srt_bytes,
                                           file_name="captions.srt", mime="text/plain",
                                           use_container_width=True)
                    if transcript:
                        st.subheader("YouTube packaging suggestions")
                        words = [w.strip(".,!?;:()[]\"'").lower() for w in transcript.split()]
                        key = [w for w in words if len(w) > 4 and w not in {
                            "today", "there", "about", "after", "before", "because", "really",
                            "trade", "trading", "profit", "video", "would", "could", "should"}]
                        phrase = " ".join(dict.fromkeys(key[:5])).title() or "My Trading Review"
                        st.write("**Title idea:** What I Learned From Today's Trade | Full Breakdown")
                        st.write("**Alternative title:** Today's Trade Explained: Plan, Execution & Lessons")
                        st.write("**Thumbnail text:** TRADE BREAKDOWN")
                        st.write("**Retention tip:** Open with the most useful lesson, then show the setup, decision, result, and what you would improve.")
                        st.write("**Caption review:** Check names, prices, profit/loss figures and financial terminology before publishing.")
            except Exception as e:
                st.error(f"Could not finish this edit: {e}")
                st.info("Try an MP4 under 300 MB, or turn off captions if the free host runs out of memory.")

st.divider()
st.subheader("What this version does — and doesn't")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Included**\n- Long-silence trimming\n- Voice loudness balancing\n- Optional quiet music bed\n- Local AI captions\n- MP4 and SRT export")
with c2:
    st.markdown("**Not included yet**\n- Perfect emotion detection\n- Automatic animated zooms on the correct trading numbers\n- Thumbnail image generation\n- Guaranteed viral/retention prediction\n- Automatic YouTube publishing")
st.caption("No editor can guarantee views. Preview the full export: silence detection may mistake quiet speech for silence.")
