# myhooks

myhooks is a Claude Code and Codex plugin for managing Claude Code hook rules. It gives you three skills to set up
the hooks system, add or change a rule, and switch individual rules on or off, without hand-editing hook scripts or
registration.

| Section | What it covers |
|---|---|
| [Install](#install) | Adding the plugin |
| [Skills](#skills) | What each skill does and when to call it |
| [Hook exit codes](#hook-exit-codes) | What a rule's result means |
| [Codex](#codex) | What happens in Codex |

## Install

The plugin ships in the `claude-assets` marketplace. Install it with the repository installer, which installs every
plugin:

```sh
curl -fsSL https://raw.githubusercontent.com/tushar2708/claude-assets/main/install.sh | bash -s -- --claude
```

To install only this plugin, add the marketplace once and install the plugin:

```sh
claude plugin marketplace add tushar2708/claude-assets
claude plugin install myhooks@claude-assets --scope user
```

Restart Claude Code or run `/reload-plugins` afterwards.

## Skills

Every skill runs only when you invoke it. None of them runs on its own.

| Skill | Use it to |
|---|---|
| `/myhooks:setup` | Set up the hooks system, reinstall it after a code change, verify it, or run its tests. The skill asks which of these you want. |
| `/myhooks:add-update` | Add a new hook rule, or change an existing one. The skill first reviews the registered hooks and asks you to confirm the scope, the action, the pattern and the test evidence. |
| `/myhooks:enable-disable` | Turn one hook rule on or off. The skill changes only that rule's flag and leaves the hook registration and the rest of the script alone. |

A typical change: run `/myhooks:add-update` to add a rule, then `/myhooks:setup` to verify it. Use
`/myhooks:enable-disable` to pause a rule without removing it.

## Hook exit codes

A hook rule reports one of three results:

| Exit code | Meaning |
|---|---|
| `0` | Allow, or the step succeeded |
| `1` | Warning, not blocking |
| `2` | Block |

A rule is verified only when the plugin has run it. The skills do not claim a rule works until that check passes.

## Codex

Codex has no equivalent of Claude Code's hook events, so these skills cannot register a hook there. In Codex, each
skill explains this and offers a portable alternative instead:

- a rule in the repository's `AGENTS.md`;
- a checked-in pre-commit hook, CI check or Makefile target; or
- a GitHub issue that describes the lifecycle event you need.
