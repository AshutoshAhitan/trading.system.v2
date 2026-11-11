import logging, json
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.DEBUG)

# read json file
with open("../config/ohlcv.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
print("Login URL:", kite.login_url())

# read the request token from the std input
request_token = input("Enter request token: ")
# generate access token
data = kite.generate_session(request_token, api_secret=config['zerodha.api.secret'])
# Print the access token
print("Access Token:", data["access_token"])

# List of other config files to update
other_configs = ["../config/instrument.json", "../config/indices.json", "../config/ohlcv.json", "../config/liquidity.json"]
for cfg_path in other_configs:
    try:
        logging.debug(f'Updating {cfg_path} with access token.')
        with open(cfg_path) as f:
            cfg = json.load(f)
        cfg['zerodha.access_token'] = data["access_token"]
        with open(cfg_path, "w") as f:
            json.dump(cfg, f, indent=4)
    except FileNotFoundError:
        logging.warning(f"{cfg_path} not found, skipping update.")