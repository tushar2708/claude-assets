---
type: Index
title: Component Index
status: stable
tags:
- index
---

# Component Index

Last updated: <YYYY-MM-DD> (<one-line summary of the change>)

<!--
One INDEX.md per UI package root (each app, each shared component library).
One row per file. Sort rows alphabetically. Keep these sections and columns.
An empty directory gets one line: "`<dir>/` exists but holds no file."
Drop a section only when its directory does not exist.
-->

## Atoms (`components/atoms/`)

| File | Component(s) | Purpose |
|------|--------------|---------|
| <File>.tsx | <Component> | <what it renders, in one line> |

## Molecules (`components/molecules/`)

| File | Component(s) | Purpose | Composed From |
|------|--------------|---------|---------------|
| <File>.tsx | <Component> | <purpose> | <atoms and primitives it renders> |

## Organisms (`components/organisms/`)

| File | Component(s) | Purpose | Composed From |
|------|--------------|---------|---------------|
| <File>.tsx | <Component> | <purpose> | <molecules, atoms, primitives> |

### `components/organisms/<sub-directory>/`

<One or two lines: which component orchestrates, which ones are prop-driven.>

| File | Component(s) | Purpose | Composed From |
|------|--------------|---------|---------------|
| <File>.tsx | <Component> | <purpose> | <children> |

## Features (`components/features/`)

| File | Component(s) | Purpose | Composed From |
|------|--------------|---------|---------------|
| <File>.tsx | <Component> | <purpose> | <organisms, molecules> |
| <helper>.ts | — | <pure logic the features share> | — |

## Templates (`components/templates/`)

| File | Component(s) | Purpose | Composed From |
|------|--------------|---------|---------------|
| <Layout>.tsx | <Layout> | <regions it lays out> | <organisms, Outlet> |

## Shared UI library (`<path to the shared library>`)

These are consumed by more than one app and are NOT part of this app's component tree. Their inventory is `<path to the shared library>/INDEX.md`; check it before you add a component here.

## Pages (`pages/`)

| File | Component(s) | Route | Composed From |
|------|--------------|-------|---------------|
| <Page>.tsx | <Page> | `<route>` | <feature it renders> |

## Hooks (`hooks/`)

| File | Hook(s) | Purpose |
|------|---------|---------|
| <use-name>.ts | <useName> | <what it returns or syncs> |

## UI Primitives (`components/ui/`) — shadcn/ui

<comma-separated list of primitive file names>
