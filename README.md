# Hermes Agent Install

Complete provisioning system for deploying AI agents to customers.

## What This Is

When someone buys an **AI Agent Setup ($399)**, you walk them through installing their own private AI agent on their VPS. This repo contains:

- **Install scripts** — automated setup for fresh VPS and existing VPS
- **Captain Profile** — the agent personality and behavior for customer instances
- **Teleprompter** — the live call script with interactive agent/model/cloud selectors
- **Landing pages** — standalone Vercel pages for the product and upsells

## Package Overview

| Product | Price | Page |
|---------|-------|------|
| **AI Assessment** | $999 | [/assessment](https://hermes-agent-install.vercel.app/assessment) |
| **AI Agent Setup** | $399 | [/](https://hermes-agent-install.vercel.app/) |
| **Captain Protocol** | $199 | [/captain](https://hermes-agent-install.vercel.app/captain) |
| **Custom Skills** | $149/skill | [/skills](https://hermes-agent-install.vercel.app/skills) |
| **Growth Audit** | $199 | [/audit](https://hermes-agent-install.vercel.app/audit) |
| **3-Month Review Pack** | $149 | [/review](https://hermes-agent-install.vercel.app/review) |

## Install Flow

### Scenario A: Customer has a fresh VPS (most common)

1. Customer buys AI Agent Setup ($399)
2. You schedule a Google Meet video call
3. Open `teleprompter.html` — it walks you through the live call
4. Customer creates a Contabo VPS ($6/mo) — you walk them through it
5. Customer SSHs in and runs the generated script
6. Script installs Hermes, configures Telegram, starts the gateway
7. Agent sends first message on Telegram
8. You're on the call to help if anything goes wrong

### Scenario B: You're provisioning remotely (add_customer.sh)

```bash
# SSH into the VPS, then:
bash scripts/install_fresh.sh --api-key "sk-or-v1-..." --bot-token "123:ABC..." --model "google/gemini-2.5-flash"
```

### Scenario C: Customer buys Captain Protocol (upsell)

```bash
# On a VPS that already has Hermes installed:
python3 scripts/install_captain.py --name "Sarah" --business "Paws & Claws" \
  --bot-token "123:ABC..." --api-key "sk-or-..." --chat-id "123456789" --path A
```

This creates a separate Hermes profile with the Captain personality, daily reports, and proactive behavior.

## Repo Structure

```
hermes-agent-install/
├── teleprompter.html           # Live call script (open in browser during calls)
├── scripts/
│   ├── install_fresh.sh        # Full VPS setup from scratch
│   ├── add_customer.sh         # Add customer to existing VPS
│   └── install_captain.py      # Captain Protocol provisioning
├── profiles/
│   └── captain/
│       ├── system_prompt.md    # Captain personality
│       ├── memory_rules.md     # Behavioral rules
│       ├── customer_template.json
│       └── crons.json          # Scheduled jobs (daily report, weekly check-in)
├── landing/                    # Vercel deployment (customer-facing pages)
│   ├── index.html              # Agent Install ($399)
│   ├── assessment.html         # AI Assessment ($999)
│   ├── captain.html            # Captain Protocol ($199)
│   ├── skills.html             # Custom Skills ($149)
│   ├── audit.html              # Growth Audit ($199)
│   ├── review.html             # 3-Month Review Pack ($149)
│   ├── vercel.json             # URL rewrites
│   └── assets/style.css        # Shared styles
├── docs/                       # Internal playbooks & teaching materials
│   ├── assessment_playbook.md  # How to deliver the $999 Assessment
│   ├── agent_setup_teachings.md # Core curriculum for $399 Install
│   ├── agent_setup_advanced.md  # Advanced topics (councils, routing, etc.)
│   ├── marketing_copy.md        # Ad scripts & direct mail copy
│   ├── profile_isolation.md     # CRITICAL: Multi-profile architecture rules
│   ├── captain_architecture.md  # Constitution + Protocol design doc
│   └── skipper_onboarding.md    # Skipper instance onboarding doc
└── README.md
```

## Deploy Landing Pages

```bash
cd landing/
npx vercel --prod --token=<VERCEL_TOKEN>
```

Or connect the repo to a Vercel project via GitHub (root directory: `landing/`).

## Key Design Decisions

- **Customer owns everything.** Their VPS, their keys, their data. You never see their passwords.
- **Secrets stay in .env.** API keys and bot tokens go in `~/.hermes/.env`, never in `config.yaml`.
- **One profile per customer.** Clean isolation via Hermes profiles. No shared memory, no shared bots.
- **Crons go in the profile, not main.** Critical: always use `hermes --profile <name> cron create` — never create customer crons under the main profile. Main's context will leak into the cron. See `docs/profile_isolation.md`.
- **Captain Protocol is default.** Every customer gets the proactive, leading agent personality.
- **Telegram is the interface.** No web UI to maintain. Customers talk to their agent like texting a friend.
- **One-time pricing.** No subscriptions (for now). Customers pay once, own forever.

## Stripe Payment Links

- AI Agent Setup ($399): https://buy.stripe.com/6oU3cv9wR0Mvfd89qz87K00
- AI Assessment ($999): https://buy.stripe.com/7sY9ATaAV1Qz9SO8mv87K01
