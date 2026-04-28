#!/usr/bin/env python3
"""
install_captain.py — Provision a new Captain Protocol customer instance.

Creates a Hermes profile for the customer, configures the Captain Protocol
personality, sets up cron jobs, and starts the Telegram gateway.

Usage:
  python3 install_captain.py --name "Sarah" --business "Paws & Claws" \
    --bot-token "123:ABC..." --api-key "sk-or-..." --chat-id "123456789"

Or interactive (no args):
  python3 install_captain.py

What it does:
  1. Creates a Hermes profile for the customer
  2. Writes Captain Protocol system prompt as agent memory
  3. Configures .env with credentials (secrets stay out of config.yaml)
  4. Sets up cron jobs (daily report, weekly check-in, dead man's switch)
  5. Starts the Telegram gateway for this profile
  6. Sends the first Captain message to the customer on Telegram
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_DIR = SCRIPT_DIR.parent
PROFILE_TEMPLATE_DIR = REPO_DIR / "profiles" / "captain"


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
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  ✓ {path}")


def run(cmd, check=True):
    """Run a shell command and print status."""
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        for line in result.stdout.strip().split("\n"):
            print(f"    {line}")
    if check and result.returncode != 0:
        print(f"  ✗ Command failed (exit {result.returncode})")
        if result.stderr.strip():
            for line in result.stderr.strip().split("\n"):
                print(f"    {line}")
        return False
    return True


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Provision a Captain Protocol customer instance")
    parser.add_argument("--name", help="Customer first name")
    parser.add_argument("--business", help="Business name")
    parser.add_argument("--website", help="Business website URL")
    parser.add_argument("--bot-token", help="Telegram bot token from BotFather")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--chat-id", help="Telegram chat ID for the customer")
    parser.add_argument("--path", choices=["A", "B1", "B2"],
                        help="Customer path: A=existing business, B1=new with idea, B2=new no idea")
    parser.add_argument("--model", default="google/gemini-2.5-flash",
                        help="LLM model (default: google/gemini-2.5-flash)")
    parser.add_argument("--start", action="store_true", help="Start gateway after provisioning")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  HERMES AGENT INSTALL — Captain Protocol Provisioner")
    print("=" * 60 + "\n")

    # ── Check prerequisites ─────────────────────────────────────────────
    result = subprocess.run("command -v hermes", shell=True, capture_output=True)
    if result.returncode != 0:
        print("✗ hermes command not found. Run install_fresh.sh first, or:")
        print("  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash")
        sys.exit(1)

    # ── Gather info ─────────────────────────────────────────────────────
    name = args.name or prompt("Customer first name")
    business = args.business or prompt("Business name (or 'TBD')")
    website = args.website or prompt("Website URL (or 'none')")
    bot_token = args.bot_token or prompt("Telegram bot token (from @BotFather)")
    api_key = args.api_key or prompt("OpenRouter API key (sk-or-v1-...)")
    chat_id = args.chat_id or prompt("Telegram chat ID (customer's numeric ID)")

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
    profile_name = f"captain-{slug}"

    # ── 1. Create Hermes profile ────────────────────────────────────────
    print(f"\n📦 Provisioning Captain instance for {name}...\n")

    print("Creating Hermes profile...")
    run(f"hermes profile create {profile_name}", check=False)

    # Profile directory
    profile_dir = Path.home() / ".hermes" / "profiles" / profile_name
    if not profile_dir.exists():
        # Fallback: create manually
        profile_dir.mkdir(parents=True, exist_ok=True)
        for subdir in ["sessions", "logs", "skills", "memory"]:
            (profile_dir / subdir).mkdir(exist_ok=True)

    print(f"  ✓ Profile: {profile_dir}\n")

    # ── 2. Write .env (secrets never go in config.yaml) ─────────────────
    print("Configuring credentials...")
    env_content = f"""OPENROUTER_API_KEY={api_key}
TELEGRAM_BOT_TOKEN={bot_token}
TELEGRAM_ALLOWED_USERS={chat_id}
TELEGRAM_HOME_CHANNEL={chat_id}
"""
    write_file(profile_dir / ".env", env_content)

    # ── 3. Write config.yaml (proper hermes-agent format) ───────────────
    print("Writing agent configuration...")
    config_content = f"""# Hermes Agent — Captain Protocol Instance
# Customer: {name} ({business})
# Generated: {install_date}

model:
  default: {args.model}
  provider: openrouter

memory:
  memory_enabled: true
  user_profile_enabled: true
