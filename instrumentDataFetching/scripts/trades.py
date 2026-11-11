import logging, json, time
from kiteconnect import KiteConnect
import pandas as pd
import pprint
from datetime import datetime
import numpy as np


logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# read json file
with open("../config/ohlcv.json") as f:
    config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])
# ----------------------------------------------------

# ----------------------------------------------------
instruments = kite.instruments(exchange='NFO')

df = pd.DataFrame(instruments)
df = df[(df['segment'] == 'NFO-OPT') & (df['name'] == 'NIFTY') & (df['instrument_type'] == 'CE')]
nextWeeklyExpiry = df['expiry'].sort_values().unique()[0]
print("next Weekly Expiry Date: ", nextWeeklyExpiry)

df = df[pd.to_datetime(df['expiry']) == pd.to_datetime(nextWeeklyExpiry)]
df = df.sort_values(by='strike', ascending=True)
print(df[['instrument_token', 'tradingsymbol', 'expiry', 'strike']])
len(df)
# ----------------------------------------------------

# ---------------- NIFTY 50 LTP ----------------------
ltp = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
print("NIFTY 50 LTP: ", ltp)
# ----------------------------------------------------

#---------------- NEAREST STIKE PRICE ----------------------
nearest_strike = min(df['strike'], key=lambda x: abs(x - ltp))
print("Nearest Strike Price: ", nearest_strike)
# ----------------------------------------------------

# ---------------- TRADING SYMBOL FOR NEAREST STRIKE ----------------------
tradingSymbol = df[df.strike == nearest_strike].tradingsymbol.values[0]
print("Trading Symbol for Nearest Strike: ", tradingSymbol)
# ----------------------------------------------------

# ---------------- PLACE ORDER ----------------------
try:
    order_id = kite.place_order(
        variety="regular",
        tradingsymbol=tradingSymbol,
        exchange=kite.EXCHANGE_NFO,
        transaction_type=kite.TRANSACTION_TYPE_BUY,
        quantity=65,
        order_type=kite.ORDER_TYPE_MARKET,
        product=kite.PRODUCT_MIS
    )
    print("Order placed successfully. Order ID: ", order_id)

    # --- Place Stoploss Order (1% below buy price) ---
    # Wait for order to be filled and fetch average price
    import time
    # time.sleep(1)  # Wait for order to be processed

    order_details = kite.order_history(order_id)
    avg_price = None
    for od in order_details:
        if od['status'] == 'COMPLETE':
            avg_price = od['average_price']
    print("Average Price of executed order: ", avg_price)
    if avg_price:
        stoploss_price = int(avg_price - (avg_price * 0.01))  # 1% below
        limit_price = int(avg_price - (avg_price * 0.04))  # 4% below
        print(f"Calculated Stoploss Price: {stoploss_price}, Limit Price: {limit_price}")
        try:
            sl_order_id = kite.place_order(
                variety="regular",
                tradingsymbol=tradingSymbol,
                exchange=kite.EXCHANGE_NFO,
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=65,
                order_type=kite.ORDER_TYPE_SL,
                product=kite.PRODUCT_MIS,
                trigger_price=stoploss_price,
                price=limit_price
            )
            print(f"Stoploss order placed at {stoploss_price}. Order ID: {sl_order_id}")
        except Exception as e:
            print("Error placing stoploss order: ", e)

        # --- Place Target Limit Sell Order (2% above avg price) ---
        target_price = int(avg_price * 1.02)
        print(f"Placing target limit sell order at 2% above avg price: {target_price}")
        try:
            target_order_id = kite.place_order(
                variety="regular",
                tradingsymbol=tradingSymbol,
                exchange=kite.EXCHANGE_NFO,
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=65,
                order_type=kite.ORDER_TYPE_LIMIT,
                product=kite.PRODUCT_MIS,
                price=target_price
            )
            print(f"Target limit sell order placed at {target_price}. Order ID: {target_order_id}")
        except Exception as e:
            print("Error placing target limit sell order: ", e)
        
        # --- Modify Stoploss to Breakeven when price reaches 1% profit ---
        try:
            # Only attempt if we have an sl_order_id and avg_price
            if 'sl_order_id' in locals() and sl_order_id and avg_price:
                print("Monitoring LTP to move SL to breakeven when profit >= 1%...")
                start_time = time.time()
                max_wait = 60 * 10  # monitor for up to 10 minutes
                poll_interval = 5  # seconds
                moved = False
                while time.time() - start_time < max_wait:
                    try:
                        ltp_key = f"NFO:{tradingSymbol}"
                        ltp_info = kite.ltp(ltp_key)
                        current_price = ltp_info[ltp_key]['last_price']
                    except Exception as e:
                        print("Error fetching LTP while monitoring SL modification:", e)
                        current_price = None

                    if current_price is not None:
                        # If current price is at least 1% above avg price, move SL to breakeven
                        if current_price >= (avg_price * 1.001):
                            new_trigger = float(avg_price)  # move trigger to buy avg price
                            # set a small limit price slightly below trigger so SL order can be filled
                            new_limit = float(avg_price - (avg_price * 0.002))
                            try:
                                kite.modify_order(
                                    variety="regular",
                                    order_id=sl_order_id,
                                    order_type=kite.ORDER_TYPE_SL,
                                    trigger_price=new_trigger,
                                    price=new_limit
                                )
                                print(f"Modified SL order {sl_order_id} to trigger={new_trigger}, price={new_limit} (breakeven)")
                                moved = True
                                break
                            except Exception as e:
                                print("Error modifying SL order:", e)
                                # If modify failed, keep monitoring but avoid tight loop
                    time.sleep(poll_interval)

                if not moved:
                    print("Did not move SL to breakeven within monitoring window.")
            else:
                print("SL order id or avg_price not available; skipping SL modification.")
        except Exception as e:
            print("Unexpected error during SL modification monitoring:", e)
    else:
        print("Could not fetch average price for stoploss/target placement.")
except Exception as e:
    print("Error placing order: ", e)
# ----------------------------------------------------







# ------------------ GET ORDER DETAILS ----------------------
# try:
#     order_details = kite.order_history(order_id)
#     print("Order Details: ")
#     pprint.pprint(order_details)
# except Exception as e:
#     print("Error fetching order details: ", e)
# ----------------------------------------------------

# ------------------ EXIT ORDER ----------------------
# try:
#     # Check current positions to avoid accidental short selling
#     positions = kite.positions()
#     found_position = False
#     for pos in positions['day']:
#         if (
#             pos['tradingsymbol'] == tradingSymbol and
#             pos['exchange'] == kite.EXCHANGE_NFO and
#             pos['product'] == kite.PRODUCT_MIS and
#             pos['quantity'] >= 65
#         ):
#             found_position = True
#             break
#     if found_position:
#         exit_order_id = kite.place_order(
#             variety="regular",
#             tradingsymbol=tradingSymbol,
#             exchange=kite.EXCHANGE_NFO,
#             transaction_type=kite.TRANSACTION_TYPE_SELL,
#             quantity=65,
#             order_type=kite.ORDER_TYPE_MARKET,
#             product=kite.PRODUCT_MIS
#         )
#         print("Exit order placed successfully. Order ID: ", exit_order_id)
#     else:
#         print(f"No open MIS BUY position found for {tradingSymbol} with quantity >= 65. Exit order not placed to avoid accidental short selling.")
# except Exception as e:
#     print("Error placing exit order: ", e)
# ----------------------------------------------------


