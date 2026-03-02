# KINGBOT SPAM BOT 

A powerful Telegram Userbot for spam/raid purposes. Controls multiple accounts simultaneously.

## Deployment

### Deploy on Railway

1. Fork this repository.
2. Login to [Railway](https://railway.app/).
3. Create a new project and select "Deploy from GitHub repo".
4. Select your forked repository.
5. Go to **Variables** tab and add the required environment variables.

### Environment Variables

| Variable | Description |
|Data|Description|
|---|---|
| `API_ID` | Your Telegram API ID (get from my.telegram.org) |
| `API_HASH` | Your Telegram API Hash |
| `SUDO` | User IDs of admins (space separated) |
| `STRING` | Telethon Session String for Account 1 |
| `STRING2` | Telethon Session String for Account 2 |
| `STRING3` | Telethon Session String for Account 3 (and so on...) |

### String Session Generator

You can generate session strings using this Repl:
[![GenerateString](https://img.shields.io/badge/repl.it-generateString-yellowgreen)](https://replit.com/@Kartikpro/KINGBOT-STRING#main.py)

## Features

- Multi-account support (add as many STRING vars as needed)
- `.spam <count> <msg>`
- `.delayspam <sleep> <count> <msg>`
- `.raid <count> <user>`
- `.join / .leave`
- `.bio <text>`

## Disclaimer

This bot is for educational purposes only. Use responsibly.
