# Modify an existing GTT order
def modify_gtt_order(trigger_id, tradingsymbol, exchange, new_trigger_values, new_orders):
	"""
	Modify an existing GTT order.
	Args:
		trigger_id: The GTT trigger ID to modify.
		tradingsymbol: The trading symbol for the order.
		exchange: The exchange (e.g., kite.EXCHANGE_NFO).
		new_trigger_values: List of new trigger values (ascending order).
		new_orders: List of new order dicts (must include trigger_price, price, etc.).
	Returns:
		API response dict or None if error.
	"""
	try:
		result = kite.modify_gtt(
			trigger_id=trigger_id,
			trigger_type=kite.GTT_TYPE_OCO,
			tradingsymbol=tradingsymbol,
			exchange=exchange,
			trigger_values=new_trigger_values,
			orders=new_orders
		)
		print(f"GTT order {trigger_id} modified successfully.")
		return result
	except Exception as e:
		print(f"Error modifying GTT order {trigger_id}: {e}")
		return None

# Utility: Place market buy, wait for fill, then place GTT OCO sell order
import time


# SRP: Split into single-responsibility functions
def get_nifty_option_chain():
	instruments = kite.instruments(exchange='NFO')
	df = pd.DataFrame(instruments)
	df = df[(df['segment'] == 'NFO-OPT') & (df['name'] == 'NIFTY') & (df['instrument_type'] == 'CE')]
	nextWeeklyExpiry = df['expiry'].sort_values().unique()[0]
	df = df[pd.to_datetime(df['expiry']) == pd.to_datetime(nextWeeklyExpiry)]
	df = df.sort_values(by='strike', ascending=True)
	return df

def get_trading_symbol(df, strike=None, ltp=None):
	if strike is None and ltp is not None:
		strike = min(df['strike'], key=lambda x: abs(x - ltp))
	return df[df.strike == strike].tradingsymbol.values[0], strike

def place_market_buy(tradingSymbol, quantity):
	print(f"Placing market BUY for {tradingSymbol}...")
	try:
		order_id = kite.place_order(
			variety="regular",
			tradingsymbol=tradingSymbol,
			exchange=kite.EXCHANGE_NFO,
			transaction_type=kite.TRANSACTION_TYPE_BUY,
			quantity=quantity,
			order_type=kite.ORDER_TYPE_MARKET,
			product=kite.PRODUCT_MIS
		)
		print(f"Buy order placed. Order ID: {order_id}")
		return order_id
	except Exception as e:
		print("Error placing buy order:", e)
		return None

def wait_for_order_fill(order_id, poll_interval=2, max_wait=60):
	avg_price = None
	waited = 0
	while waited < max_wait:
		try:
			order_details = kite.order_history(order_id)
			for od in order_details:
				if od['status'] == 'COMPLETE':
					avg_price = od['average_price']
					break
			if avg_price:
				break
		except Exception as e:
			print("Error fetching order status:", e)
		time.sleep(poll_interval)
		waited += poll_interval
	if not avg_price:
		print("Buy order not filled in time. Exiting.")
	else:
		print(f"Buy filled at avg price: {avg_price}")
	return avg_price

