# BioScale Phenotypic Age — Frontend

A Next.js 14 (App Router) + TypeScript + Tailwind CSS web interface for the
BioScale phenotypic age estimation project. It presents the project and provides
a tool that calls the existing FastAPI backend (`POST /predict`).

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Inter via `next/font`

## Project structure

```
frontend/
├── app/
│   ├── layout.tsx          # Global layout, navigation, fonts, SEO metadata
│   ├── globals.css         # Tailwind layers and component classes
│   ├── page.tsx            # Overview / home
│   ├── tool/page.tsx       # Phenotypic Age tool (renders the client form)
│   └── methods/page.tsx    # Methods / technical details
├── components/
│   ├── NavBar.tsx          # Top navigation (active-link aware)
│   └── PhenotypicAgeTool.tsx  # Client form + results panel
├── lib/
│   └── api.ts              # Typed API client (reads NEXT_PUBLIC_API_BASE_URL)
├── .env.example
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── postcss.config.js
└── next.config.mjs
```

## Prerequisites

- Node.js 18.18+ (developed against Node 20+)
- The BioScale FastAPI backend running and reachable

## Development

```bash
cd frontend
npm install
cp .env.example .env.local   # then edit if your backend is not on localhost:8000
npm run dev
```

The app runs at http://localhost:3000.

Start the backend separately (from the repository root) so the tool can reach it:

```bash
cd bioscale
uvicorn backend.api.app:app --reload   # serves http://localhost:8000
```

## Configuring the API base URL

The frontend reads the backend origin from `NEXT_PUBLIC_API_BASE_URL` and appends
`/predict`. It defaults to `http://localhost:8000` when the variable is unset.

