<div align="center">

# gpbl-bot

</div>

**gpbl-bot** is a Python-based Discord bot that plays music from a library 24/7 in a specified voice channel.<br/>

# How to Use ✍️

This bot is currently hosted by me for the **Ghetto Poetry Battle League** Discord server, and the `songs` folder contains the songs for the server.

***Alternatively, to host it yourself...***
1. Download the Source Code. Click on **Code** and **Download ZIP**.
2. Get a **Discord Bot Token** from your [Discord developer portal](https://discord.com/developers/applications).
3. Put the token into `src/.env.sample`, and rename it to `.env`.

If you have [**Docker**](https://www.docker.com/), you can use the provided `docker-compose.yml`: `docker-compose up -d`<br/>
*For updates (after a `git pull`), you will need to `docker-compose restart` to apply the changes to an active container*

If you don't have/don't want to use Docker, you can still continue as so:
1. Download and install [Python version 3.11.0+](https://www.python.org/downloads/).
2. Download dependencies: `python3 -m pip install -r src/requirements.txt`.
3. Run locally hosted instance: `cd src && python3 main.py`.

# Bug reports & feature suggestions 🐛
Has something gone **horribly** wrong? *Or do you just think something's missing?*

Feel free to [create a new issue](https://github.com/jack-avery/gpbl-bot/issues), or message me directly on Discord about it: `@raspy`.
