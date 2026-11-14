#!/usr/bin/env bash
# Install or uninstall every claude-assets plugin and standalone skill. Install is a clean reinstall: run it again to update.
#
#   curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude
#   curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --codex
#   ... bash -s -- --claude|--codex uninstall
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

# The clone is a mirror, never a working copy. Match the remote exactly, so a rewritten upstream history cannot block a run.
sync_clone() {
  if [ -d "$CLONE_DIR/.git" ]; then
    log "Resetting $CLONE_DIR to $REPO main"
    run git -C "$CLONE_DIR" fetch --quiet "$REPO_URL" main
    run git -C "$CLONE_DIR" checkout --quiet --force -B main FETCH_HEAD
    run git -C "$CLONE_DIR" clean --quiet -fdx
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

# Remove every plugin and the marketplace. An optional flag, such as --keep-data, is passed to `plugin uninstall`.
remove_claude_plugins() {
  local name
  for name in $(plugin_names); do
    log "Uninstalling plugin $name"
    run claude plugin uninstall "$name@$MARKETPLACE" --scope user ${1:+"$1"} || true
  done
  run claude plugin marketplace remove "$MARKETPLACE" || true
}

# A clean reinstall: safe on a fresh machine, on an existing install, and when new plugins were added upstream.
install_plugins() {
  local name
  if [ "$HOST" = "--claude" ]; then
    # Remove, then add: a fresh marketplace clone cannot be broken by a rewritten upstream history.
    # --keep-data keeps each plugin's saved data in ~/.claude/plugins/data.
    remove_claude_plugins --keep-data
    log "Adding marketplace $MARKETPLACE"
    run claude plugin marketplace add "$REPO"
    for name in $(plugin_names); do
      log "Installing plugin $name"
      run claude plugin install "$name@$MARKETPLACE" --scope user
    done
  else
    # Remove, then add: Codex refuses to add a marketplace that exists from another source.
    log "Adding Codex marketplace $REPO"
    run codex plugin marketplace remove "$MARKETPLACE" || true
    # The Codex marketplace file lives in .agents/plugins, but its entries point at ./plugins/*.
    run codex plugin marketplace add "$REPO" --sparse .agents/plugins --sparse plugins
    for name in $(plugin_names); do
      log "Installing Codex plugin $name"
      run codex plugin add "$name@$MARKETPLACE"
    done
  fi
}

uninstall_plugins() {
  local name
  if [ "$HOST" = "--claude" ]; then
    remove_claude_plugins
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
    install | uninstall) ;;
    *) die "Unknown mode '$MODE'. Use 'install' or 'uninstall'." ;;
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
  install_plugins
  unlink_skills
  link_skills

  if [ "$HOST" = "--claude" ]; then
    log "Done. Restart Claude Code, or run /reload-plugins in a session."
  else
    log "Done. Start a new Codex session so it discovers the installed plugins and skills."
  fi
}

main "$@"
