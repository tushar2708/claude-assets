---
type: explanation
title: Pipeline Overview
status: stable
tags: [pipeline, architecture]
stale_after: 2027-06-30
---

# Pipeline Overview

| Section | Purpose |
|---------|---------|
| [Entry Point](#entry-point) | How work items enter the pipeline |
| [Utilities](#utilities) | Helper code shared by the stages |

## Entry Point

The pipeline starts in `src/main.go`, where `src/main.go#HandleThing`
dispatches incoming work items to the processing stages.

## Utilities

Shared helpers live in the util package and are documented in the
reference section.
