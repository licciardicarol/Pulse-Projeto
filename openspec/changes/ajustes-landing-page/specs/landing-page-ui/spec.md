## Purpose

Define a apresentação visual, a responsividade e a acessibilidade da landing page pública do Pulse.

## ADDED Requirements

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