def place_gtt_oco_sell(tradingSymbol, quantity, avg_price, trigger_up_perc, trigger_down_perc):
	trigger_up = round(avg_price * trigger_up_perc, 1)
	trigger_down = round(avg_price * trigger_down_perc, 1)

	# Set price 2% away from trigger (for sell: price < trigger for stoploss, price > trigger for target)
	price_gap_perc = 0.02
	price_down = round(trigger_down * (1 - price_gap_perc), 1)  # 2% below stoploss trigger
	# price_up = round(trigger_up * (1 + price_gap_perc), 1)
	price_up = trigger_up 
	print(f"Calculated triggers - UP: {trigger_up}, DOWN: {trigger_down}")



	triggers = sorted([trigger_up, trigger_down])
	if triggers[0] == trigger_down:
		orders = [
			{
				"transaction_type": kite.TRANSACTION_TYPE_SELL,
				"quantity": quantity,
				"order_type": kite.ORDER_TYPE_LIMIT,
				"price": price_down,
				"product": kite.PRODUCT_MIS
			},
			{
				"transaction_type": kite.TRANSACTION_TYPE_SELL,
				"quantity": quantity,
				"order_type": kite.ORDER_TYPE_LIMIT,
				"price": price_up,
				"product": kite.PRODUCT_MIS
			}
		]
	else:
		orders = [
			{
				"transaction_type": kite.TRANSACTION_TYPE_SELL,
				"quantity": quantity,
				"order_type": kite.ORDER_TYPE_LIMIT,
				"price": price_up,
				"product": kite.PRODUCT_MIS
			},
			{
				"transaction_type": kite.TRANSACTION_TYPE_SELL,
				"quantity": quantity,
				"order_type": kite.ORDER_TYPE_LIMIT,
				"price": price_down,
				"product": kite.PRODUCT_MIS
			}
		]
	print(f"Placing GTT OCO sell for {tradingSymbol} with triggers: {triggers}")
	try:
		gtt = kite.place_gtt(
			trigger_type=kite.GTT_TYPE_OCO,
			tradingsymbol=tradingSymbol,
			exchange=kite.EXCHANGE_NFO,
			trigger_values=triggers,
			last_price=avg_price,
			orders=orders
		)
		print(f"GTT OCO sell order placed. Trigger ID: {gtt['trigger_id']}")
		return gtt
	except Exception as e:
		print("Error placing GTT OCO sell order:", e)
		return None

def buy_and_place_gtt_oco(
	strike=None,
	quantity=65,
	trigger_up_perc=1.02,
	trigger_down_perc=0.98,
	poll_interval=2,
	max_wait=60
):
	"""
	Orchestrates: buy, wait for fill, then place GTT OCO sell order.
	"""
	df = get_nifty_option_chain()
	ltp = kite.ltp("NSE:NIFTY 50")['NSE:NIFTY 50']['last_price']
	tradingSymbol, strike_used = get_trading_symbol(df, strike, ltp)
	order_id = place_market_buy(tradingSymbol, quantity)
	if not order_id:
		return None
	avg_price = wait_for_order_fill(order_id, poll_interval, max_wait)
	if not avg_price:
		return None
	return place_gtt_oco_sell(tradingSymbol, quantity, avg_price, trigger_up_perc, trigger_down_perc)


import logging, json
from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime

# ----------------------------------------------------
# Read config
with open("../config/ohlcv.json") as f:
	config = json.load(f)

kite = KiteConnect(api_key=config['zerodha.api.key'])
kite.set_access_token(config["zerodha.access_token"])
# ----------------------------------------------------


# Example usage:
if __name__ == "__main__":
	# To buy and then place GTT OCO sell order:
	gtt = buy_and_place_gtt_oco()
	print(gtt)

	time.sleep(60)  # Wait a bit before fetching order history
	print(kite.order_history(gtt['trigger_id']))

	# Or, to only place GTT OCO sell order (if you already hold the option):
	# place_gtt_oco_order_for_nifty50()

	# Example: Modify an existing GTT order (uncomment and fill values to use)
	# trigger_id = 123456789  # Replace with your GTT trigger ID
	# tradingsymbol = "NIFTY26MAR24500CE"  # Replace with your symbol
	# exchange = kite.EXCHANGE_NFO
	# new_trigger_values = [240, 260]  # New triggers (ascending order)
	# new_orders = [
	#     {
	#         "transaction_type": kite.TRANSACTION_TYPE_SELL,
	#         "quantity": 50,
	#         "order_type": kite.ORDER_TYPE_LIMIT,
	#         "price": 238,
	#         "trigger_price": 240,
	#         "product": kite.PRODUCT_MIS
	#     },
	#     {
	#         "transaction_type": kite.TRANSACTION_TYPE_SELL,
	#         "quantity": 50,
	#         "order_type": kite.ORDER_TYPE_LIMIT,
	#         "price": 262,
	#         "trigger_price": 260,
	#         "product": kite.PRODUCT_MIS
	#     }
	# ]
	# modify_gtt_order(trigger_id, tradingsymbol, exchange, new_trigger_values, new_orders)
