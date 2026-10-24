# DESIGN_SYSTEM.md

# Book Catalog --- Design System

**Version:** 1.0\
**Status:** Draft

> **Implemented theme (current).** The frontend ships the "Literary Noir" theme
> from `design/stitch/theme/DESIGN.md`; treat those mockups and tokens as
> authoritative where this draft is generic.
>
> - Surfaces: background `#111317`, surface `#16191F`, raised `#1E2024`,
>   border `#2D333D`
> - Text: primary `#F8FAFC`, muted `#94A3B8`, accent text `#C0C1FF`, accent fill
>   `#6A67F5`
> - Type: Inter for headings and body; tabular numbers for stats and progress
> - Shape: 12–16px radii, hairline borders, minimal shadow; content column
>   capped at 1240px with 40px page padding
> - Shell: 260px sidebar (Dashboard, Library, Tags, Reading, Import, Insights +
>   "Add New Book"), sticky topbar search routed to `/library?q=`, and a stacked
>   header below 900px
> - Dark theme only. Books without artwork get a generated typographic cover,
>   never an empty frame.
>
> All tokens and component classes live in `frontend/src/styles.css`.

------------------------------------------------------------------------

# 1. Design Philosophy

Book Catalog is a productivity application, not an online bookstore.

Core principles:

-   Clarity over decoration
-   Fast information discovery
-   Consistent interactions
-   Minimal visual noise
-   Accessible
-   Responsive
-   Dark mode first

------------------------------------------------------------------------

# 2. Visual Inspiration

-   Linear
-   Notion
-   Readwise
-   Arc Browser
-   GitHub
-   Apple Books (layout inspiration only)

Avoid: - Wooden bookshelf themes - Heavy gradients - Cartoon
illustrations - Skeuomorphic designs

------------------------------------------------------------------------

# 3. Color System

## Primary

-   Primary
-   Primary Hover
-   Primary Active

## Semantic

-   Success
-   Warning
-   Error
-   Info

## Surfaces

-   Background
-   Surface
-   Elevated Surface
-   Border

## Text

-   Primary
-   Secondary
-   Muted
-   Disabled

Support: - Light Theme - Dark Theme

------------------------------------------------------------------------

# 4. Typography

Recommended Font: - Inter

Scale

-   Display
-   H1
-   H2
-   H3
-   Body Large
-   Body
-   Small
-   Caption
-   Label

Guidelines

-   1.5 line height for body text
-   Bold only for emphasis
-   Left aligned content

------------------------------------------------------------------------

# 5. Spacing

Use an 8px spacing system.

Base scale:

4 8 12 16 24 32 40 48 64

------------------------------------------------------------------------

# 6. Layout

Desktop-first.

Navigation:

Persistent left sidebar.

Content:

Centered container with comfortable whitespace.

Cards are the primary layout element.

------------------------------------------------------------------------

# 7. Radius

Small Medium Large

Rounded but subtle.

------------------------------------------------------------------------

# 8. Shadows

Use soft elevation only.

Levels:

-   None
-   Small
-   Medium
-   Large

------------------------------------------------------------------------

# 9. Icons

Library:

Lucide Icons

Rules:

-   Outline icons
-   Consistent sizing
-   Avoid filled icon sets

------------------------------------------------------------------------

# 10. Buttons

Variants

-   Primary
-   Secondary
-   Outline
-   Ghost
-   Danger
-   Icon Button

States

-   Default
-   Hover
-   Active
-   Disabled
-   Loading

------------------------------------------------------------------------

# 11. Inputs

Components

-   Text Input
-   Search
-   Textarea
-   Dropdown
-   Multi-select
-   Date Picker
-   File Upload

Validation

-   Success
-   Warning
-   Error

------------------------------------------------------------------------

# 12. Cards

Reusable cards:

-   Book Card
-   Statistic Card
-   Insight Card
-   Recommendation Card
-   Chart Card

All cards should have consistent padding and spacing.

------------------------------------------------------------------------

# 13. Navigation

Sidebar items:

-   Dashboard
-   Library
-   Add Book
-   Insights
-   Search
-   Settings

Behavior:

-   Active state
-   Hover state
-   Collapsible in future

------------------------------------------------------------------------

# 14. Tables

Support:

-   Sorting
-   Filtering
-   Pagination
-   Row actions

------------------------------------------------------------------------

# 15. Charts

Preferred charts:

-   Bar
-   Line
-   Pie
-   Area
-   Heatmap

Charts should prioritize readability over decoration.

------------------------------------------------------------------------

# 16. Book Card Specification

Contains:

-   Cover
-   Title
-   Author
-   Rating
-   Reading Status
-   Tags

Hover actions:

-   View
-   Edit
-   Favorite

------------------------------------------------------------------------

# 17. Empty States

Create dedicated empty states for:

-   Empty Library
-   No Search Results
-   No Analytics
-   Upload Failure

Each should contain a helpful action.

------------------------------------------------------------------------

# 18. Loading States

Use:

-   Skeleton loaders
-   Progress indicators
-   Upload progress
-   Metadata lookup progress

------------------------------------------------------------------------

# 19. Accessibility

-   Keyboard navigation
-   Visible focus states
-   Semantic HTML
-   WCAG-aware contrast
-   Screen reader friendly labels

------------------------------------------------------------------------

# 20. Responsive Design

Desktop: Primary experience.

Tablet: Collapsible sidebar.

Mobile (future): Bottom navigation and simplified layouts.

------------------------------------------------------------------------

# 21. Motion

Animations should be subtle.

Recommended:

-   150--250ms transitions
-   Fade
-   Slide
-   Scale

Avoid excessive motion.

------------------------------------------------------------------------

# 22. Design Principles

Every screen should be:

-   Consistent
-   Minimal
-   Information-rich
-   Fast
-   Predictable
-   Easy to scan
-   Easy to extend

A user should be able to catalog a book, find it later, and discover
related books with the fewest possible interactions.
