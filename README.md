# SSH Key Password Checker

A simple bash script that checks whether SSH private keys are unprotected or use a weak passphrase from a common password list.

Meant to be a fast screen, not a full password audit.

## What the output means


| Status          | Meaning                                               |
| --------------- | ----------------------------------------------------- |
| `SKIPPED`       | File not found, or not a private key                  |
| `UNPROTECTED`   | The key has no passphrase                             |
| `WEAK PASSWORD` | The passphrase was found in `dictionaries/common.txt` |
| `GOOD PASSWORD` | Passphrase was not found in the common password list  |


Important: `GOOD PASSWORD` does not mean "perfectly secure." It only means the passphrase was not in this wordlist.

## What password list it uses

- `dictionaries/common.txt` (common weak passwords)

The first 1000 passwords come from the top of
`[10k-most-common.txt](https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10k-most-common.txt)`
in [SecLists](https://github.com/danielmiessler/SecLists) (Daniel Miessler).
A few extra specific terms (for example `ssh`, `id_rsa`, `umiacs`, `maryland`) were added at the end.

## Requirements

- bash
- OpenSSH (`ssh-keygen`)

## Usage

Check one or more keys:

```bash
./check-ssh-key-passwords.sh ~/.ssh/id_rsa ~/.ssh/id_ed25519
```

Example output:

```text
UNPROTECTED: /home/you/.ssh/id_rsa
WEAK PASSWORD: /home/you/.ssh/id_ed25519 (passphrase: password)
GOOD PASSWORD: /home/you/.ssh/id_ecdsa
```

Note: if password is weak then the program will print out the weak password being used. 

## Exit codes

- `0` = no weak/unprotected keys found
- `1` = at least one weak/unprotected key found, or a usage/setup error

## How it works

1. Check that each argument is an existing file.
2. Check that the file looks like a private key (`PRIVATE KEY` in the file).
3. Try opening it with an empty passphrase.
4. If that works, report `UNPROTECTED`.
5. Otherwise try each password in `dictionaries/common.txt` with `ssh-keygen`.
6. Report `WEAK PASSWORD` if one works, otherwise `GOOD PASSWORD`.

## Testing

See [TESTING.md](TESTING.md) for a step-by-step guide to create sample keys and verify the script.

## Project files

```text
check-ssh-key-passwords.sh   # main bash checker
dictionaries/common.txt      # weak password list
TESTING.md                   # how to test the script
```

