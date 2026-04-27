# Hermes Agent Install

Complete provisioning system for deploying AI agents to customers.

## What This Is

When someone buys an **AI Agent Setup ($399)**, you walk them through installing their own private AI agent on their VPS. This repo contains:

- **Install scripts** — automated setup for fresh VPS and existing VPS
- **Captain Profile** — the agent personality and behavior for customer instances
- **Landing pages** — standalone Vercel pages for the product and upsells

## Package Overview

| Product | Price | Page |
|---|---|---|
| **AI Agent Setup** | $399 | [/](landing/index.html) |
| **Captain Protocol** | $199 | [/captain](landing/captain.html) |
| **Custom Skills** | $149/skill | [/skills](landing/skills.html) |
| **Growth Audit** | $199 | [/audit](landing/audit.html) |
| **3-Month Review Pack** | $149 | [/review](landing/review.html) |

## Install Flow

### Scenario A: Customer has a fresh VPS (most common)

1. Customer buys AI Agent Setup ($399)
2. You schedule a Google Meet video call
3. Customer creates a Contabo VPS ($6/mo) — you walk them through it
4. Customer SSHs in and clones this repo
5. Customer runs `bash scripts/install_fresh.sh`
6. Script installs Docker, prompts for credentials, provisions the agent
7. Agent sends first message on Telegram
8. You're on the call to help if anything goes wrong

### Scenario B: Customer already has a VPS with Hermes

1. Customer buys AI Agent Setup ($399)
2. You SSH in (or they run it) and run `bash scripts/add_customer.sh --name "..." --bot-token "..." --api-key "..." --chat-id "..." --path A`
3. New customer instance is provisioned alongside existing installation
4. Agent sends first message on Telegram

## Repo Structure

```
hermes-agent-install/
├── scripts/
│   ├── install_fresh.sh        # Full VPS setup from scratch
│   ├── add_customer.sh         # Add customer to existing VPS
│   └── install_captain.py      # Core provisioning script
├── profiles/
│   └── captain/
│       ├── system_prompt.md    # Agent personality
│       ├── memory_rules.md     # Behavioral rules
│       ├── customer_template.json  # Customer data template
│       └── crons.json          # Scheduled jobs
├── landing/                    # Vercel deployment
│   ├── index.html              # Agent Install ($399)
│   ├── captain.html            # Captain Protocol ($199)
│   ├── skills.html             # Custom Skills ($149)
│   ├── audit.html              # Growth Audit ($199)
│   ├── review.html             # 3-Month Review Pack ($149)
│   └── assets/style.css        # Shared styles
└── README.md
```

## Deploy Landing Pages

```bash
cd landing/
npx vercel --prod
```

Or connect the `landing/` directory to a Vercel project via GitHub.

## Key Design Decisions

- **Customer owns everything.** Their VPS, their keys, their data. You never see their passwords.
- **One instance per customer.** Clean isolation. No shared memory, no shared bots.
- **Captain Protocol is default.** Every customer gets the proactive, leading agent personality.
- **Telegram is the interface.** No web UI to maintain. Customers talk to their agent like texting a friend.
- **One-time pricing.** No subscriptions (for now). Customers pay once, own forever.

## Stripe Payment Links

- AI Agent Setup ($399): `https://buy.stripe.com/6oU3cv9wR0Mvfd89qz87K00`
- AI Assessment ($999): `https://buy.stripe.com/7sY9ATaAV1Qz9SO8mv87K01`
