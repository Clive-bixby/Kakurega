# COMPONENTS.md

# Book Catalog --- UI Components

**Version:** 1.0\
**Status:** Draft

------------------------------------------------------------------------

# Purpose

This document defines reusable UI components used throughout the
application. Components should be composable, accessible, responsive,
and consistent with the design system.

------------------------------------------------------------------------

# Component Principles

-   Reusable
-   Stateless when possible
-   Accessible
-   Responsive
-   Consistent spacing
-   Keyboard friendly

------------------------------------------------------------------------

# 1. Sidebar

## Purpose

Primary application navigation.

## Items

-   Dashboard
-   Library
-   Add Book
-   Insights
-   Search
-   Settings

## States

-   Default
-   Hover
-   Active
-   Collapsed (future)

------------------------------------------------------------------------

# 2. Top Navigation

Contains:

-   Search
-   Notifications (future)
-   Theme Toggle
-   User Menu (future)

------------------------------------------------------------------------

# 3. Book Card

## Displays

-   Cover
-   Title
-   Author
-   Rating
-   Reading Status
-   Tags

## Actions

-   View
-   Edit
-   Favorite

## States

-   Default
-   Hover
-   Selected

------------------------------------------------------------------------

# 4. Book Grid

Displays multiple Book Cards.

Supports:

-   Grid/List toggle
-   Infinite scroll (future)
-   Pagination

------------------------------------------------------------------------

# 5. Search Bar

Supports:

-   Instant search
-   Suggestions
-   Keyboard shortcuts
-   Clear button

------------------------------------------------------------------------

# 6. Filter Panel

Filters:

-   Author
-   Genre
-   Publisher
-   Year
-   Rating
-   Reading Status
-   Tags
-   Favorites

------------------------------------------------------------------------

# 7. Sort Menu

Options:

-   Recently Added
-   Title A--Z
-   Author
-   Rating
-   Publication Year

------------------------------------------------------------------------

# 8. Metadata Panel

Displays:

-   ISBN
-   Publisher
-   Language
-   Pages
-   Publication Year
-   Genres
-   Description

Read-only by default.

------------------------------------------------------------------------

# 9. Reading Progress

Displays:

-   Progress Bar
-   Percentage
-   Status

Statuses:

-   Unread
-   Reading
-   Completed

------------------------------------------------------------------------

# 10. Notes Panel

Supports:

-   Rich text (future)
-   Plain text
-   Auto-save (future)

------------------------------------------------------------------------

# 11. Tags

Functions:

-   Add
-   Remove
-   Filter

Variants:

-   Default
-   Selected

------------------------------------------------------------------------

# 12. Recommendation Card

Displays:

-   Cover
-   Title
-   Author
-   Match Reason

Types:

-   In Library
-   Recommended
-   Same Author
-   Same Series

------------------------------------------------------------------------

# 13. Statistic Card

Examples:

-   Total Books
-   Read
-   Unread
-   Favorites

------------------------------------------------------------------------

# 14. Chart Card

Wraps analytics charts.

Supported:

-   Bar
-   Pie
-   Line
-   Area
-   Heatmap

------------------------------------------------------------------------

# 15. Upload Area

Supports:

-   Drag & Drop
-   Browse
-   Camera (future)

States:

-   Empty
-   Uploading
-   Success
-   Error

------------------------------------------------------------------------

# 16. Progress Stepper

Pipeline:

Upload

↓

Barcode

↓

OCR

↓

Metadata

↓

Review

↓

Save

------------------------------------------------------------------------

# 17. Buttons

Variants:

-   Primary
-   Secondary
-   Outline
-   Ghost
-   Danger
-   Icon

States:

-   Default
-   Hover
-   Active
-   Disabled
-   Loading

------------------------------------------------------------------------

# 18. Dialogs

Reusable dialogs:

-   Delete Confirmation
-   Edit Book
-   Import
-   Export

------------------------------------------------------------------------

# 19. Toast Notifications

Types:

-   Success
-   Error
-   Warning
-   Info

Position:

Top-right

------------------------------------------------------------------------

# 20. Empty State

Includes:

-   Illustration/Icon
-   Message
-   Primary Action

Examples:

-   Empty Library
-   No Search Results
-   No Recommendations

------------------------------------------------------------------------

# 21. Skeleton Loader

Used while loading:

-   Book Cards
-   Metadata
-   Charts
-   Tables

------------------------------------------------------------------------

# 22. Responsive Behavior

Desktop: Full sidebar and multi-column layouts.

Tablet: Collapsible sidebar.

Mobile (future): Bottom navigation and simplified cards.

------------------------------------------------------------------------

# Component Naming

Examples:

-   BookCard
-   BookGrid
-   Sidebar
-   SearchBar
-   FilterPanel
-   MetadataPanel
-   RecommendationCard
-   StatisticCard
-   ChartCard
-   UploadArea
-   ProgressStepper
-   EmptyState
-   SkeletonLoader

------------------------------------------------------------------------

# Development Guidelines

-   Build components as independent reusable units.
-   Avoid page-specific logic inside components.
-   Prefer composition over inheritance.
-   Keep props minimal and well typed.
-   Follow the design system for colors, spacing, typography, and
    interactions.
