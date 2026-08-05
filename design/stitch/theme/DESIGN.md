---
name: Literary Noir
colors:
  surface: '#111317'
  surface-dim: '#111317'
  surface-bright: '#37393e'
  surface-container-lowest: '#0c0e12'
  surface-container-low: '#1a1c20'
  surface-container: '#1e2024'
  surface-container-high: '#282a2e'
  surface-container-highest: '#333539'
  on-surface: '#e2e2e8'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e2e2e8'
  inverse-on-surface: '#2f3035'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#b9c8de'
  on-secondary: '#233143'
  secondary-container: '#39485a'
  on-secondary-container: '#a7b6cc'
  tertiary: '#ffb783'
  on-tertiary: '#4f2500'
  tertiary-container: '#d97721'
  on-tertiary-container: '#452000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#d4e4fa'
  secondary-fixed-dim: '#b9c8de'
  on-secondary-fixed: '#0d1c2d'
  on-secondary-fixed-variant: '#39485a'
  tertiary-fixed: '#ffdcc5'
  tertiary-fixed-dim: '#ffb783'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#703700'
  background: '#111317'
  on-background: '#e2e2e8'
  surface-variant: '#333539'
  surface-deep: '#16191F'
  surface-muted: '#1E2229'
  border-subtle: '#2D333D'
  text-primary: '#F8FAFC'
  text-secondary: '#94A3B8'
  accent-purple-dim: '#312E81'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-h1:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-h2:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  headline-h3:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  page-padding-desktop: 40px
  page-padding-mobile: 24px
  card-padding-lg: 32px
  card-padding-md: 24px
  gutter: 24px
  sidebar-width: 260px
  content-max-width: 1200px
---

## Brand & Style

The design system is built for a premium, desktop-first personal library management experience. It is defined by a "Calm, Minimal, and Professional" aesthetic that distances itself from the cluttered utility of typical admin dashboards. Inspired by the focus-oriented interfaces of Linear and the refined reading experience of Apple Books, this system prioritizes craftsmanship and readability over decoration.

The visual style is **Minimalist** with a focus on **Tonal Layers**. It utilizes high-quality typography and generous whitespace to create a "quiet" interface. The mood is intellectual and focused, evoking the feeling of a well-curated physical library transformed into a digital sanctuary. Every decision is intentional, ensuring that the books—represented by large, high-fidelity covers—remain the primary visual anchor of the application.

## Colors

The color strategy is "Dark Mode First," employing a deep charcoal and gray palette to reduce eye strain and provide a sophisticated backdrop for book cover art. 

- **Neutral Dark Background:** Avoid pure black (`#000000`). Use a deep, saturated charcoal for the primary background to maintain depth.
- **Surface Tiers:** Use muted grays to differentiate between the persistent sidebar, main content area, and elevated cards.
- **Restrained Accent:** Purple is used strictly as a functional accent—denoting primary actions, progress indicators, or active states. It should never dominate the layout.
- **Contrast:** Typography should maintain high contrast against backgrounds, using off-whites and cool grays rather than pure white to preserve the calm atmosphere.

## Typography

The design system exclusively uses **Inter** to achieve a clean, systematic, and utilitarian look. Hierarchy is established through weight and letter spacing rather than relying solely on dramatic size changes.

- **Display Titles:** Should be large, breathable, and slightly tight in letter-spacing for a premium editorial feel.
- **Body Text:** Optimized for long-form reading with comfortable line heights (1.5x+). 
- **Labels:** Used for metadata and UI controls, often employing medium weights to distinguish from body copy without increasing size.
- **Restraint:** Avoid excessive use of bold text. Use "Medium" weights (500) for secondary emphasis.

## Layout & Spacing

The layout is **Desktop-First**, featuring a persistent left sidebar for navigation and a primary content area that values asymmetrical balance. 

- **Grid Model:** A flexible column system is used, but whitespace is the primary tool for separation. Content should never feel "boxed in."
- **Margins & Padding:** Large page titles should be accompanied by generous top and side padding (32–40px). 
- **Readable Width:** Text-heavy content (like book synopses) should be constrained to a maximum readable width to prevent line lengths from becoming too long.
- **Reflow:** On smaller viewports, the sidebar collapses into a bottom bar or hidden drawer, and grid columns for book covers reduce while maintaining the "Large Cover" priority.

## Elevation & Depth

Visual hierarchy is conveyed through **Tonal Layers** and **Subtle Shadows**. 

- **Layers:** The base background is the darkest layer. Surface containers (cards, sidebars) use slightly lighter grays to appear "lifted." 
- **Shadows:** Use extremely soft, large-radius shadows (e.g., 20-40px blur) with very low opacity (10-15%). Shadows should feel ambient rather than directional.
- **Borders:** Minimal use of borders. When necessary, use 1px solid lines with low-contrast colors (`border-subtle`). Prefer separation through tonal changes or whitespace.
- **Depth Focus:** The book covers themselves are the "highest" elements, utilizing slightly more pronounced shadows to feel tactile and physically present.

## Shapes

The shape language is **Rounded**, providing a soft, approachable feel that balances the technicality of the Inter typeface.

- **Standard Radius:** 0.5rem (8px) for most UI components including buttons, input fields, and smaller cards.
- **Large Radius:** 1rem (16px) for book covers and primary content containers to emphasize their importance.
- **Pill Shapes:** Used exclusively for tags, chips, and search bars to provide high contrast against the rectangular grid of book covers.

## Components

### Book Covers
The anchor of the system. Displayed in high aspect ratios with a `rounded-lg` radius and soft ambient shadows. No borders around the image itself.

### Buttons
- **Primary:** Purple background with white text. Rounded (0.5rem).
- **Secondary:** Ghost style with a subtle border or muted gray background. 
- **Sizes:** Prefer larger hit areas with generous horizontal padding.

### Cards
Containers for metadata or dashboard widgets. Use `card-padding-lg` (32px), minimal borders, and a tonal background slightly lighter than the page base. Never stack cards inside cards.

### Input Fields
Clean and understated. No heavy borders; use a subtle background fill and a change in border color (to purple) only on focus.

### Chips & Filters
Pill-shaped with medium-weight text. Active states use a subtle purple tint or solid fill to provide clear feedback.

### Progress Bars
Thin (4-6px) track with a solid purple fill. Used for reading progress and goals, avoiding distracting animations.