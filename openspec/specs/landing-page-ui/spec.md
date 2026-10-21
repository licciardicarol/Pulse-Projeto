# landing-page-ui Specification

## Purpose
Define a apresentação visual, a responsividade e a acessibilidade da landing page pública do Pulse.

## Requirements

### Requirement: Header spans full viewport width
A landing page SHALL render a header that spans the full viewport width, with responsive horizontal padding and a persistent visual separation from the content below.

#### Scenario: Header with full width
- **WHEN** the page loads at any viewport width
- **THEN** the header occupies the full viewport width and its content remains horizontally aligned within the viewport

### Requirement: Header actions use consistent styling
The system SHALL use the same secondary-button style for the header login action and the hero secondary action.

#### Scenario: Secondary action consistency
- **WHEN** the user views the header and hero
- **THEN** both actions use the same color, radius, height, typography, hover, active and focus states

### Requirement: Content is centered
The landing page SHALL center hero, section titles, subtitles, cards and CTAs while preserving a full-width header.

#### Scenario: Visual alignment
- **WHEN** the user views each landing-page section
- **THEN** its primary content is centered within the section container

### Requirement: Responsive layout
The landing page SHALL use responsive grids and fluid typography for widths of 360px, 768px and 1280px or greater.

#### Scenario: Responsive card grid
- **WHEN** the viewport width is 360px
- **THEN** cards appear in one column
- **WHEN** the viewport width is 768px
- **THEN** cards appear in two columns
- **WHEN** the viewport width is 1280px or greater
- **THEN** cards appear in four columns

### Requirement: FAQ behavior
The system SHALL render a single-select accordion where opening one question closes the previously open question, with clear expanded and collapsed states.

#### Scenario: Expanding a question
- **WHEN** the user selects a closed question
- **THEN** its answer appears below it and the previously open question closes

#### Scenario: Collapsing a question
- **WHEN** the user selects an open question
- **THEN** its answer closes

#### Scenario: Keyboard support
- **WHEN** the user navigates to a FAQ question with the keyboard
- **THEN** Enter and Space activate the question and the question receives visible focus

### Requirement: Accessible FAQ presentation
Each FAQ question SHALL use an accessible control with aria-expanded and aria-controls attributes and reduced-motion support.

#### Scenario: Accessible state
- **WHEN** a user inspects the accordion control
- **THEN** the expanded state is exposed through aria-expanded and the answer is referenced by aria-controls

### Requirement: Landing page sections remain centered across viewport widths
The landing page SHALL center the content of the hero, how-it-works, resources, audience, FAQ, and final CTA sections relative to the viewport, with section backgrounds spanning the full viewport. The header and footer alignment SHALL remain unchanged.

#### Scenario: Wide viewport content alignment
- **WHEN** the page is viewed at 1920px wide
- **THEN** each listed section's content container is centered around the viewport midpoint and no horizontal scrolling is introduced

#### Scenario: Responsive section alignment
- **WHEN** the page is viewed at 360px, 768px, or 1280px wide
- **THEN** section content stays within the viewport and remains centered

### Requirement: Hero typography and spacing are readable
The hero title SHALL use fluid sizing from 2.25rem to 4.5rem, a 1.1 line-height, -0.02em letter spacing, a maximum width near 900px, and automatic horizontal margins. The subtitle SHALL be separated from its actions by at least 32px, and the actions SHALL be separated from the microcopy by at least 16px. The brand icon and name SHALL appear in one horizontal row.

#### Scenario: Hero hierarchy
- **WHEN** a visitor views the hero at any supported viewport width
- **THEN** the title, subtitle, actions, and microcopy are centered and have the specified spacing and readable title proportions

### Requirement: FAQ questions disclose one answer without accent backgrounds
The FAQ SHALL initially render all answers collapsed, permit at most one expanded answer, and allow the active answer to be collapsed by activating its question again. Question controls SHALL have no accent-color background in hover, focus, active, expanded, or collapsed states.

#### Scenario: Open and close one answer
- **WHEN** a visitor activates a collapsed question
- **THEN** its answer becomes visible, and activating the same question again hides that answer

#### Scenario: Only one answer remains open
- **WHEN** a visitor opens a different question while an answer is visible
- **THEN** the newly selected answer becomes visible and the previous answer closes

### Requirement: FAQ remains accessible and motion-aware
Each FAQ question SHALL be a keyboard-operable button with `aria-expanded` and `aria-controls`; each answer SHALL have a matching `id` and `role="region"`. Keyboard focus SHALL be visibly indicated, and answer and icon animations SHALL respect reduced-motion preferences.

#### Scenario: Keyboard operation
- **WHEN** a visitor focuses a question and activates it with Enter or Space
- **THEN** that question toggles its answer and updates `aria-expanded`

#### Scenario: Reduced motion preference
- **WHEN** the visitor requests reduced motion
- **THEN** FAQ expansion and icon rotation occur without animated transitions