`.env.local` (development):

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Production (set in your hosting provider's environment, no trailing slash):

```
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.example
```

Because this variable is prefixed with `NEXT_PUBLIC_`, it is inlined at build
time. Set it before running `npm run build` for production deployments.

## Build and run for production

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.example npm run build
npm run start
```

`npm run start` serves the optimized build (default port 3000; override with
`-p`, e.g. `npm run start -- -p 4000`).

## Backend contract

The tool sends a JSON body matching the backend `PredictRequest` model:

| Field | Type | Notes |
|-------|------|-------|
| `chronological_age` | number | years (0–150) |
| `sex` | enum | `male`, `female`, `other`, `unknown` |
| `bmi` | number | kg/m² (10–60) |
| `sleep_hours` | number | 0–24 |
| `sleep_quality` | integer | 1–5 |
| `weekly_exercise_sessions` | integer | 0–7 |
| `diet_quality_score` | integer | 1–10 |
| `stress_level` | integer | 1–10 |
| `physical_activity_level` | enum | `low`, `moderate`, `high` |
| `smoking_status` | enum | `never`, `former`, `current` |
| `alcohol_intake_frequency` | enum | `never`, `monthly`, `weekly`, `daily` |
| `has_hypertension` | boolean | |
| `has_diabetes` | boolean | |

The response is rendered from:

```json
{
  "chronological_age": 52.0,
  "phenotypic_age": 56.2,
  "age_acceleration": 4.2,
  "model_version": "v1.0.0"
}
```

The "age difference" shown in the UI is the backend `age_acceleration`
(`phenotypic_age − chronological_age`).

## Notes

- Validation errors and unreachable-backend conditions are surfaced in a red
  results banner.
- The interface is intended as a research and educational demonstration and
  does not provide medical advice.

## `/predict` response shape and component state handling

### Expected response shape

The `/predict` endpoint returns the following JSON, mirrored by the
`PredictResponse` type in `lib/api.ts`:

```json
{
  "chronological_age": 52.0,
  "phenotypic_age": 56.2,
  "age_acceleration": 4.2,
  "model_version": "v1.0.0"
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `chronological_age` | number | Echoed input age, in years |
| `phenotypic_age` | number | Predicted phenotypic (biological) age, in years |
| `age_acceleration` | number | `phenotypic_age − chronological_age` (positive = accelerated) |
| `model_version` | string | Version label of the deployed model |

The response is validated and normalized by `normalizePredictResponse()` in
`lib/api.ts` before reaching the component. Each numeric field is coerced to a
finite number; if `age_acceleration` is absent but the two ages are present, it
is derived as `phenotypic_age − chronological_age`. If the essential numeric
fields are missing or non-numeric, an `ApiError` is thrown rather than allowing
`undefined` values to propagate into rendering. `model_version` falls back to
`"unknown"` when missing.

### Loading, success, and error states

`PhenotypicAgeTool.tsx` tracks an explicit status: `idle | loading | success |
error`. The results panel renders one state at a time:

- **Idle** — before any submission, an instructional placeholder card is shown;
  no numeric values are accessed.
- **Loading** — while the request is in flight, the submit button is disabled
  and shows "Estimating…", and the panel shows a loading message.
- **Success** — the results card displays phenotypic age, chronological age, the
  signed age difference, and the model version. All numeric rendering goes
  through safe helpers (`toFiniteOrNull` / `formatNumber`) that emit an en dash
  ("–") instead of crashing if a value is ever missing or non-finite.
- **Error** — backend validation errors (FastAPI `detail`, including field-level
  validation arrays) and network/unreachable-backend failures are caught and
  displayed in a clearly styled red banner; the app does not crash.

The form can be submitted repeatedly: each submission resets the error state and
status, and the previous result remains visible until a new result or error
replaces it. A **Reset** button restores the default inputs and clears results.

## Design system & implementation notes

The UI uses a **Material You (Material Design 3)** design system, adapted to
Tailwind, to present BioScale as a personal, end-to-end ML + full-stack
portfolio project. Tokens live in `tailwind.config.ts`; shared patterns live in
`app/globals.css`.

### Color tokens (light, tonal)

Defined as semantic Tailwind colors:

| Token | Hex | Usage |
|-------|-----|-------|
| `surface` | `#FFFBFE` | Page background (never pure white) |
| `surface-container` | `#F3EDF7` | Default card/section surface |
| `surface-container-low` | `#E7E0EC` | Recessed surfaces, fields |
| `on-surface` / `on-surface-variant` | `#1C1B1F` / `#49454F` | Primary / secondary text |
| `primary` / `on-primary` | `#6750A4` / `#FFFFFF` | CTAs, focus, key accents |
| `primary-container` / `on-primary-container` | `#EADDFF` / `#21005D` | Hero result surface |
| `secondary-container` / `on-secondary-container` | `#E8DEF8` / `#1D192B` | Tonal buttons, active nav, chips |
| `tertiary` / `tertiary-container` | `#7D5260` / `#FFD8E4` | Calm accent (age acceleration, disclaimers) |
| `outline` / `outline-variant` | `#79747E` / `#CAC4D0` | Borders, dividers (used sparingly) |
| `error` / `error-container` | `#B3261E` / `#F9DEDC` | Error banner only |

Depth is created by **tonal layering** (surface → surface-container →
surface-container-low), not heavy borders. Interaction uses **opacity-based
state layers** (a `currentColor` `::after` overlay at 8% hover / 10% focus /
12% press) rather than hard color swaps.

### Typography

Roboto (Google Fonts, weights 400/500/700) via `next/font`, with an MD3 type
scale exposed as Tailwind font sizes: `display-lg` (56px), `display-md`,
`headline-md` (32px), `title-lg` (24px), `title-md`, `body-lg` (20px),
`body-md` (16px), `body-sm`, and `label-lg` / `label-md` (buttons & chips, with
slightly increased letter spacing). Headings default to weight 500; headings use
~1.2–1.3 line height and body ~1.6.

### Radius, elevation, motion

- **Radius:** `md-xs` 8px, `md-sm` 12px, `md-md` 16px, `md-lg` 24px (default
  cards), `md-xl` 32px / `md-2xl` 48px (hero & major containers), `rounded-full`
  for all buttons, chips, and badges.
- **Elevation:** soft, layered shadows `shadow-md-1`…`shadow-md-4`; cards rest at
  `md-1` and lift to `md-3` on hover.
- **Motion:** `transition-all duration-300 ease-emphasized`
  (`cubic-bezier(0.2,0,0,1)`); interactive cards use
  `motion-safe:hover:scale-[1.02]`; buttons use `motion-safe:active:scale-95`.
  Decorative blurred **blobs** (`components/Blobs.tsx`, `.blob` + `blur-3xl`)
  add organic depth in the hero and disclaimer. All animation is gated behind
  `motion-safe` and a global `prefers-reduced-motion` reset.

### Component patterns (reuse these)

Shared classes in `globals.css`:

- **Buttons:** `.btn-filled` (primary), `.btn-tonal` (secondary container),
  `.btn-text`. All are pill-shaped and carry the state-layer overlay and focus
  ring automatically.
- **Cards:** `.md-card` (container surface + `shadow-md-1`), `.md-card-low`
  (recessed), and `.md-card-interactive` (hover lift + scale).
- **Fields:** `.md-label`, `.md-field` (filled text field — muted surface,
  rounded top, 2px bottom border that turns `primary` on focus), `.md-hint`.
- **Chips:** `.md-chip`, `.md-chip-primary`, `.md-chip-tertiary`.
- **Misc:** `.eyebrow` (section label), `.state-layer` (add to any custom
  interactive element to get the MD3 overlay), `.container-content`, `.page-bg`.

React components: `SectionHeader` (eyebrow + title + description), `StatCard`
(label + value + hint), `Blobs` (decorative), and `NavBar`.

**To add a new component that fits the system:** build on `.md-card` for
surfaces, use the `body-*` / `title-*` / `headline-*` type classes for text,
reach for the `surface*` / `on-surface*` / `primary*` color tokens, keep radii
on the `md-*` scale, and add `.state-layer` (or a `.btn-*` class) to anything
clickable so it inherits the state layer and focus styling.

### Accessibility

- Inputs are associated with `<label htmlFor>`; the results region uses a clear
  visual hierarchy.
- Focus-visible rings (`focus-visible:ring-2 ring-primary ring-offset-2`) on all
  interactive elements; decorative blobs are `aria-hidden` and
  `pointer-events-none`.
- `prefers-reduced-motion` disables animations and smooth scrolling globally.

### Responsiveness

Mobile-first: the hero, feature grid, tech-stack panel, form sections, metrics,
and architecture cards reflow from multi-column on desktop to single-column on
small screens. The results panel becomes sticky beside the form at the `lg`
breakpoint, and the nav keeps inline links with a persistent "Open Tool" CTA.

