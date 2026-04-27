#!/usr/bin/env python3
"""
install_captain.py — Provision a new Captain Protocol customer instance.

Usage:
  python3 install_captain.py --name "Sarah" --website "https://example.com" --bot-token "123:ABC..." --api-key "sk-..." --chat-id "123456789"

Or interactive (no args):
  python3 install_captain.py

What it does:
  1. Creates customer directory structure
  2. Generates Captain profile (system prompt, memory, config)
  3. Sets up cron job definitions
  4. Generates docker-compose service entry
  5. Optionally starts the container
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_DIR = SCRIPT_DIR.parent
PROFILE_TEMPLATE_DIR = REPO_DIR / "profiles" / "captain"
CUSTOMERS_DIR = Path.home() / "hermes-customers"

# ─── Helpers ────────────────────────────────────────────────────────────────

def prompt(message, default=None):
    """Ask the user for input with an optional default."""
    if default:
        response = input(f"{message} [{default}]: ").strip()
        return response if response else default
    while True:
        response = input(f"{message}: ").strip()
        if response:
            return response

def read_template(path):
    """Read a template file."""
    with open(path, "r") as f:
        return f.read()

def fill_template(content, replacements):
    """Replace {PLACEHOLDER} tokens with values."""
    for key, value in replacements.items():
        content = content.replace(f"{{{key}}}", str(value))
    return content

def write_file(path, content):
    """Write content to a file, creating directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  ✓ {path}")

# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Provision a Captain Protocol customer instance")
    parser.add_argument("--name", help="Customer name (e.g., Sarah)")
    parser.add_argument("--business", help="Business name (e.g., Paws & Claws Grooming)")
    parser.add_argument("--website", help="Business website URL")
    parser.add_argument("--bot-token", help="Telegram bot token from BotFather")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--chat-id", help="Telegram chat ID for the customer")
    parser.add_argument("--path", choices=["A", "B1", "B2"], help="Customer path: A=existing business, B1=new with idea, B2=new no idea")
    parser.add_argument("--start", action="store_true", help="Start the container after provisioning")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  HERMES AGENT INSTALL — Captain Protocol Provisioner")
    print("=" * 60 + "\n")

    # Gather info (interactive if not provided via args)
    name = args.name or prompt("Customer name (first name)")
    business = args.business or prompt("Business name (or 'TBD' if unknown)")
    website = args.website or prompt("Website URL (or 'none')")
    bot_token = args.bot_token or prompt("Telegram bot token (from BotFather)")
    api_key = args.api_key or prompt("OpenRouter API key (sk-or-...)")
    chat_id = args.chat_id or prompt("Telegram chat ID (customer's)")

    if args.path:
        path = args.path
    else:
        print("\nCustomer path:")
        print("  A  = Existing business (has a website)")
        print("  B1 = New business, has an idea")
        print("  B2 = New business, needs help figuring out what to build")
        path = prompt("Path (A / B1 / B2)", "A").upper()

    install_date = datetime.now().strftime("%Y-%m-%d")
    slug = name.lower().replace(" ", "-")
    customer_dir = CUSTOMERS_DIR / slug

    # Check if customer already exists
    if customer_dir.exists():
        print(f"\n⚠  Customer directory already exists: {customer_dir}")
        overwrite = prompt("Overwrite? (y/n)", "n").lower()
        if overwrite != "y":
            print("Aborted.")
            sys.exit(1)

    print(f"\n📦 Provisioning Captain instance for {name}...")
    print(f"   Directory: {customer_dir}\n")

    # ── 1. Create directory structure ────────────────────────────────────
    for subdir in ["data", "memory", "skills", "logs", "cron"]:
        (customer_dir / subdir).mkdir(parents=True, exist_ok=True)

    # ── 2. Replacements dict ─────────────────────────────────────────────
    replacements = {
        "CUSTOMER_NAME": name,
        "BUSINESS_NAME": business,
        "WEBSITE": website,
        "BOT_TOKEN": bot_token,
        "API_KEY": api_key,
        "CHAT_ID": chat_id,
        "INSTALL_DATE": install_date,
        "PATH": path,
        "STATUS": "discovery",
    }

    # ── 3. Generate system prompt ────────────────────────────────────────
    print("Generating Captain profile...")
    system_prompt = fill_template(
        read_template(PROFILE_TEMPLATE_DIR / "system_prompt.md"),
        replacements
    )
    write_file(customer_dir / "system_prompt.md", system_prompt)

    # ── 4. Generate memory rules ─────────────────────────────────────────
    memory_rules = fill_template(
        read_template(PROFILE_TEMPLATE_DIR / "memory_rules.md"),
        replacements
    )
    write_file(customer_dir / "memory_rules.md", memory_rules)

    # ── 5. Generate customer.json ────────────────────────────────────────
    customer_json = fill_template(
        read_template(PROFILE_TEMPLATE_DIR / "customer_template.json"),
        replacements
    )
    # Parse and re-dump to validate JSON
    customer_data = json.loads(customer_json)
    write_file(customer_dir / "customer.json", json.dumps(customer_data, indent=2))

    # ── 6. Generate cron jobs ────────────────────────────────────────────
    crons = json.loads(read_template(PROFILE_TEMPLATE_DIR / "crons.json"))
    write_file(customer_dir / "crons.json", json.dumps(crons, indent=2))

    # ── 7. Generate config.yaml ──────────────────────────────────────────
    config = f"""# Hermes Agent — Captain Protocol Instance
# Customer: {name}
# Generated: {install_date}

mode: captain

model:
  provider: openrouter
  model: google/gemini-2.5-flash
  api_key: "{api_key}"

telegram:
  token: "{bot_token}"

customer:
  name: "{name}"
  business: "{business}"
  website: "{website}"
  chat_id: "{chat_id}"
  path: "{path}"
  status: "discovery"

profile:
  system_prompt: "./system_prompt.md"
  memory_rules: "./memory_rules.md"

cron:
  config: "./crons.json"

logging:
  level: info
  dir: "./logs"
"""
    write_file(customer_dir / "config.yaml", config)

    # ── 8. Generate docker-compose service entry ─────────────────────────
    service_name = f"hermes-{slug}"
    docker_service = f"""
  {service_name}:
    image: hermes-agent:latest
    container_name: {service_name}
    restart: always
    volumes:
      - {customer_dir}:/app/config
    environment:
      - HERMES_CONFIG=/app/config/config.yaml
      - HERMES_PROFILE=captain
    ports: []
"""
    docker_compose_path = customer_dir / "docker-compose.yml"
    full_compose = f"""version: "3.8"

services:
{docker_service}
"""
    write_file(docker_compose_path, full_compose)

    # ── 9. Generate first-message script ─────────────────────────────────
    first_message = f"""#!/usr/bin/env python3
\"\"\"
Send the Captain Protocol first message to the customer.
Run this after the container is started.
\"\"\"
import requests
import sys

BOT_TOKEN = "{bot_token}"
CHAT_ID = "{chat_id}"

if path == "A":
    greeting = f"""Hey {{name}}! I'm your AI agent — I live on your server and work for you 24/7.

