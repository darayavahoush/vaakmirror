# VaakMirror

Face & mouth biofeedback games for children with articulation disorders,
autism-related face/mouth awareness needs, or thick-tongue side effects from
medication. Module 02 of the VaakSiddhi speech & communication platform.

## Structure

- `src/pages/` — routed screens: `Landing`, `MirrorMirror`, `TongueTamer`,
  `LipSyncHero` (all three games live), `Dashboard` (therapist/parent view),
  `Exercises` (oromotor video library). `ComingSoonGame` is an unused
  leftover placeholder component, kept around in case a future game needs it.
- `src/data/soundTaxonomy.js` — the phonetics classification (place / manner /
  voicing) every target sound is tagged with. This is the backbone the
  diagnostic layer and dashboard roll results up against.
- `src/data/tongueMoves.js` — Tongue Tamer's two movement targets.
- `src/lib/mouthMetrics.js` — turns MediaPipe face landmarks into openness /
  spread metrics and scores them against a target shape.
- `src/lib/tongueTracking.js` — a color-based heuristic estimating tongue
  visibility/elevation (MediaPipe doesn't track the tongue itself).
- `src/lib/faceOverlay.js` — canvas drawing: the live mouth-match outline,
  the lion/robot/hero/bunny/cat/unicorn filters, Tongue Tamer's arrow cue.
- `src/lib/signalSmoothing.js` — EMA smoothing + tier hysteresis, so
  landmark/pixel jitter doesn't flicker the red/yellow/green feedback.
- `src/lib/sound.js` — synthesized chimes (Web Audio) and TTS cues (Speech
  Synthesis) — no audio asset files.
- `src/lib/api.js` — the client for the FastAPI backend (see below).
- `src/components/` — `Navbar`, `GameCard`, `MouthMotif` (hero signature
  visual), `CharacterFilterPicker`, `MouthShapeGuide` / `TongueShapeGuide`
  (animated target references), `CelebrationOverlay`, `ProgressRing` (star
  rewards, no numeric scores).

## Stack

React + Vite + Tailwind, matching the `frontend/` convention in
[breathquest](https://github.com/darayavahoush/breathquest). Face tracking
runs client-side via `@mediapipe/tasks-vision` (FaceLandmarker, loaded from
Google's CDN model asset) — no video leaves the browser.

## Running locally

The backend needs to be running for Dashboard/Exercises/attempt-logging to
work — see `../vaakmirror-backend/README.md` for that setup. The three games
themselves still work without it (attempt logging just fails silently and
gets skipped).

```
npm install
cp .env.example .env.local   # only needed if your backend isn't on localhost:8000
npm run dev
```

All three games need camera permission and a reasonably lit face to track
reliably. Each does a brief one-time calibration (relax your mouth for a
second) before scoring starts, since face proportions vary enough between
people that fixed thresholds don't fit everyone.

## What's live vs. approximate

- **Mirror Mirror** — real camera input, real landmark tracking, shape
  scoring calibrated per-player.
- **Tongue Tamer** — real camera input, but tongue position is a color
  heuristic (pink-pixel visibility/elevation in the mouth region), not a
  dedicated tongue tracker — MediaPipe's face mesh doesn't have tongue
  landmarks. Treat it as approximate; there's a disclosure banner in-app
  about this.
- **Lip Sync Hero** — same shape-scoring as Mirror Mirror, with timing
  pressure instead of untimed hold-to-pass. Audio cues use the browser's
  built-in speech synthesis, which mostly says letter *names* for single
  consonants rather than the isolated phoneme — also disclosed in-app.
- **Dashboard** and **Exercises** now read live from the backend
  (`src/lib/api.js`) instead of mock data. Both handle a "backend not
  running" state gracefully rather than breaking.

## Backend integration

Everything currently points at one hardcoded demo child (`DEMO_CHILD_ID = 1`
in `src/lib/api.js`), created by the backend's seed script — there's no
child-picker UI yet. Each game creates a session on load and logs an
attempt (tagged with place/manner/voicing where applicable) every time a
sound/movement resolves; the dashboard's category breakdowns and flagged
gaps are computed from that real data, not mocked.

This backend is standalone for now rather than merged into `breathquest`'s
actual database — see the backend README for the reasoning and what's
still missing (auth, migrations, multi-child support) before this could
handle real usage.
