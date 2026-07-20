# Testing the SSH Key Password Checker

making sample keys with **known** passphrases, then checking that the script reports the right status for each one.



## Quick test (recommended)

### 1. Create a temp folder and sample keys

```bash
mkdir -p /tmp/password-test

# no passphrase -> should be UNPROTECTED
ssh-keygen -t ed25519 -f /tmp/password-test/unprotected -N "" -q

# weak passphrase from common.txt -> should be WEAK PASSWORD
ssh-keygen -t ed25519 -f /tmp/password-test/weak -N "password" -q

# strong passphrase not in common.txt -> should be GOOD PASSWORD
ssh-keygen -t ed25519 -f /tmp/password-test/strong -N "$+rong_p@assWORD" -q
```

What each `ssh-keygen` flags mean:


| Flag         | Meaning                                  |
| ------------ | ---------------------------------------- |
| `-t ed25519` | Create an Ed25519 key                    |
| `-f ...`     | Where to save the private key            |
| `-N "..."`   | Passphrase for the key (`""` means none) |
| `-q`         | Quiet mode                               |




### 2. Run the script

**Full check** (can take a couple min for the strong password to work):

```bash
./check-ssh-key-passwords.sh \
  /tmp/sshchk-test/unprotected \
  /tmp/sshchk-test/weak \
  /tmp/sshchk-test/strong \
  /tmp/sshchk-test/missing
```



### 3. Expected output

```text
UNPROTECTED: /tmp/sshchk-test/unprotected
WEAK PASSWORD: /tmp/sshchk-test/weak (passphrase: password)
GOOD PASSWORD: /tmp/sshchk-test/strong
SKIPPED:/tmp/sshchk-test/missing (file not found)
```

(`GOOD PASSWORD` only appears if you included the strong key.)

### 4. Check the exit code

```bash
echo $?
```

- `1` if any key was unprotected or weak (expected for this test)
- `0` only if every checked key was fine



## If something looks wrong


| Problem                        | What to check                                                   |
| ------------------------------ | --------------------------------------------------------------- |
| `Could not find ssh-keygen`    | Install OpenSSH / make sure `ssh-keygen` is in your PATH        |
| `Could not find password list` | Run from the project root so `./dictionaries/common.txt` exists |
| `WEAK` key not detected        | Confirm the passphrase is actually in `dictionaries/common.txt` |
| Strong key takes a long time   | Normal — the script tries many passwords one by one             |






