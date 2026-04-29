# AI Agent Setup: Core Curriculum

When delivering the "$399 AI Agent Setup" call to pragmatic founders and makers, we aren't just giving them API keys and a terminal window. We are teaching them how to build an **autonomous operating system** for their business.

This document outlines the core operational philosophies that must be taught during the implementation call to ensure the client gets compounding value and ascends your "Infinite Strategy Ladder."

## 1. The Core Framework: "Visionary & Floor Worker"
- **The Concept**: You (the human) are the Visionary. The Agent is the Floor Worker.
- **The Pitfall**: Most people treat AI agents like search engines—they ask it a question, get an answer, and leave. This is a massive waste of potential.
- **The Teaching**: An agent is a junior employee with the keys to your VPS that works 24/7. It needs standard operating procedures (Skills), tools (APIs), and a mandate to actually execute work independently.

## 2. The "Hope is Not a Strategy" Rule (Watchdogs)
- **The Concept**: Never deploy code, a scraper, or an automation without simultaneously deploying the system that watches it. 
- **The Pitfall**: People build a cool automated scraper. It breaks silently on day 2. They find out on day 14. They blame the AI and give up.
- **The Teaching ("The Watchdog Rule")**: For every automation built, the Agent must be instructed to build a background cron job to monitor it. 
  - *Example*: "If I build a crypto trading bot, I must also teach the agent to schedule a 2-hour heartbeat script that checks `docker ps`, searches the logs for the word 'error', and sends me a WhatsApp message if the bot crashes. If the board is green, it stays silent."

## 3. State Injection vs Context Bloat
- **The Concept**: Do not stuff every detail of every project into the Agent's permanent memory.
- **The Pitfall**: Humans tell the AI, "Remember all 50 of these passwords, URLs, and schemas." The AI's context window fills up, api costs skyrocket, and it starts hallucinating because it has too much noise.
- **The Teaching**: Teach the client to build "Project State Files" (e.g., `~/projects/crm.md`, `~/projects/trading_bot.md`). When the human says "Work on the CRM," the Agent's first move is to read that specific file, load the strict context locally, spawn a separate worker thread (Subagent) that only knows about the CRM, and execute. This keeps the main agent fast, cheap, and hyper-focused.

## 4. Automated Ecosystem Awareness
- **The Concept**: The AI shouldn't just do client work; it should maintain its own software stack and monitor the AI industry landscape.
- **The Pitfall**: Software rusts. APIs deprecate. Users fall off the frontier because they don't know a model endpoint was sunset or a new, 10x cheaper model was released.
- **The Teaching**: Teach the AI to run a bi-weekly "Updates Watchdog" script. It queries upstream APIs (OpenRouter, GitHub), filters for new releases from Tier-1 providers (Anthropic, Google, OpenAI), and proactively alerts the user: *"Anthropic just dropped Claude 4.5. Our backend subagent is currently using Mistral, and Claude is cheaper. Do you want me to update the config file to switch models?"*

By the end of the 60-minute implementation call, the client shouldn't just walk away with a working terminal. They should walk away with a **Watchdog**, a **Project State File**, and the mental framework to scale their operations horizontally.
### The "Probably Not An Issue" Trap
- **The Concept**: When an AI says an error is "likely fine" or "probably not an issue," it is guessing. It does not have proof.
- **The Pitfall**: The AI detects a 0-byte database file (`tournament.db`) or a brief log warning. Because the main system hasn't crashed *yet*, the AI dismisses it to keep the conversation moving. Two days later, that exact file causes a system-wide lockup under load.
- **The Teaching**: "Hope is not a strategy." Do not let the AI hand-wave warnings. If the AI says an error is "likely fine," teach the client to immediately reply: *"Prove it."* Force the agent to write a targeted watchdog script (e.g., a cron job that checks the `tournament.db` logs every 6 hours) so that if the "likely" assumption is wrong, the trap is sprung automatically.
