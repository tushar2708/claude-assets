#!/usr/bin/env bash
# Install, update, or uninstall every claude-assets plugin and standalone skill.
#
#   curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude
#   curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --codex
#   ... bash -s -- --claude|--codex update|uninstall
#
# Env: CLAUDE_ASSETS_DIR (clone path, default ~/.claude-assets), DRY_RUN=1 (print only).
set -euo pipefail

REPO="tushar2708/claude-assets"
REPO_URL="https://github.com/${REPO}.git"
MARKETPLACE="claude-assets"
CLONE_DIR="${CLAUDE_ASSETS_DIR:-$HOME/.claude-assets}"
HOST="${1:-}"
MODE="${2:-install}"

log() { printf '==> %s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

run() {
  if [ "${DRY_RUN:-0}" = "1" ]; then
    printf '[dry-run] %s\n' "$*"
    return 0
  fi
  "$@"
}

require() {
  command -v "$1" >/dev/null 2>&1 || die "'$1' is not installed or not on PATH."
}

sync_clone() {
  if [ -d "$CLONE_DIR/.git" ]; then
    log "Updating $CLONE_DIR"
    run git -C "$CLONE_DIR" pull --ff-only --quiet
  elif [ -e "$CLONE_DIR" ]; then
    die "$CLONE_DIR exists and is not a git clone. Move it or set CLAUDE_ASSETS_DIR."
  else
    log "Cloning $REPO into $CLONE_DIR"
    run git clone --quiet "$REPO_URL" "$CLONE_DIR"
  fi
}

# Plugin names come from the marketplace file, the one source of truth.
plugin_names() {
  local manifest="$CLONE_DIR/.claude-plugin/marketplace.json"
  [ -f "$manifest" ] || die "Missing $manifest."
  grep -o '"\./plugins/[^"]*"' "$manifest" | sed -e 's|"\./plugins/||' -e 's|"$||'
}

install_claude_plugins() {
  log "Adding marketplace $REPO"
  run claude plugin marketplace add "$REPO"
  # Refresh the registry so it offers the latest commit, otherwise an
  # already-installed plugin would never see a newer version below.
  run claude plugin marketplace update "$MARKETPLACE" || true
  local name
  for name in $(plugin_names); do
    log "Installing plugin $name"
    # `install` exits 0 for an already-installed plugin without upgrading it,
    # so always follow with `update` to pull the newest marketplace commit.
    run claude plugin install "$name@$MARKETPLACE" --scope user || true
    log "Updating plugin $name"
    run claude plugin update "$name@$MARKETPLACE" || true
  done
}

update_claude_plugins() {
  log "Refreshing marketplace $MARKETPLACE"
  run claude plugin marketplace add "$REPO"
  run claude plugin marketplace update "$MARKETPLACE"
  local name
  for name in $(plugin_names); do
    log "Updating plugin $name"
    run claude plugin update "$name@$MARKETPLACE" \
      || run claude plugin install "$name@$MARKETPLACE" --scope user
  done
}

install_codex_plugins() {
  log "Adding Codex marketplace $REPO"
  # The Codex marketplace file lives in .agents/plugins, but its entries point at ./plugins/*.
  run codex plugin marketplace add "$REPO" --sparse .agents/plugins --sparse plugins
  local name
  for name in $(plugin_names); do
    log "Installing Codex plugin $name"
    run codex plugin add "$name@$MARKETPLACE"
  done
}

update_codex_plugins() {
  log "Refreshing Codex marketplace $MARKETPLACE"
  # Remove first: adding a marketplace that exists from another source fails.
  run codex plugin marketplace remove "$MARKETPLACE" || true
  run codex plugin marketplace add "$REPO" --sparse .agents/plugins --sparse plugins
  local name
  for name in $(plugin_names); do
    log "Updating Codex plugin $name"
    run codex plugin add "$name@$MARKETPLACE"
  done
}

uninstall_plugins() {
  local name
  if [ "$HOST" = "--claude" ]; then
    for name in $(plugin_names); do
      log "Uninstalling plugin $name"
      run claude plugin uninstall "$name@$MARKETPLACE" --scope user || true
    done
    run claude plugin marketplace remove "$MARKETPLACE" || true
  else
    for name in $(plugin_names); do
      log "Uninstalling Codex plugin $name"
      run codex plugin remove "$name@$MARKETPLACE" || true
    done
    run codex plugin marketplace remove "$MARKETPLACE" || true
  fi
}

# Each skill is a symlink into the clone, so a git pull updates it.
link_skills() {
  run mkdir -p "$SKILLS_DIR"
  local src name target
  for src in "$CLONE_DIR"/skills/*/; do
    [ -f "$src/SKILL.md" ] || continue
    src="${src%/}"
    name="$(basename "$src")"
    target="$SKILLS_DIR/$name"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$src" ]; then
      log "Skill $name is linked"
    elif [ -e "$target" ] || [ -L "$target" ]; then
      warn "Skipping skill $name: $target exists and is not managed here."
    else
      log "Linking skill $name"
      run ln -s "$src" "$target"
    fi
  done
}

# Remove links whose skill was deleted upstream.
prune_skills() {
  local link dest
  for link in "$SKILLS_DIR"/*; do
    [ -L "$link" ] || continue
    dest="$(readlink "$link")"
    case "$dest" in
      "$CLONE_DIR"/skills/*)
        if [ ! -e "$dest" ]; then
          log "Removing stale skill link $(basename "$link")"
          run rm "$link"
        fi
        ;;
    esac
  done
}

# Remove every skill link this script manages, whether or not upstream still has it.
unlink_skills() {
  local link
  for link in "$SKILLS_DIR"/*; do
    [ -L "$link" ] || continue
    case "$(readlink "$link")" in
      "$CLONE_DIR"/skills/*)
        log "Unlinking skill $(basename "$link")"
        run rm "$link"
        ;;
    esac
  done
}

main() {
  case "$HOST" in
    --claude | --codex) ;;
    "") die "Choose a host: --claude or --codex." ;;
    *) die "Unknown host '$HOST'. Use --claude or --codex." ;;
  esac
  case "$MODE" in
    install | update | uninstall) ;;
    *) die "Unknown mode '$MODE'. Use 'install', 'update', or 'uninstall'." ;;
  esac
  require git
  if [ "$HOST" = "--claude" ]; then
    require claude
    SKILLS_DIR="$HOME/.claude/skills"
  else
    require codex
    SKILLS_DIR="$HOME/.codex/skills"
  fi

  sync_clone
  if [ "$MODE" = "uninstall" ]; then
    uninstall_plugins
    unlink_skills
    log "Uninstalled. The clone at $CLONE_DIR was kept."
    return 0
  fi
  if [ "$HOST" = "--claude" ] && [ "$MODE" = "install" ]; then
    install_claude_plugins
  elif [ "$HOST" = "--claude" ]; then
    update_claude_plugins
  elif [ "$MODE" = "update" ]; then
    update_codex_plugins
  else
    install_codex_plugins
  fi
  link_skills
  prune_skills

  if [ "$HOST" = "--claude" ]; then
    log "Done. Restart Claude Code, or run /reload-plugins in a session."
  else
    log "Done. Start a new Codex session so it discovers the installed plugins and skills."
  fi
}

main "$@"
