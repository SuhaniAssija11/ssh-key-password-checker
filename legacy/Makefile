.PHONY: wordlist install test help

BIN := bin/check-ssh-key-passwords

help:
	@echo "Targets:"
	@echo "  wordlist  Build brute-force and combined dictionaries"
	@echo "  install   Mark scripts executable"
	@echo "  test      Run a smoke test"

wordlist:
	python3 scripts/generate-brute-wordlist.py --max-length 4 -o dictionaries/brute-1-4.txt
	cat dictionaries/common.txt dictionaries/brute-1-4.txt > dictionaries/combined-1-4.txt

install:
	chmod +x $(BIN) scripts/*.py

test: install
	@rm -f /tmp/sshchk-test-key /tmp/sshchk-test-key.pub
	@ssh-keygen -t ed25519 -f /tmp/sshchk-test-key -N "1234" -q
	@$(BIN) --timeout 30 /tmp/sshchk-test-key || true
	@rm -f /tmp/sshchk-test-key /tmp/sshchk-test-key.pub
