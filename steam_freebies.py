import time
import requests
import json
import logging

STEAM = "https://api.steampowered.com"
ISTOREQUERYSERVICE = "/IStoreQueryService"

store_query_url = f"{STEAM}{ISTOREQUERYSERVICE}/Query/v1/"

def _get_owned_appids(steamid: str, api_key: str) -> set:
    """Fetches the list of owned appids for a given Steam ID using the Steam Web API."""
    logging.debug(f"Fetching owned appids for Steam ID: {steamid}")
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": api_key,
        "steamid": steamid,
        "include_appinfo": False
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        logging.debug(f"Owned games data: {data}")
        return set(game['appid'] for game in data.get('response', {}).get('games', []))
    else:
        print(f"Error fetching owned games: {response.status_code}")
        return set()

def _get_free_games(api_key: str):
    """Fetches free games from the Steam Store Query API. Returns a JSON response containing free games."""
    logging.debug("Fetching free games from Steam Store Query API")
    input_json = {
            "query": {
                "start": "0",
                "count": "100",
                "filters": {
                    "type_filters": {
                        "include_bundles": "true",
                        "include_mods": "true",
                        "include_dlc": "true",
                        "include_games": "true",
                    },
                    "price_filters": {
                        "min_discount_percent": "99"
                    }
                },
            },
            "context": {
                "country_code": "US"
            }
    }

    params = {
        "key": api_key,
        "input_json": json.dumps(input_json)
    }
    
    response = requests.get(store_query_url, params=params)
    
    if response.status_code == 200:
        logging.info(f"Free games: {response.json()}")
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

def _get_app_names(appids):
    """Takes a list of appids and returns a list of (appid, name) tuples."""
    logging.debug(f"Fetching app names for appids: {appids}")
    results = []
    for appid in appids:
        url = f"https://store.steampowered.com/api/appdetails"
        params = {"appids": appid}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            app_data = data.get(str(appid), {}).get('data', {})
            name = app_data.get('name')
            if name:
                results.append((appid, name))
    return results

def all_new_free_games(steam_ids: list, api_key: str) -> dict:
    """
    Returns a dict mapping each Steam ID to a list of (appid, name) tuples
    for free games that are unowned by that user.
    """
    logging.debug("Starting the free games fetch process")

    free_games = _get_free_games(api_key)
    if not free_games:
        logging.info("No free games found or an error occurred.")
        return {}

    ids = free_games.get('response', {}).get('ids', [])
    appid_games = [entry for entry in ids if 'appid' in entry]
    appids = [entry['appid'] for entry in appid_games]

    # Dict to hold results for each Steam ID
    missing_games = {}

    for steamid in steam_ids:
        owned_appids = _get_owned_appids(steamid, api_key)
        logging.debug(f"Owned appids for {steamid}: {owned_appids}")
        unowned_appids = [appid for appid in appids if appid not in owned_appids]
        free_game_names = _get_app_names(unowned_appids) if unowned_appids else []
        missing_games[steamid] = free_game_names
        time.sleep(1)

    return missing_games