INSTALL_UNIT_DIR = "$${HOME}"/.config/systemd/user

all: install

install:
	mkdir -p $(INSTALL_UNIT_DIR)
	install -m 0644 gpbl-bot.service $(INSTALL_UNIT_DIR)
	sed -i 's?#PWD?'`pwd`'?' $(INSTALL_UNIT_DIR)/gpbl-bot.service
	python3 -m pip install -r src/requirements.txt
	systemctl --user enable --now gpbl-bot

uninstall:
	systemctl --user disable --now gpbl-bot
	rm $(INSTALL_UNIT_DIR)/gpbl-bot.service
