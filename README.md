# AI YouTube Studio — India + Global News Explainers

This project is being developed for an English-language news channel. The editorial goal is not to read headlines: every episode should explain **what happened, why it matters, who is affected, what the evidence says, and what happens next**.

## Current repository capability

- Builds a structured news-explainer production package with title options, description template, story beats, Shorts angles, source requirements and editorial checks.
- Renders a separate 18-second visual/audio design preview with FFmpeg.
- Adds synchronised phrase captions, original generated background music and music ducking.
- Can optionally send the design preview to Telegram when the required repository secrets are configured.
- Runs automated tests and a sample-render smoke test in GitHub Actions.

**Important:** The current code does not yet fetch and verify live India/global news, write complete fact-checked narration, select real story-specific footage, or render a complete daily episode. The package is an editorial draft/structure, not publishable news copy. Do not publish the design preview as a real bulletin.

## Format strategy

- **Main explainer:** 16:9 landscape, normally 6–10 minutes for a focused multi-story episode. Give each story enough time to explain its context; do not stretch thin stories to hit a duration.
- **Shorts:** 9:16 vertical and no longer than 3 minutes. Make each Short a complete explanation of one story angle, not an arbitrary cut.
- The uploaded sample reviewed during development is 1080×1920 and 3:02.3 long. It is vertical but exceeds YouTube's 3-minute Shorts limit, so it should be shortened below 3:00 or split. It is not the right master format for a landscape long-form episode.

## Editorial workflow required before publishing

1. Collect current stories from reliable sources; prioritise primary sources and record source URLs, publisher, publication time and last-checked time.
2. Confirm important claims with independent reporting where appropriate. Separate confirmed facts, estimates, allegations, analysis and unknowns.
3. Write original narration that explains causes, context, impact and what happens next. Do not read article text or simply stitch headlines together.
4. Create story-specific visuals: original charts, timelines, maps, labelled documents, and footage/images with documented commercial-use rights.
5. Generate accurate searchable titles, a simple factual thumbnail, a useful description and chapter timestamps.
6. Render narration, captions, restrained original/licensed music and story-specific visuals. Keep narration intelligible and music ducked under speech.
7. Run automated checks for duration, resolution, missing audio, silence, clipping, caption coverage and black frames.
8. Require human editorial approval before public release. Breaking news must not publish until the key facts are verified.

## Run from Android

1. Open the repository's Actions tab.
2. Select AI YouTube Studio.
3. Tap Run workflow.
4. For the current design sample, enable Render the visual/audio sample MP4.
5. When the run finishes, open its artifacts and download the MP4/JSON.
6. To send the sample to Telegram, configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as repository Actions secrets and enable Telegram delivery.

Never put bot credentials in source files or share them in chat.

## Schedule and delivery

The existing schedule is preserved: Monday, Wednesday and Friday at 10:00 AM IST. That scheduled path currently creates a production-package JSON; it is not yet a fully automated, verified daily news MP4. Telegram delivery for the current workflow is for the design sample only.

## Monetisation and rights

YouTube monetisation is not guaranteed by upload frequency, AI tools, titles or tags. The channel needs original, non-repetitive reporting and meaningful explanation, not generic slideshows or automated readings of news feeds. Every visual, clip, music track and sound effect must be cleared for the intended commercial use. Follow current YouTube Partner Program and advertiser-friendly policies.

## Next engineering milestones

1. Connect a reliable news-ingestion layer with source timestamps and deduplication.
2. Add an optional script-generation provider that produces original explainers from source evidence, with citations and a strict no-invention rule.
3. Build the landscape episode renderer and a separate vertical Short renderer.
4. Add a story-specific visual asset pipeline and commercial-rights manifest.
5. Connect the completed, QC-passed episode to Telegram at the existing scheduled delivery time.
6. Add human approval before any public YouTube upload.
