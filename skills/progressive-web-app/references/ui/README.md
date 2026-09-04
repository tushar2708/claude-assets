# Bundled shadcn/ui primitives (Level 1 dependency)

The Level 1 responsive rules in `../../SKILL.md` build on a small set of **standard shadcn/ui**
primitives. They are bundled here so the skill is **self-sufficient in any project** — nothing is
specific to the codebase this skill was extracted from. Every file is unmodified shadcn/ui and
imports the others only by relative path (`./x`) plus npm packages, so the folder is self-contained.

## What's here

| File | Exports the responsive rules use |
|---|---|
| `sidebar.tsx` | `SidebarProvider`, `Sidebar`, `SidebarTrigger`, `SidebarInset`, `SidebarHeader`, `SidebarContent`, `SidebarFooter`, `SidebarGroup`, `SidebarGroupLabel`, `SidebarGroupContent`, `SidebarMenu`, `SidebarMenuItem`, `SidebarMenuButton`, `useSidebar` |
| `sheet.tsx` | `Sheet`, `SheetTrigger`, `SheetContent`, `SheetHeader`, `SheetTitle`, `SheetClose` |
| `drawer.tsx` | `Drawer`, `DrawerContent`, `DrawerHeader`, `DrawerTitle`, `DrawerDescription`, `DrawerFooter` (Vaul-based) |
| `dialog.tsx` | `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter` |
| `use-mobile.ts` | `useIsMobile()` — flips at **768px** (the `md` breakpoint), used for the sidebar off-canvas switch and the Dialog↔Drawer branch |
| `utils.ts` | `cn()` (clsx + tailwind-merge) |
| `button.tsx`, `input.tsx`, `separator.tsx`, `skeleton.tsx`, `tooltip.tsx` | peer components that `sidebar.tsx` imports |

## Getting them into a project (two options)

1. **shadcn CLI (recommended):**
   ```bash
   npx shadcn@latest add sidebar sheet drawer dialog button input separator skeleton tooltip
   ```
   This also generates the `use-mobile` hook and `lib/utils` (`cn`).

2. **Copy these files** into your `components/ui/` folder. They resolve each other by relative
   import (`./utils`, `./use-mobile`, `./button`, …), so no path edits are needed *between* them.
   If your project keeps `cn` at `@/lib/utils` (the shadcn default) rather than `./utils`, update
   the `cn` import line in each file to match.

## npm peer dependencies

`@radix-ui/react-dialog`, `@radix-ui/react-slot`, `@radix-ui/react-separator`,
`@radix-ui/react-tooltip`, `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-react`,
`vaul`. Requires **Tailwind** + the shadcn design tokens / CSS variables.
