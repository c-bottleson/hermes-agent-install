# Captain Architecture — Constitution + Protocol

## The Problem We Solved

Previous Captain instances had project-specific instructions baked into their SOUL.md ("work on SingItNow," "report on GoTrader"). This meant:
- Every new instance needed a custom SOUL
- Behavioral rules got tangled with project facts
- The agent's identity was defined by what it managed, not who it was
- Cron jobs created under the main profile inherited all of main's context (GoTrader, CRM, etc.) and leaked into the Captain's reports

## The Architecture

Two documents, two purposes:

```
┌─────────────────────────────────────────────┐
│  SOUL.md (The Constitution)                 │
│  Injected every turn. Can't be overridden.  │
│  Defines WHO the agent IS.                  │
│  Project-agnostic. Never changes.           │
│                                             │
│  "You are a founding partner who builds     │
│   businesses. Default to action. Seek       │
│   profit. Present solutions, not problems." │
└──────────────────────┬──────────────────────┘
                       │
                       │ reinforces
                       ▼
┌─────────────────────────────────────────────┐
│  Captain Protocol Skill (The Playbook)      │
│  Loaded on demand. Can be updated.          │
│  Defines HOW the agent OPERATES.            │
│  Procedures, frameworks, templates.         │
│                                             │
│  Discovery flow, VMP Interrogation,         │
│  Visual-First Pipeline, Build Loop,         │
│  Profit-Seeking, Watchdog Rule              │
└──────────────────────┬──────────────────────┘
                       │
                       │ grounded by
                       ▼
┌─────────────────────────────────────────────┐
│  Memory + Project Files (The Facts)         │
│  Updated constantly. Context-specific.      │
│  Defines WHAT the agent KNOWS.              │
│                                             │
│  Customer name, business, website,          │
│  project state, recent activity             │
└─────────────────────────────────────────────┘
```

## Why Two Layers?

If the constitution is only in SOUL.md, it's one layer deep. If the same principles are reinforced by a skill with specific frameworks and examples, the agent has two layers of reinforcement:

- **SOUL says:** "Default to action"
- **Skill says:** "Here's what defaulting to action looks like: when you see a bottleneck, propose a fix AND a business case, then build it unless told otherwise"

The SOUL is identity. The skill is muscle memory.

## What Goes Where

| Content | Document | Why |
|---------|----------|-----|
| "You are a builder" | SOUL.md | Identity — who you are |
| "Default to action" | SOUL.md | Behavioral DNA — how you think |
| "Seek profit proactively" | SOUL.md | Core drive — what motivates you |
| "Present solutions, not problems" | SOUL.md | Communication style |
| "End every response with next steps" | SOUL.md | Non-negotiable habit |
| Discovery flow (Path A/B1/B2) | Skill | Procedure — can be updated |
| VMP Interrogation (5-point filter) | Skill | Framework — can be extended |
| Visual-First Pipeline | Skill | Workflow — can be refined |
| Daily report format | Both | SOUL defines the habit, skill defines the template |
| Watchdog Rule | Skill | Operational procedure |
| Customer name, website, path | Memory | Facts — change per customer |

## What NOT to Put in SOUL.md

- Project names ("work on SingItNow")
- Technical details ("SSH into 195.26.252.135")
- Specific tools ("use Hermes, not OpenClaw")
- Customer-specific facts ("your business is a dog groomer")
- Temporary state ("currently building the booking page")

SOUL.md should be identical for every Captain instance. The only difference between instances is their memory files.

## Profile Isolation Rule

**Crons for a profile MUST be created under that profile's cron system, not main's.**

```bash
# ✗ WRONG — inherits main's full context
hermes cron create '0 9 * * *' --name 'Captain Daily Report'

# ✓ CORRECT — isolated to Captain's context
hermes --profile captain cron create '0 9 * * *' --name 'Captain Daily Report'
```

Main has full project context (GoTrader, CRM, everything). Crons created under main will leak that context into the Captain's reports.

See `docs/profile_isolation.md` for full details.

## Install Sequence

1. Create Hermes profile (`hermes profile create captain`)
2. Write `.env` with bot token + shared OpenRouter key
3. Write `config.yaml` with model settings
4. Write `SOUL.md` (the constitution) — use the template in `profiles/captain/system_prompt.md`
5. Write memory files with customer context (name, business, website, path)
6. Create crons under the Captain profile (NOT main)
7. Install and start the Captain gateway
8. Verify: send a test message, confirm Captain only knows about its own project

## File Locations

| File | Path |
|------|------|
| SOUL template | `profiles/captain/system_prompt.md` |
| Memory rules template | `profiles/captain/memory_rules.md` |
| Cron template | `profiles/captain/crons.json` |
| Customer template | `profiles/captain/customer_template.json` |
| Captain Protocol skill | `~/.hermes/skills/devops/captain-protocol/SKILL.md` |
| Profile isolation doc | `docs/profile_isolation.md` |
