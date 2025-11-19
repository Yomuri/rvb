#!/usr/bin/env python3

import sys
import subprocess
import random
from datetime import datetime

LOG_FILE = "password_change.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as lf:
        lf.write(f"[{timestamp}] {msg}\n")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inventory_file> <wordlist>")
        sys.exit(1)

    inventory_file = sys.argv[1]
    wordlist_file = sys.argv[2]

    # Load passwords
    with open(wordlist_file, "r") as f:
        wordlist = [line.strip() for line in f if line.strip()]

    if not wordlist:
        print("[-] Wordlist is empty.")
        sys.exit(1)

    # Load inventory
    with open(inventory_file, "r") as f:
        inventory = [line.strip() for line in f if line.strip()]

    updated_inventory = []

    for entry in inventory:
        try:
            username, old_pw = entry.split()
        except ValueError:
            print(f"[!] Skipping malformed line: {entry}")
            log(f"SKIP malformed line: {entry}")
            continue

        # Pick a **new** password that is NOT the same as the current one
        possible_pw = [p for p in wordlist if p != old_pw]
        if not possible_pw:
            print(f"[!] No valid password for {username} (all match old?)")
            log(f"FAIL no new password available for {username}")
            updated_inventory.append(entry)
            continue

        new_pw = random.choice(possible_pw)

        print(f"[+] Changing password for {username}")

        chpasswd_input = f"{username}:{new_pw}"
        result = subprocess.run(
            ["sudo", "chpasswd"],
            input=chpasswd_input,
            text=True,
            capture_output=True
        )

        if result.returncode != 0:
            print(f"[!] Failed to update {username}")
            log(f"FAIL {username} -> {result.stderr.strip()}")
            updated_inventory.append(entry)  # keep old password
        else:
            print(f"[+] Updated {username}: {old_pw} -> {new_pw}")
            log(f"OK {username}: {old_pw} -> {new_pw}")
            updated_inventory.append(f"{username} {new_pw}")

    # Write updated inventory
    with open(inventory_file, "w") as f:
        for line in updated_inventory:
            f.write(line + "\n")

    print("\n[+] Done. Changes logged to", LOG_FILE)

if __name__ == "__main__":
    main()
