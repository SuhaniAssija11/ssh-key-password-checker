#!/bin/bash

# check ssh keys to see if they have weak passwords
# usage: ./check-ssh-key-passwords.sh keyfile

# path to the password dictionary
passwords="./dictionaries/common.txt"

# User must provide at least one arg 
if [ $# -eq 0 ]; then
  echo "usage: $0 KEY [KEY ...]" 
  exit 1
fi

# checking if ssh-keygen exists
which ssh-keygen > /dev/null
if [ $? -ne 0 ]; then
  echo "Could not find ssh-keygen in your PATH"
  exit 1
fi

# checking if the wordlist exists
if [ ! -f "$passwords" ]; then
  echo "Could not find password list at $passwords"
  exit 1
fi

exitcode=0

# go through each key they passed in
for key in "$@"; do

  # skip if its not a real private key
  if [ ! -f "$key" ]; then
    echo "SKIPPED:$key (file not found)"
    continue
  fi

  grep -q "PRIVATE KEY" "$key"
  if [ $? -ne 0 ]; then
    echo "SKIPPED: $key (File is not a private key)"
    continue
  fi

  # First trying to see if the key is not protected (no passphrase)
  ssh-keygen -y -f "$key" -P "" > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "UNPROTECTED: $key"
    exitcode=1
    continue
  fi

  # try all the passwords from the list
  found=""
  for password in $(cat "$passwords"); do
    # skipping blank lines
    if [ -z "$password" ]; then
        continue
    fi
    #checking if the password is found in the common password list
    ssh-keygen -y -f "$key" -P "$password" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      found=$password
      break
    fi
  done

# if the password is found, print the key and the password
  if [ "$found" != "" ]; then
    echo "WEAK PASSWORD: $key (passphrase: $found)"
    exitcode=1
# else: good password
  else
    echo "GOOD PASSWORD: $key"
  fi

done

exit $exitcode
