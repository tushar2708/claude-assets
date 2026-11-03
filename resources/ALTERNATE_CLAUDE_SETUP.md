# Alternate Claude Code setup — OpenRouter with open-weight models

A second Claude Code configuration that routes every model slot to an open-weight model through OpenRouter,
instead of to Anthropic. The alias is `cldo`, defined in `~/.bash_aliases`:

```sh
alias cldo='claude --settings ~/.claude_or/settings.json'
alias clddo='cldo --dangerously-skip-permissions'
```

`cldo` passes `--settings`, which does **not** change `CLAUDE_CONFIG_DIR`. The session still runs out of
`~/.claude`, so anything the `--settings` file does not override is inherited from the main config.

## Final model mapping

| Slot | Model | In $/M | Out $/M | Cache read $/M | Cache disc | Context |
|---|---|---|---|---|---|---|
| Haiku | `qwen/qwen3.7-flash` | $0.030 | $0.130 | $0.006 | 80% | 1,000,000 |
| Sonnet | `deepseek/deepseek-v4.1-flash` | $0.045 | $0.500 | $0.006 | 87% | 1,048,576 |
| Opus | `z-ai/glm-5.3-flashx` | $0.370 | $1.250 | $0.075 | 80% | 1,048,576 |
| Fable | `deepseek/deepseek-v4-pro-0813` | $0.115 | $4.000 | $0.110 | 4% | 1,048,576 |

Every model is ≥1M context and every one has a cache-read price. Cache reads dominate the bill in Claude Code,
because the whole conversation is re-sent on every turn.

## Cost model used throughout

```
session cost = 1M fresh input + 10M cache reads + 200K output
```

| Slot | Model | Session cost |
|---|---|---|
| Haiku | `qwen/qwen3.7-flash` | **$0.116** |
| Sonnet | `deepseek/deepseek-v4.1-flash` | **$0.205** |
| Opus | `z-ai/glm-5.3-flashx` | **$1.370** |
| Fable | `deepseek/deepseek-v4-pro-0813` | **$2.015** |

Cost and measured capability both rise across the four tiers, so the ladder is internally consistent.

## Benchmarks

| Slot | Model | SWE-bench Verified | Source quality |
|---|---|---|---|
| Haiku | `qwen/qwen3.7-flash` | 64.4% | cited, unconfirmed |
| Sonnet | `deepseek/deepseek-v4.1-flash` | — | no score published by any source |
| Opus | `z-ai/glm-5.3-flashx` | 92.0% | Vals AI, measured (one outlier reports 63%) |
| Fable | `deepseek/deepseek-v4-pro-0813` | 96.4% | Vals AI, measured |

SWE-bench Verified is saturated and was archived by Vals AI on 2026-09-01. Ranks 2–6 span less than one
point, so treat closely-ranked models as tied. The Sonnet slot is the one unverified link in the chain.

## Alternates considered

| Slot | Model | Session | Cache disc | SWE-bench | Why not chosen |
|---|---|---|---|---|---|
| Haiku | `anthropic/claude-haiku-5.5` | $0.300 | 90% | 64.8% (Pro, vendor) | Real Haiku via OpenRouter; costs 2.6x the pick |
| Haiku | `qwen/qwen3.5-flash-02-23` | $0.117 | 100% | 64.4% | Cache reads free, but only half the cache discount of the pick in practice |
| Sonnet | `deepseek/deepseek-v4-flash-0731` | $0.405 | 80% | 88.8% (measured) | 2x the pick's cost, but the only Sonnet-priced model with a measured score |
| Opus | `qwen/qwen3.8-27b` | $0.900 | 75% | 86.0% (measured) | Undisputed data; lower score than the pick |
| Opus | `z-ai/glm-5.3` | $1.560 | **5%** | 95.4% (measured) | Best score, but almost no cache discount |
| Opus | `minimax/minimax-m3` | $1.140 | 80% | 80.5% (vendor) | Vendor-reported only |
| Fable | `deepseek/deepseek-v4-pro` | $3.590 | 92% | 96.4% | Good cache discount, but 14x the input price of the `-0813` snapshot |

### Rejected outright

