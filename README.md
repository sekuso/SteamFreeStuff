# SteamFreeStuff

Finds currently free games on Steam that you don't own.

Ideal implementation is probably in your Discord bot or wherever you like getting notifications.

## Setup

1. Get a Steam API key: https://steamcommunity.com/dev/apikey
2. Install `requests` or do: `pip3 install -r requirements.txt`

## Usage

`git clone https://github.com/sekuso/SteamFreeStuff`

```py
from SteamFreeStuff.steam_freebies import all_new_free_games

all_new_free_games(api_key="ABC12345678910", steam_ids=["76561198000000001", "76561198000000002"])
```

The all_new_free_games function returns a dict mapping each Steam ID to a list of (appid, name) tuples
