"""
Hook registry for tracking enabled/disabled state.

Stores hook configurations in ~/.claude/hook_registry.json
Supports enabling/disabling hooks without modifying settings.json
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


REGISTRY_FILE = Path.home() / ".claude" / "hook_registry.json"


@dataclass
class HookEntry:
    """A registered hook entry."""

    name: str  # Unique hook name (e.g., "pretooluse_bash")
    script_path: str  # Path to Python script
    hook_type: str  # PreToolUse, PostToolUse, etc.
    matcher: str  # Tool matcher pattern (e.g., "Bash", "Edit|Write|MultiEdit")
    enabled: bool = True
    description: str = ""


@dataclass
class HookRegistry:
    """Registry of all managed hooks."""

    hooks: dict[str, HookEntry] = field(default_factory=dict)
    version: str = "1.0.0"


def _load_registry() -> HookRegistry:
    """Load registry from file."""
    if REGISTRY_FILE.exists():
        try:
            data = json.loads(REGISTRY_FILE.read_text())
            hooks = {}
            for name, entry_data in data.get("hooks", {}).items():
                hooks[name] = HookEntry(
                    name=entry_data.get("name", name),
                    script_path=entry_data.get("script_path", ""),
                    hook_type=entry_data.get("hook_type", ""),
                    matcher=entry_data.get("matcher", ""),
                    enabled=entry_data.get("enabled", True),
                    description=entry_data.get("description", ""),
                )
            return HookRegistry(
                hooks=hooks,
                version=data.get("version", "1.0.0"),
            )
        except (json.JSONDecodeError, OSError):
            pass
    return HookRegistry()


def _save_registry(registry: HookRegistry) -> None:
    """Save registry to file."""
    data = {
        "version": registry.version,
        "hooks": {
            name: {
                "name": entry.name,
                "script_path": entry.script_path,
                "hook_type": entry.hook_type,
                "matcher": entry.matcher,
                "enabled": entry.enabled,
                "description": entry.description,
            }
            for name, entry in registry.hooks.items()
        },
    }
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, indent=2))


def register_hook(
    name: str,
    script_path: str,
    hook_type: str,
    matcher: str,
    description: str = "",
    enabled: bool = True,
) -> HookEntry:
    """Register a new hook or update existing."""
    registry = _load_registry()
    entry = HookEntry(
        name=name,
        script_path=script_path,
        hook_type=hook_type,
        matcher=matcher,
        enabled=enabled,
        description=description,
    )
    registry.hooks[name] = entry
    _save_registry(registry)
    return entry


def get_hook(name: str) -> Optional[HookEntry]:
    """Get a hook by name."""
    registry = _load_registry()
    return registry.hooks.get(name)


def list_hooks() -> list[HookEntry]:
    """List all registered hooks."""
    registry = _load_registry()
    return list(registry.hooks.values())


def enable_hook(name: str) -> bool:
    """Enable a hook. Returns True if found and updated."""
    registry = _load_registry()
    if name in registry.hooks:
        registry.hooks[name].enabled = True
        _save_registry(registry)
        return True
    return False


def disable_hook(name: str) -> bool:
    """Disable a hook. Returns True if found and updated."""
    registry = _load_registry()
    if name in registry.hooks:
        registry.hooks[name].enabled = False
        _save_registry(registry)
        return True
    return False


def is_hook_enabled(name: str) -> bool:
    """Check if a hook is enabled."""
    registry = _load_registry()
    entry = registry.hooks.get(name)
    return entry.enabled if entry else False


def unregister_hook(name: str) -> bool:
    """Remove a hook from registry. Returns True if found and removed."""
    registry = _load_registry()
    if name in registry.hooks:
        del registry.hooks[name]
        _save_registry(registry)
        return True
    return False
