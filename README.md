# SSH Key Password Checker

This is my SECURITY-107 project.  
It checks SSH private keys for weak passphrases in a quick way.

It is meant to be a fast screen, not a full password audit.

## What the output means

| Status | Meaning |
|--------|---------|
| `UNPROTECTED` | The key has no passphrase |
| `WEAK` | The passphrase was found in the test list |
| `OK` | Passphrase was not found in the test list within timeout |

Important: `OK` does not mean "perfectly secure." It only means not found in this check.

## What password lists it uses

- `dictionaries/common.txt` (common weak passwords)
- `dictionaries/brute-1-4.txt` (all lowercase letters + digits, length 1 to 4)
- `dictionaries/combined-1-4.txt` (common + brute list together)

## Requirements

- Python 3
- OpenSSH (`ssh-keygen`)

Optional:
- John the Ripper tools for advanced workflows (`scripts/ssh2john.py` is included), but this project checks passphrases directly with `ssh-keygen`.

## Setup

```bash
make -f Makefile install wordlist
```

## Usage

Check specific keys:

```bash
./bin/check-ssh-key-passwords ~/.ssh/id_rsa ~/.ssh/id_ed25519
```

Scan a directory:

```bash
./bin/check-ssh-key-passwords --dir ~/.ssh
```

Only print problem keys:

```bash
./bin/check-ssh-key-passwords -q --dir ~/.ssh
```

Tune settings:

```bash
./bin/check-ssh-key-passwords --timeout 120 --workers 8 --max-length 3 ~/.ssh/id_ed25519
```

## Exit codes

- `0` = no weak/unprotected keys found
- `1` = at least one weak/unprotected key found
- `2` = usage/config error

## How it works (simple)

1. Check if each file is a private key.
2. Check if it is encrypted.
3. If not encrypted, report `UNPROTECTED`.
4. If encrypted, try passphrases from the list using `ssh-keygen`.
5. Report `WEAK` if found, otherwise `OK` (within timeout).

## Limitations

- It only checks the included wordlists.
- Longer/unusual passphrases may not be found.
- It is not a full security audit or key-rotation policy tool.

## Project files

```text
bin/check-ssh-key-passwords            # CLI entry point
scripts/check_ssh_key_passwords.py     # main checker logic
scripts/is_encrypted_key.py            # encrypted/unprotected detection
scripts/generate-brute-wordlist.py     # brute list generator
scripts/ssh2john.py                    # optional John helper
dictionaries/common.txt                # weak password list
Makefile
```
