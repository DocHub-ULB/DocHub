<!-- Hallmark · studied: yes · DNA-source: local file (own work)
     macrostructure: Marquee Hero → Workbench · theme: custom "Papier, cooled" -->

# Design — DocHub

Locked design system for the DocHub visual refresh. This is the source of
truth: `static/styles/style.css` `:root` implements it, and future work (the
remaining screens, any contributor) should defer to it. Amend intentionally —
the file is the rule, not a snapshot.

Bootstrap 5.3 ships in a `layer(bootstrap)`; the rules in `style.css` win over
it. Colours are plain hex on purpose — no build step, readable by newcomers.

## System
- Genre · editorial voice (serif display) on a modern-minimal cool surface
- Macrostructure · Marquee Hero feeding a two-column Workbench (feed left, sticky rail right)
- Theme · custom — "Papier, cooled": production's royal blue + hand-made warmth, on a cool near-white paper
- Axes · light paper / high-contrast serif display / cyan-blue accent
- Lineage · production DocHub was Bootstrap royal-blue on cool white with serif headings; this keeps that identity and adds the "made by students" character.

## Tokens (`static/styles/style.css` `:root` is the source of truth)
```css
:root {
  /* Surface — cool, faint blue tint. Paper is light (L≈97%). */
  --bg:            #f4f6fa;   /* page paper            */
  --bg-raised:     #ffffff;   /* cards, topbar, inputs */
  --bg-sunk:       #e8ecf3;   /* recessed fills        */
  --ink:           #1b1e24;   /* primary text (cool near-black) */
  --ink-soft:      #4c535d;   /* secondary text        */
  --ink-faint:     #828b98;   /* meta / eyebrows (cool grey) */
  --rule:          #dde2ea;   /* hairlines             */
  --rule-strong:   #c1c8d3;   /* stronger dividers     */
  --paper-dot:     rgba(90, 115, 150, 0.12); /* ambient dot texture — decorative, non-aligning */

  /* Accent — the one recognisable DocHub blue. Buttons, links, active, doodles. */
  --brand-blue:      #0d6efd;
  --brand-blue-soft: #6ea8fe;
  --brand-blue-tint: #cfe2ff;
  --accent:          #0d6efd;
  --accent-soft:     #cfe2ff;
  --accent-ink:      #ffffff; /* white on blue — AA ~4.5:1 */

  /* Highlight — the one warm note. Staff-picks, marker-stroke, sticky notes. */
  --highlight:      #ffd84d;
  --highlight-soft: #fff2b8;
  --highlight-ink:  #5a4410;

  /* Semantic (votes) — deliberately off-palette, warm. */
  --positive: #6f8c3a;  /* upvote  */
  --negative: #c55c3a;  /* downvote */
  --danger:   #b43a2a;

  /* Type — four families, each quarantined to a job. */
  --font-display: "Instrument Serif", "Times New Roman", serif; /* headings; italic = emphasis words only */
  --font-body:    "DM Sans", -apple-system, sans-serif;         /* 15px / 28px */
  --font-mono:    "JetBrains Mono", ui-monospace, monospace;    /* eyebrows, course codes, meta */
  --font-hand:    "Caveat", cursive;                            /* taglines + doodle labels ONLY */

  /* Rhythm & shape. --grid is a 14px spacing/line-height unit, NOT a baseline
     the layout must snap to (the notebook grid was removed for that reason). */
  --grid: 14px;                 /* body line-height = calc(--grid * 2) = 28px */
  --radius-sm: 4px;  --radius: 6px;  --radius-lg: 10px;
  --shadow:      0 1px 0 rgba(43,35,26,.06), 0 4px 14px -6px rgba(43,35,26,.12);
  --shadow-card: 0 1px 0 rgba(43,35,26,.05), 0 8px 22px -10px rgba(43,35,26,.14);
}
```

## Type roles
- Hero h1 · Instrument Serif · 64px / 1.15 · wt 400 · `-0.02em` · name gets a yellow marker-stroke (gradient behind text, not a box)
- Section titles · Instrument Serif · ~32px · wt 400
- List/doc titles · Instrument Serif · 15–16px · wt 500
- Eyebrow / meta · JetBrains Mono · 11–13px · uppercase · `0.1–0.16em` · `--ink-faint`
- Headings are always roman. Italic survives only as emphasis inside a heading or as body emphasis.

## Components
- Nav · N1b masthead — brand-left, centre search with ⌘K chip, actions-right ("Déposer" blue button + initials avatar). Sticky, white, hairline bottom rule.
- Footer · Ft3 index columns + one Ft5 statement column (tilted yellow sticky-note CTA).
- Cards / list rows · `--bg-raised` or `--bg`, opaque, `--radius`, `--shadow-card`, `--rule` hairlines.
- Votes · up/down arrows, `--positive` / `--negative` on cast.

## CTA voice
- Primary · `--accent` fill · `--accent-ink` text · `--radius` · hover darkens 10%
- Secondary · ghost / outline on `--rule` · same radius

## Treatments (the identity)
- Ambient **dot texture** on `.main` (`--paper-dot`, 22px radial) — replaces the old baseline grid; decorative, nothing aligns to it.
- Hand-drawn **doodles** — `--brand-blue` at 0.06–0.15 opacity, `aria-hidden`, `pointer-events:none`, small.
- **Marker-stroke** highlight + tilted **sticky notes** in `--highlight`.

## Motion stance
- Silent success over toasts; optimistic vote/follow with un-toggle.
- Reduced-motion fallback · ≤150ms opacity crossfade.

## Provenance
- Source · local file (`static/styles/style.css` + `design_handoff_dochub_refresh/`), user's own work
- Extracted · 2026-08-11 via `hallmark study`
- Confidence · tokens are exact (read from shipped CSS); fonts are exact (declared in `base.html`). Reconciled from the Papier handoff: blue reverted to production royal `#0d6efd`, neutrals cooled from warm cream, notebook grid replaced by dot texture.

## Notes — anti-patterns to keep out
- Cards/rows on the dotted `.main` must stay **opaque** — dots must not bleed through them.
- **Caveat is quarantined** to taglines/doodles. It must never label real UI.
- Doodles stay low-contrast, `aria-hidden`, non-interactive — texture, not UI.
- Document viewer keeps the **compact action bar above the PDF**, not a sidebar (long-PDF fix).
- Do **not** reintroduce a baseline-locked grid; `--grid` is a spacing unit only.
- Cleanup debt: 11 inert `.baseline-grid` rules and a half-migrated `n`/`debug-layout` diagnostic remain in `style.css` — remove in a dedicated pass.

## Exports
`static/styles/style.css` `:root` is the source of truth (plain hex, no build
step — the project's intentional constraint). For Tailwind `@theme`, DTCG
`tokens.json`, or shadcn/ui variables, ask *"extend design.md with <format>
exports"*.
