# Claude Code Adapter: Enable or Disable Rules

This adapter applies only to the shared hook scripts under `~/.claude/hooks/`.

Each script has a `RULE_ENABLED` map such as:

```python
RULE_ENABLED = {
    "git-checkout": True,
    "git-add-all": True,
}
```

Toggle a single rule by changing its value from `True` to `False` or back. Do not edit `~/.claude/settings.json`; this operation does not add, remove, or disable a registered hook script.

Common Bash rule identifiers include `git-checkout`, `git-add-all`, `git-no-verify`, `git-destructive`, `git-stash`, `go-direct`, `rm-command`, `sed-command`, `npm-no-save`, and `pip-uv-direct`. File hooks include `autogen-files`; post-file checks include `python-syntax` and `python-local-imports`.

Inspect `pretooluse_bash.py`, `pretooluse_file.py`, and `posttooluse_file.py` before changing a value. Verify the final map after editing. If a request such as “disable all git hooks” matches several identifiers, obtain explicit confirmation before toggling them.
