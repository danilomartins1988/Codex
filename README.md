# The Hidden Economics

A reusable TypeScript / React / Remotion pipeline for a single original animated
YouTube Short: **Visa Isn't Your Lender. So Who Gets Paid?**

**Editorial status:** official primary-source sites are currently blocked by the
environment's network policy. Technical production can run; publication is gated.
See [research](research/README.md) and [QA](docs/QA.md). This is not permission to
publish the video to YouTube. No YouTube upload is performed.

## Requirements and setup

- Linux, Node.js 22+ (tested 24.22.1), Python 3.12, FFmpeg / FFprobe (tested 7.1.5).
- Chromium at `/usr/bin/chromium`, or set `CHROME_PATH` to a supported executable.
- About 3 GB disk for dependencies, cached neural speech assets, and render work.
- Network: npm / PyPI registries and GitHub release / raw download hosts.
- No paid API and no TTS credentials. Do not put secrets in this project.

Use the existing checkout in the isolated cloud task. No separate Git worktree
is needed. In `/workspace/Codex`:

```sh
npm ci --cache .cache/npm
python -m venv .venv
.venv/bin/pip install -r requirements-lock.txt
npm run prepare:episode
npm run typecheck
npm run render -- --stills
npm run render
npm run qa
npm run editorial:check
```

The last command deliberately fails until real primary-source verification is
recorded. Do not remove this gate to obtain a passing report. `npm run produce`
runs speech preparation, TypeScript checking, the one final render, and technical
QA; it does **not** imply editorial approval. `npm run studio` opens Remotion's
interactive local editor for development; the export itself is fully programmatic.

Kokoro model weights and voice styles are downloaded via verified HTTPS into
ignored `.cache/tts/`, and checked against `docs/tts-checksums.json`. Original
checksum capture establishes repeatability from the TLS download, not a
publisher-signed provenance assertion. Audio chunks are cached by text, voice,
and speed. The finished narration WAV is committed, so rebuilding the exact
initial animation does not require generating speech again.

## Production architecture

1. **Topic/config:** `episodes/001-visa-mastercard.json` is the authored source.
2. **Research:** `research/claims.json` maps every narrative claim to references,
   verification state, and evidence. A person must actually read primary sources.
3. **Script:** original human-reviewed narration lives in scene `text` fields;
   preparation generates `episodes/script.md`. There is no hidden LLM API call
   or claim that fact-checking/script authorship is autonomously solved.
4. **Storyboard:** configuration selects reusable visual kinds, headline lines,
   and claim IDs. `episodes/storyboard.md` is derived from actual audio lengths.
5. **Assets:** SVG banks, merchant, credit card, moving network, flows and road
   metaphor are built from reusable components in `src/components.tsx`.
6. **Speech:** `scripts/prepare.py` runs Kokoro ONNX `af_heart` locally in en-US.
7. **Synchronization:** individually synthesized sentences determine frame-based
   scene durations. Lead-in and breath pauses are explicit, quantized to 30 fps.
8. **Animation:** `src/Film.tsx` adds continuous flow, orbital motion, spring
   entrances, wipe transitions, safe typography and an overall progress indicator.
9. **Captions:** sentence captions burned into the film; matching SRT exported
   separately. No claim of word-level timing. Text appears with each scene.
10. **Export:** `scripts/render.ts` bundles once and renders H.264 / AAC MP4,
    yuv420p, 1080×1920, 30 fps with three rendering workers and CRF 19.
11. **QA:** `scripts/qa.py` probes the real file, decodes it completely, detects
    full black frames / prolonged silence, verifies tracks, frame counts, audio
    levels and caption coverage. Editorial clearance is a separate failing gate.
12. **Publishing package:** `episodes/publishing.json` is generated from config.

For a future production, create a new config using the same schema and run
`EPISODE=/absolute/path/to/episode.json npm run prepare:episode`. Then render and
validate. The generated timeline is the active composition; it is rebuilt rather
than accumulating episodes in one export. New kinds can reuse existing SVG
components. The initial execution intentionally produces only episode 001.
Research paths and the final QA's 12-scene assertion currently describe this
initial target; adapt those explicit editorial/test assumptions for a new episode.

## Output and persistence

`output/001-visa-mastercard-short-1080x1920.mp4` is the sole final video.
`output/captions.srt`, `output/ffprobe.json`, `output/qa.json`, and
`output/contact-sheet.jpg` accompany it. See `DELIVERY.md` for the actual verified
remote delivery status. Local output existence alone is not persistence.

Source, narration and the small final MP4 are intended for the authorized GitHub
branch. No model weights, environments, node_modules, API tokens or caches belong
in Git. Future large videos should use an authorized release or LFS workflow.

## Rights and costs

All visual artwork and narration script are original for this project. No copied
brand logos, stock footage, third-party music, or sound effects are included.
Visa and Mastercard names are used descriptively, without implying endorsement.
Kokoro's upstream documentation describes Apache-licensed weights; the upstream
Apache license and ONNX wrapper's MIT license are retained in `docs/`. Runtime
dependencies retain their own licenses. Remotion has a commercial-use license
with eligibility conditions; check current terms before scaling a business team.
No paid services or YouTube publishing were activated.
