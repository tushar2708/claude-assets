#!/usr/bin/env bash
# Install or update every claude-assets plugin and skill for Claude Code.
#
#   curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- update
#
# Env: CLAUDE_ASSETS_DIR (clone path, default ~/.claude-assets), DRY_RUN=1 (print only).
set -euo pipefail

REPO="tushar2708/claude-assets"
REPO_URL="https://github.com/${REPO}.git"
MARKETPLACE="claude-assets"
CLONE_DIR="${CLAUDE_ASSETS_DIR:-$HOME/.claude-assets}"
SKILLS_DIR="$HOME/.claude/skills"
MODE="${1:-install}"

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

install_plugins() {
  log "Adding marketplace $REPO"
  run claude plugin marketplace add "$REPO"
  local name
  for name in $(plugin_names); do
    log "Installing plugin $name"
    run claude plugin install "$name@$MARKETPLACE" --scope user \
      || run claude plugin update "$name@$MARKETPLACE"
  done
}

update_plugins() {
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

main() {
  case "$MODE" in
    install | update) ;;
    *) die "Unknown mode '$MODE'. Use 'install' or 'update'." ;;
  esac
  require git
  require claude

  sync_clone
  if [ "$MODE" = "install" ]; then
    install_plugins
  else
    update_plugins
  fi
  link_skills
  prune_skills

  log "Done. Restart Claude Code, or run /reload-plugins in a session."
}

main "$@"
