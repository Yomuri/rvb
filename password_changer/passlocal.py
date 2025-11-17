#!/usr/bin/env python3
import sys
import subprocess
from datetime import datetime

def load_list(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <inventory_file> <wordlist>")
        sys.exit(1)

    inventory_path = sys.argv[1]
    wordlist_path = sys.argv[2]
    log_path = "password_change.log"

    inventory = load_list(inventory_path)
    wordlist = load_list(wordlist_path)

    if not inventory:
        print("[-] Inventory file is empty.")
        sys.exit(1)
    if not wordlist:
        print("[-] Wordlist is empty.")
        sys.exit(1)

    updated_inventory = []
    log_entries = []

    # timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for line in inventory:
        try:
            username, current_pw = line.split()
        except ValueError:
            log_entries.append(f"[{now}] MALFORMED LINE: {line}")
            continue

        # pick first NEW password different from current
        new_pw = None
        for pw in wordlist:
            if pw != current_pw:
                new_pw = pw
                break

        if new_pw is None:
            log_entries.append(f"[{now}] {username}: No alternative password found.")
            updated_inventory.append(line)
            continue

        print(f"[+] {username}: {current_pw} -> {new_pw}")

        # change password using sudo chpasswd
        chpasswd_input = f"{username}:{new_pw}"
        result = subprocess.run(
            ["sudo", "chpasswd"],
            input=chpasswd_input,
            text=True,
            capture_output=True
        )

        if result.returncode != 0:
            log_entries.append(
                f"[{now}] FAIL {username}: {result.stderr.strip()}"
            )
            # keep old pw in inventory
            updated_inventory.append(line)
        else:
            log_entries.append(
                f"[{now}] OK   {username}: {current_pw} -> {new_pw}"
            )
            updated_inventory.append(f"{username} {new_pw}")

    # write updated inventory
    with open(inventory_path, "w") as f:
        for entry in updated_inventory:
            f.write(entry + "\n")

    # save log
    with open(log_path, "a") as f:
        for entry in log_entries:
            f.write(entry + "\n")

    print(f"\n[+] Done. Log written to {log_path}")

if __name__ == "__main__":
    main()
