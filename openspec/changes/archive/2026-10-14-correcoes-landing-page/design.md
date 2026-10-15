## Context

See proposal.md and specs/landing-page-ui/spec.md. The current `rx.container` wrappers render at x=0 on wide screens without a centering margin; the FAQ currently uses a Radix header rendered as an `h3`, while its content defaults to `display:none` until Radix state changes.

## Goals / Non-Goals

**Goals:**
- Make section width, maximum width, auto margins, padding, and alignment explicit in one reusable component helper.
- Keep full-width backgrounds separate from their constrained content.
- Make FAQ state and disclosure semantics explicit and independent of Radix accordion defaults.

**Non-Goals:**
- Change the navbar or footer alignment.
- Change routes, business behavior, Xano integration, stored data, or dependencies.

## Decisions

- Replace content `rx.container` wrappers with one landing-page section-container helper that renders a full-width centered flex column and accepts section vertical padding. Keep each section's existing outer full-width box as the background layer.
- Keep the hero content in a full-width centered wrapper; apply the requested title sizing and spacing to its existing components. Use a horizontal stack for the logo mark and wordmark.
- Use a small Reflex state with an integer active FAQ index, plus native button controls and an always-present answer region. A single integer provides single-open/collapsible behavior without depending on Radix's generated header/content styles. Native buttons provide Tab, Enter, and Space behavior.
- Animate answer height with a CSS grid-row transition between `0fr` and `1fr`, and rotate the chevron from the same state. Explicit transparent backgrounds and focus outlines prevent theme accent fills.

## Risks / Trade-offs

- [FAQ state updates require the Reflex backend connection] → Run the app in the supported production mode and validate clicks and keyboard interaction in the browser.
- [CSS grid-row animation can clip content if the inner wrapper lacks a zero minimum height] → Keep the answer text inside an `overflow:hidden; min-height:0` wrapper and test expanded/collapsed states.

## Migration Plan

No data or dependency migration is required. Rollback consists of restoring the previous page component and CSS; routes and persisted state are unaffected.
