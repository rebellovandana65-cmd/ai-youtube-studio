# Newsroom AI Agent Network

## Scope
English-language daily newsroom covering India and Global stories, targeting up to eight story leads per region.

## Agents in the foundation milestone
1. India Research Agent — collects India-focused RSS leads.
2. Global Research Agent — collects global RSS leads independently.
3. Deduplication Agent — removes exact normalized headline duplicates.
4. Verification Agent — checks source metadata and explicitly leaves factual verification pending.
5. Script Agent — creates a source-attributed editorial rundown; it does not invent missing details.
6. Chief Agent — coordinates agents, isolates regional feed failures and emits a report.

## Free-first design
- Python standard library for RSS and orchestration.
- GitHub Actions for daily scheduled execution.
- JSON artifact for the editorial queue.
- No paid model, API key, database or video-generation provider required in this milestone.

## Important limitations
RSS headlines and snippets are leads, not sufficient evidence for publication. The current verification agent checks metadata only. An editor must open original reporting, confirm facts against independent sources, resolve conflicts and approve the script. No video generation or YouTube publishing is enabled yet.

## Next milestones
- Multi-source corroboration and claim-level verification.
- Editor-approved script generation with optional free/local model adapter.
- Rights-aware visual asset planning and FFmpeg rendering.
- Thumbnail, metadata and Shorts generation.
- YouTube OAuth upload/scheduling with approval gate.
- Analytics feedback loop and failure notifications.