| Model | Reason |
|---|---|
| `z-ai/glm-5.3-flash` | **0% cache discount** — cached reads cost full input price |
| `moonshotai/kimi-k3` | 5.2% cache discount |
| `x-ai/grok-4.6` | 500K context, below the 1M requirement |
| `meta/muse-spark-1.2` | 86.6% measured but $3.60/session — worst value on the board |
| `meta/muse-spark-1.3-contributor` | $0.16/session but **no benchmark anywhere**, and marketed as a contributor/experimentation tier |
| `meta/muse-glimmer-30b` | 131K context |

## The `models` array alone is not enough — you must also override `modelPicker`

Adding a `models` array is not sufficient. Most main `~/.claude/settings.json` files define a `modelPicker`
block. Claude Code reads `modelPicker` from the highest-priority source that defines it, and it **never
merges rows from two sources** (source: [settings reference](https://code.claude.com/docs/en/settings-reference#modelpicker)).

This matters because `--settings` does **not** change `CLAUDE_CONFIG_DIR`. The session still runs out of
`~/.claude`, so `~/.claude/settings.json` is loaded and its `modelPicker` stays in force. If the alternate
file leaves `modelPicker` unset, the main file's `modelPicker` wins: the picker lists the Claude models, and
picking one sends a Claude model ID to OpenRouter.

So the alternate file must define **both** the `models` array **and** the `modelPicker` block. Overriding
only `ANTHROPIC_DEFAULT_*_MODEL`, or adding only a `models` array, leaves the main `modelPicker` in control.

### The one-message $3 mistake

I hit this the hard way. I had configured the `models` array and the `ANTHROPIC_DEFAULT_*_MODEL` variables,
but I had not added `modelPicker`. The picker therefore still offered the main file's rows. I picked "Fable"
and the picker sent `claude-opus-5-5`, not `deepseek/deepseek-v4-pro-0813`. Through OpenRouter that single
message was billed at Anthropic's rate — roughly **$3 for one message**. Adding the `modelPicker` block shown
below fixed it.

### Safest option: disable the Anthropic provider in OpenRouter

The settings-file fix is client-side. The client decides what to send; the settings only steer it, and a
config that is missing a key silently falls back to the main file. The server-side backstop is to disable
Anthropic as a provider in your OpenRouter account settings, if no other tool needs it. Then a stray Claude
model ID cannot route at all — the request is refused instead of billed.

## Recommended `settings.json`

The example below carries both `modelPicker` and `models`, each with the marker that identifies it in the
picker.

```json
{
  "includeCoAuthoredBy": false,
  "modelPicker": {
    "options": [
      { "model": "qwen/qwen3.7-flash[1m]",            "label": "Haiku (qwen/qwen3.7-flash)",  "description": "Qwen3.7 Flash via OpenRouter, 1M context" },
      { "model": "deepseek/deepseek-v4.1-flash[1m]",  "label": "Sonnet (deepseek/deepseek-v4.1-flash)", "description": "DeepSeek V4.1 Flash via OpenRouter, 1M context" },
      { "model": "z-ai/glm-5.3-flashx[1m]",           "label": "Opus (z-ai/glm-5.3-flashx)",   "description": "GLM-5.3 FlashX via OpenRouter, 1M context" },
      { "model": "deepseek/deepseek-v4-pro-0813[1m]", "label": "Fable (deepseek/deepseek-v4-pro-0813)",  "description": "DeepSeek V4 Pro 0813 via OpenRouter, 1M context" }
    ],
    "replaceBuiltInOptions": true
  },
  "models": [
    {
      "id": "qwen/qwen3.7-flash",
      "name": "Qwen3.7 Flash [1M]",
      "description": "Alibaba open-weight flash model via OpenRouter; 1M context; 80% cache discount; $0.030 in / $0.130 out per M tokens"
    },
    {
      "id": "deepseek/deepseek-v4.1-flash",
      "name": "DeepSeek V4.1 Flash [1M]",
      "description": "DeepSeek open-weight workhorse via OpenRouter; 1M context; 87% cache discount; $0.045 in / $0.500 out per M tokens"
    },
    {
      "id": "z-ai/glm-5.3-flashx",
      "name": "GLM-5.3 FlashX [1M]",
      "description": "Z.ai open-weight frontier-class model via OpenRouter; 1M context; 80% cache discount; 92.0% SWE-bench Verified; ~200 tok/s"
    },
    {
      "id": "deepseek/deepseek-v4-pro-0813",
      "name": "DeepSeek V4 Pro 0813 [1M]",
      "description": "DeepSeek open-weight frontier model via OpenRouter; 1M context; 96.4% SWE-bench Verified; 4% cache discount"
    }
  ],
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_AUTH_TOKEN": "<openrouter key>",
    "DISABLE_TELEMETRY": "1",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "85",

    "CLAUDE_CODE_ENABLE_TODO_TOOLS": "1",
    "CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION": "500",
    "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "50",

    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "qwen/qwen3.7-flash[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME": "Qwen3.7 Flash",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_DESCRIPTION": "Cheap 1M-context model, 80% cache discount",
    "ANTHROPIC_DEFAULT_HAIKU_MAX_TOKENS": 1000000,

    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek/deepseek-v4.1-flash[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME": "DeepSeek V4.1 Flash",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_DESCRIPTION": "Cheap workhorse, 87% cache discount",
    "ANTHROPIC_DEFAULT_SONNET_MAX_TOKENS": 1000000,

    "ANTHROPIC_DEFAULT_OPUS_MODEL": "z-ai/glm-5.3-flashx[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME": "GLM-5.3 FlashX",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_DESCRIPTION": "Frontier-class, 80% cache discount",
    "ANTHROPIC_DEFAULT_OPUS_MAX_TOKENS": 1000000,

    "ANTHROPIC_DEFAULT_FABLE_MODEL": "deepseek/deepseek-v4-pro-0813[1m]",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_NAME": "DeepSeek V4 Pro",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_DESCRIPTION": "Highest measured score, 4% cache discount",
    "ANTHROPIC_DEFAULT_FABLE_MAX_TOKENS": 1000000
  },
  "attribution": {
    "commit": "",
    "pr": "",
    "sessionUrl": false
  },
  "includeCoAuthoredBy": false,
  "permissions": {
    "allow": ["Read", "Grep", "Glob", "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)"],
    "deny": ["Bash(rm:*)", "Bash(git reset:*)", "Bash(git checkout:*)", "Bash(git stash:*)"],
    "ask": ["Bash(git add:*)", "Bash(git commit:*)", "Bash(git push:*)"],
    "defaultMode": "auto"
  },
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  },
  "effortLevel": "medium",
  "tui": "fullscreen",
  "verbose": true,
  "theme": "dark-daltonized",
  "voiceEnabled": true,
  "fileCheckpointingEnabled": false,
  "skipDangerousModePermissionPrompt": true,
  "skipWorkflowUsageWarning": true
}
```

`[1m]` is a Claude Code context annotation only. It is stripped before the request is sent, so it does not
affect routing. It is safe to apply to all four because all four are ≥1M context.

## Recommended base settings

The keys below are not about model routing. They are the settings that make an alternate setup behave like a
normal one. An alternate profile that only sets `ANTHROPIC_BASE_URL` and the four model slots will still show
Claude attribution in commits and still report telemetry, because the default for both is on.

| Key | Value | Effect |
|---|---|---|
| `attribution` | `{"commit":"", "pr":"", "sessionUrl":false}` | Stops Claude being added to commit messages and pull requests, and stops session URLs being attached. Empty strings are how you clear the attribution text. |
| `includeCoAuthoredBy` | `false` | Drops the `Co-Authored-By` trailer. Older key; keep both it and `attribution` to be safe. |
| `DISABLE_TELEMETRY` | `"1"` | Turns telemetry off. |
| `CLAUDE_CODE_ENABLE_TODO_TOOLS` | `"1"` | **Enables the task system.** Without it the `TaskCreate` / `TaskUpdate` / `TaskList` tools are unavailable. |
| `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` | `"500"` | Total subagents a session may spawn. |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | `"50"` | How many may run at once. |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `"85"` | Percentage of the context window at which auto-compaction fires. Raise it if you want to use more of a 1M window before compaction. |
| `permissions` | allow / deny / ask / `defaultMode` | Pre-approves commands so you are not prompted repeatedly. Tune to taste — the sample above is a starting point, not a recommendation. |
| `statusLine` | `{"type":"command","command":"..."}` | Custom status line. Point it at your own script. |
| `effortLevel` | `"medium"` | Default reasoning effort. Can be overridden per model via `modelSettings`. |
| `tui` | `"fullscreen"` | Interface mode. |
| `verbose` | `true` | Verbose output. |
| `theme` | `"dark-daltonized"` | Colour theme. Use whichever you prefer. |
| `voiceEnabled` | `true` | Enables voice input. |
| `fileCheckpointingEnabled` | `false` | Turns file checkpointing off. |
| `skipDangerousModePermissionPrompt` | `true` | Skips the warning prompt when launching with `--dangerously-skip-permissions`. |
| `skipWorkflowUsageWarning` | `true` | Skips the workflow usage warning. |

### Do not copy hooks into an alternate settings file

Hooks are deliberately excluded above. `--settings` does not change `CLAUDE_CONFIG_DIR`, so
`~/.claude/settings.json` is still loaded for the session and its hooks already run. Redefining the same hook
events in the alternate file risks each one executing twice — double notifications, double reminders, and any
side-effecting hook run twice.

If you do want an alternate profile to own its own hooks, move them out of `~/.claude/settings.json` rather
than defining them in both, so exactly one file owns each event.

## Sources

Prices are from the OpenRouter API, fetched 2026-11-03. Model pages:

| Model | OpenRouter page |
|---|---|
| `qwen/qwen3.7-flash` | https://openrouter.ai/qwen/qwen3.7-flash |
| `deepseek/deepseek-v4.1-flash` | https://openrouter.ai/deepseek/deepseek-v4.1-flash |
| `z-ai/glm-5.3-flashx` | https://openrouter.ai/z-ai/glm-5.3-flashx |
| `deepseek/deepseek-v4-pro-0813` | https://openrouter.ai/deepseek/deepseek-v4-pro-0813 |
| `deepseek/deepseek-v4-flash-0731` | https://openrouter.ai/deepseek/deepseek-v4-flash-0731 |
| `qwen/qwen3.8-27b` | https://openrouter.ai/qwen/qwen3.8-27b |
| `z-ai/glm-5.3` | https://openrouter.ai/z-ai/glm-5.3 |
| `minimax/minimax-m3` | https://openrouter.ai/minimax/minimax-m3 |
| `anthropic/claude-haiku-5.5` | https://openrouter.ai/anthropic/claude-haiku-5.5 |

Other links:

- All models (open-weight and proprietary, filterable): https://openrouter.ai/models
- Machine-readable catalogue: https://openrouter.ai/api/v1/models
- Per-provider prices for one model: https://openrouter.ai/api/v1/models/z-ai/glm-5.3-flashx/endpoints
- Benchmarks (not OpenRouter — they publish none): https://www.vals.ai/benchmarks/swebench
- Artificial Analysis: https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index

## Caveats

- **One price per model is misleading.** OpenRouter routes across many upstream providers, each with its own
  price. `deepseek/deepseek-v4.1-flash` has 41 providers ranging $0.035–$0.450 input and $0.139–$1.800
  output. The table above uses the representative price. Pin your routing preference if you need a specific rate.
- **Cache read is the number that matters.** A cheap input price with no cache discount loses to a dearer
  input price with a steep one, once cache reads dominate. This is why `z-ai/glm-5.3-flash` was rejected.
- **`-0813` and undated IDs are different models.** `deepseek/deepseek-v4-pro-0813` is $0.115/$4.00 with a 4%
  cache discount; `deepseek/deepseek-v4-pro` is $1.60/$3.20 with 92%. Same for `v4-flash` vs `v4.1-flash`.
- **The Opus pick has disputed data.** One source reports `z-ai/glm-5.3-flashx` at 63% on SWE-bench Verified
  where three others report 92%. Unresolved.
- **The Sonnet slot has no benchmark.** `deepseek/deepseek-v4.1-flash` publishes no SWE-bench Verified score
  from any source. Treat it as unmeasured.
- **The Haiku slot is not only summarisation.** It also backs Claude Code's auto-mode classifier, which decides
  permission prompts. Combined with `--dangerously-skip-permissions`, a weaker model there changes permission
  behaviour.
