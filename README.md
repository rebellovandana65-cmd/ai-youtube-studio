# Impossible Reality — AI YouTube Studio

A mobile-friendly production engine for the **Impossible Reality** YouTube channel.

## Goal
Turn one unusual video idea into a complete production blueprint:
- clickable titles and thumbnail concepts
- 8–12 minute story structure
- scene-by-scene narration and visual prompts
- editing and sound-design plan
- five Shorts derived from the long-form story
- provider-agnostic image/video/voice routing

## API
Run:
`pip install -r requirements.txt`
`uvicorn app:app --reload`

Then open `/docs`.

Generate with `POST /api/generate`:
`{"idea":"A photograph from tomorrow appeared on every phone."}`

## Provider model
The project supports multiple configured providers in priority order. It does **not** bypass quotas, paywalls, CAPTCHAs, or provider terms. Actual media generation requires legitimate provider APIs and credentials.

## Publishing quality
Every episode should be genuinely different, original, and human-reviewed. Avoid copied footage, copyrighted clips, unsupported claims presented as fact, and repetitive mass-produced slideshows.