"""
    write_file(profile_dir / "config.yaml", config_content)

    # ── 4. Write Captain system prompt as memory ────────────────────────
    print("Loading Captain Protocol profile...")
    replacements = {
        "CUSTOMER_NAME": name,
        "BUSINESS_NAME": business,
        "WEBSITE": website,
        "BOT_TOKEN": bot_token,  # kept for template compat, not stored in config
        "API_KEY": api_key,      # kept for template compat, not stored in config
        "CHAT_ID": chat_id,
        "INSTALL_DATE": install_date,
        "PATH": path,
        "STATUS": "discovery",
    }

    # System prompt → user_memory (injected into every session)
    system_prompt = fill_template(
        read_template(PROFILE_TEMPLATE_DIR / "system_prompt.md"),
        replacements
    )
    write_file(profile_dir / "memory" / "user_profile.md", system_prompt)

    # Memory rules → memory file
    memory_rules = fill_template(
        read_template(PROFILE_TEMPLATE_DIR / "memory_rules.md"),
        replacements
    )
    write_file(profile_dir / "memory" / "hermes_memory.md", memory_rules)

    # Customer data
    customer_data = {
        "name": name,
        "business_name": business,
        "website": website,
        "install_date": install_date,
        "path": path,
        "status": "discovery",
        "messaging": {
            "platform": "telegram",
            "chat_id": chat_id,
        },
        "upsells": {
            "captain_protocol": True,
            "custom_skills": [],
            "growth_audit": False,
            "review_pack": False,
        },
        "project": {
            "name": None,
            "type": None,
            "started": None,
            "shipped": None,
            "current_task": None,
        },
    }
    write_file(
        profile_dir / "memory" / "customer.json",
        json.dumps(customer_data, indent=2)
    )

    # ── 5. Register cron jobs ──────────────────────────────────────────
    print("\nRegistering cron jobs...")
    crons = json.loads(read_template(PROFILE_TEMPLATE_DIR / "crons.json"))
    for job in crons.get("jobs", []):
        name = job["name"]
        schedule = job["schedule"]
        prompt_text = job["prompt"]
        deliver = job.get("deliver", "origin")
        print(f"  • {name} ({schedule})")
        # Write prompt to temp file to avoid shell escaping issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt_text)
            prompt_file = f.name
        run(
            f"hermes --profile {profile_name} cron create "
            f"'{schedule}' "
            f"\"$(cat {prompt_file})\" "
            f"--name '{name}' "
            f"--deliver '{deliver}'",
            check=False
        )
        os.unlink(prompt_file)
    print()

    # ── 6. Generate first-message script ────────────────────────────────
    if path == "A":
        msg_text = (
            f"Hey {name}! I'm your AI agent — I live on your server and work for you 24/7.\n\n"
            f"I already did some homework on {business}. Before I share what I found, one question:\n\n"
            f"**Do you have an existing website, or are you starting from scratch?**"
        )
    elif path == "B1":
        msg_text = (
            f"Hey {name}! I'm your AI agent — I live on your server and work for you 24/7.\n\n"
            f"I heard you have a business idea you want to build. I'd love to hear about it.\n\n"
            f"**Tell me about your idea — what are you thinking?**"
        )
    else:
        msg_text = (
            f"Hey {name}! I'm your AI agent — I live on your server and work for you 24/7.\n\n"
            f"Let's figure out what we should build together. Two options:\n\n"
            f"**Got an idea already?** Tell me about it.\n"
            f"**Not sure yet?** Just say \"let's figure it out\" and I'll ask you a few questions."
        )

    first_msg_script = f'''#!/usr/bin/env python3
"""Send the Captain Protocol first message to {name}."""
import requests, sys

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {{"chat_id": "{chat_id}", "text": """{msg_text}""", "parse_mode": "Markdown"}}
resp = requests.post(url, json=payload)
if resp.status_code == 200:
    print("✓ First message sent to {name}")
else:
    print(f"✗ Failed: {{resp.text}}")
    sys.exit(1)
'''
    write_file(profile_dir / "send_first_message.py", first_msg_script)

    # ── 7. Summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  ✓ Captain instance provisioned for {name}")
    print("=" * 60)
    print(f"""
  Profile:    {profile_dir}
  Config:     {profile_dir}/config.yaml
  Memory:     {profile_dir}/memory/user_profile.md
  Customer:   {profile_dir}/memory/customer.json
  Crons:      {profile_dir}/crons.json
  First msg:  {profile_dir}/send_first_message.py

  To start:
    hermes gateway install --profile {profile_name}
    hermes gateway start --profile {profile_name}

  To send the first message:
    python3 {profile_dir}/send_first_message.py

  To chat with this agent directly:
    hermes --profile {profile_name}
""")

    # ── 8. Optionally start ─────────────────────────────────────────────
    if args.start:
        print("Starting gateway...")
        run(f"hermes --profile {profile_name} gateway install", check=False)
        run(f"hermes --profile {profile_name} gateway start", check=False)
        print("\nSending first message...")
        run(f"python3 {profile_dir}/send_first_message.py", check=False)
    else:
        start_now = prompt("Start the gateway now? (y/n)", "y").lower()
        if start_now == "y":
            run(f"hermes --profile {profile_name} gateway install", check=False)
            run(f"hermes --profile {profile_name} gateway start", check=False)
            send = prompt("Send first message to customer? (y/n)", "y").lower()
            if send == "y":
                run(f"python3 {profile_dir}/send_first_message.py", check=False)


if __name__ == "__main__":
    main()