I already did some homework on your business. Before I share what I found, one question:

**Do you have an existing business, or are you starting something new?**"""
elif path == "B1":
    greeting = f"""Hey {{name}}! I'm your AI agent — I live on your server and work for you 24/7.

I heard you have a business idea you want to build. I'd love to hear about it.

**Tell me about your idea — what are you thinking?**"""
else:
    greeting = f"""Hey {{name}}! I'm your AI agent — I live on your server and work for you 24/7.

Let's figure out what we should build together. Two options:

**Got an idea already?** Tell me about it.
**Not sure yet?** Just say "let's figure it out" and I'll ask you a few questions to find the right business for you."""

url = f"https://api.telegram.org/bot{{BOT_TOKEN}}/sendMessage"
payload = {{"chat_id": CHAT_ID, "text": greeting, "parse_mode": "Markdown"}}

resp = requests.post(url, json=payload)
if resp.status_code == 200:
    print(f"✓ First message sent to {{name}}")
else:
    print(f"✗ Failed to send: {{resp.text}}")
    sys.exit(1)
"""
    # Fix the first message to use actual values
    if path == "A":
        msg_text = f"Hey {name}! I'm your AI agent — I live on your server and work for you 24/7.\n\nI already did some homework on your business. Before I share what I found, one question:\n\n**Do you have an existing business, or are you starting something new?**"
    elif path == "B1":
        msg_text = f"Hey {name}! I'm your AI agent — I live on your server and work for you 24/7.\n\nI heard you have a business idea you want to build. I'd love to hear about it.\n\n**Tell me about your idea — what are you thinking?**"
    else:
        msg_text = f"Hey {name}! I'm your AI agent — I live on your server and work for you 24/7.\n\nLet's figure out what we should build together. Two options:\n\n**Got an idea already?** Tell me about it.\n**Not sure yet?** Just say \"let's figure it out\" and I'll ask you a few questions to find the right business for you."

    simple_first_msg = f"""#!/usr/bin/env python3
\"\"\"Send the Captain Protocol first message to {name}.\"\"\"
import requests, sys

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {{"chat_id": "{chat_id}", "text": """{msg_text}""", "parse_mode": "Markdown"}}
resp = requests.post(url, json=payload)
if resp.status_code == 200:
    print("✓ First message sent to {name}")
else:
    print(f"✗ Failed: {{resp.text}}")
    sys.exit(1)
"""
    write_file(customer_dir / "send_first_message.py", simple_first_msg)

    # ── Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  ✓ Captain instance provisioned for {name}")
    print("=" * 60)
    print(f"""
  Directory:  {customer_dir}
  Config:     {customer_dir}/config.yaml
  Profile:    {customer_dir}/system_prompt.md
  Customer:   {customer_dir}/customer.json
  Cron jobs:  {customer_dir}/crons.json
  Docker:     {customer_dir}/docker-compose.yml
  First msg:  {customer_dir}/send_first_message.py

  Next steps:
  1. Start the container:
     cd {customer_dir} && docker compose up -d

  2. Send the first message:
     python3 {customer_dir}/send_first_message.py

  3. The agent will greet {name} and start discovery.
""")

    # Optionally start
    if args.start or prompt("Start the container now? (y/n)", "y").lower() == "y":
        os.system(f"cd {customer_dir} && docker compose up -d")
        print(f"\n✓ Container started. Sending first message...")
        os.system(f"python3 {customer_dir}/send_first_message.py")

if __name__ == "__main__":
    main()
