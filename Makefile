SHELL = /bin/bash
INSTALL_DIR = ${HOME}/.config/systemd/user

all: install

install:
	mkdir -p $(INSTALL_DIR)
	install -m 0644 gpbl-bot.service $(INSTALL_DIR)
	sed -i 's?#PWD?'`pwd`'?' $(INSTALL_DIR)/gpbl-bot.service
	python3 -m pip install -r src/requirements.txt
	systemctl --user enable --now gpbl-bot

uninstall:
	rm $(INSTALL_DIR)/gpbl-bot.service
	systemctl --user disable --now gpbl-bot
