# AI YouTube Studio — News Video Upgrade

This repository is being upgraded for an English-language news channel covering India and global stories.

## What this upgrade adds

- A reproducible FFmpeg news-style sample renderer.
- Animated editorial graphics, a headline treatment, lower-third and ticker.
- Burned-in, phrase-timed subtitles with high-contrast styling.
- A newly synthesized, copyright-safe ambient music bed.
- Voice/music sidechain ducking and final loudness normalization.
- MP4 H.264/AAC export at 1280x720, 24 fps.
- Optional Telegram delivery for the manually rendered sample.
- A GitHub Actions artifact containing the sample MP4 and production package.

The sample is explicitly labelled as a design preview. It uses generated graphics and a basic open-source system voice, not live reporting, licensed news footage, or a finished daily news episode.

## Run the first sample from Android

1. Open the repository's **Actions** tab.
2. Select **AI YouTube Studio**.
3. Tap **Run workflow**.
4. Keep **Render the visual/audio sample MP4** enabled.
5. Tap **Run workflow** again.
6. Open the completed run and download the **news-studio-first-preview** artifact. It contains news-style-preview.mp4.

If Telegram delivery is wanted, add these repository Actions secrets:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

The manual preview workflow sends the sample to Telegram when both secrets are present and the Telegram option is enabled. Never put bot credentials in source files.

## Schedule

The existing cron schedule is intentionally preserved: 30 4 * * 1,3,5 UTC, which is 10:00 AM India Standard Time on Monday, Wednesday, and Friday. This scheduled path still generates the existing production-package JSON; it does not send a fake preview as a news bulletin.

## Important current limitation

The existing studio.py and pipeline.py create production blueprints with placeholder narration and visual prompts. They do not yet research and verify daily news, create a complete finished episode, or render real news footage. The new MP4 is a renderer/design smoke test so the visual treatment, subtitle appearance, audio mix, and Telegram sample-delivery path can be inspected before connecting the renderer to verified story assets and production narration.

Do not publish the sample as real news. Real episodes require verified sources, rights-cleared visuals, accurate scripts, and human review.

## Quality and rights

- Never invent claims, statistics, quotes, sources, or events.
- Use original or properly licensed music, images, and footage.
- Keep narration intelligible above music.
- Use readable mobile-safe subtitles.
- Do not use sensational visuals that misrepresent the story.
