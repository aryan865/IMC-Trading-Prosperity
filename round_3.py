import numpy as np
import pandas as pd
import json
from datamodel import Order, OrderDepth, ProsperityEncoder, TradingState, Symbol 
from typing import Any, Dict, List

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        logs = self.logs
        if logs.endswith("\n"):
            logs = logs[:-1]

        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.state = None
        self.orders = {}
        self.logs = ""

logger = Logger()

def get_zscore(S1, S2, window1, window2):
    S1 = pd.DataFrame(S1)
    S2 = pd.DataFrame(S2)
    
    # If window length is 0, algorithm doesn't make sense, so exit
    if (window1 == 0) or (window2 == 0):
        return 0

    # Compute rolling mean and rolling standard deviation
    ratios = S1/S2
    ma1 = ratios[-window1:].mean()
    ma2 = ratios[-window2:].mean()
    std = ratios[-window2:].std()
    zscore = (ma1 - ma2)/std

    return [zscore[0], float(ratios.iloc[-1])]

class Trader:
    def __init__(self):
            self.chocolate_data = [8000 for i in range(100)]
            self.gift_basket_data = [72000 for i in range(100)]
            


    def run(self, state: TradingState) -> Dict[str, List[Order]]:
       

        # Initialize the method output dict as an empty dict
        result = {}
        # Initialize the list of Orders to be sent as an empty list
        orders_chocolate: list[Order] = []
        orders_gift_basket: list[Order] = []

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            
            if product == "CHOCOLATE":
                window1 = 100
                window2 = 5
                
                order_depth_chocolate: OrderDepth = state.order_depths['CHOCOLATE']
                order_depth_gift_basket: OrderDepth = state.order_depths['GIFT_BASKET']

                mid_price_chocolate = (min(order_depth_chocolate.sell_orders.keys()) + max(order_depth_chocolate.buy_orders.keys()))/2
                mid_price_gift_basket = (min(order_depth_gift_basket.sell_orders.keys()) + max(order_depth_gift_basket.buy_orders.keys()))/2

                self.chocolate_data.append(mid_price_chocolate)
                self.gift_basket_data.append(mid_price_gift_basket)
                

                couple = get_zscore(self.gift_basket_data, self.chocolate_data, window1, window2)
                print(couple)
                zscore = couple[0]
                ratio = couple[1]
                chocolate_position = state.position.get('CHOCOLATE', 0)
                gift_basket_position = state.position.get('GIFT_BASKET', 0)


                if zscore > 1 and gift_basket_position< 300 and chocolate_position > -600:
                    if len(order_depth_gift_basket.buy_orders.keys()) > 0:
                        best_bid = max(order_depth_gift_basket.buy_orders.keys())
                        best_bid_volume = order_depth_gift_basket.buy_orders[best_bid]
                        print("SELL GIFT_BASKET", str(best_bid_volume) + "x", best_bid)
                        orders_gift_basket.append(Order('GIFT_BASKET', best_bid, -best_bid_volume))
                    #sell chocolate
                    if len(order_depth_chocolate.buy_orders.keys()) > 0:
                        best_bid = max(order_depth_chocolate.buy_orders.keys())
                        best_bid_volume = order_depth_chocolate.buy_orders[best_bid]
                        print("SELL CHOCOLATE", str(best_bid_volume) + "x", best_bid)
                        orders_chocolate.append(Order('CHOCOLATE', best_bid, -best_bid_volume*ratio))

                elif zscore < -1 and gift_basket_position > -300 and chocolate_position < 600:
                    #short position
                    #buy chocolate
                    if len(order_depth_chocolate.sell_orders.keys()) > 0:
                        best_ask = min(order_depth_chocolate.sell_orders.keys())
                        best_ask_volume = order_depth_chocolate.sell_orders[best_ask]
                        print("BUY CHOCOLATE", str(-best_ask_volume) + "x", best_ask)
                        orders_chocolate.append(Order('CHOCOLATE', best_ask, -best_ask_volume*ratio))
                    #sell gift_basket
                    if len(order_depth_gift_basket.sell_orders.keys()) > 0:
                        best_ask = min(order_depth_gift_basket.sell_orders.keys())
                        best_ask_volume = order_depth_gift_basket.sell_orders[best_ask]
                        print("BUY GIFT_BASKET", str(-best_ask_volume) + "x", best_ask)
                        orders_gift_basket.append(Order('GIFT_BASKET', best_ask, -best_ask_volume))
                    
                elif abs(zscore) < 0.5 or (abs(gift_basket_position) >= 300 and abs(chocolate_position) >= 600):
                # elif abs(zscore) < 0.5:
                    # Reset Positions to 0
                    if chocolate_position < 0:
                        chocolate_asks = order_depth_chocolate.sell_orders
                        while chocolate_position < 0 and len(chocolate_asks.keys()) > 0:
                            # Go through dict looking for best sell orders and append order.
                            # Then subtract order amount from chocolate_position
                            # Remove order from the dict
                            best_ask = min(chocolate_asks.keys())
                            best_ask_volume = chocolate_asks[best_ask]
                            if best_ask_volume < chocolate_position:
                                best_ask_volume = chocolate_position
                            orders_chocolate.append(Order('CHOCOLATE', best_ask, -best_ask_volume))
                            chocolate_position -= best_ask_volume
                            chocolate_asks.pop(best_ask)
                            
                    elif chocolate_position > 0:
                        chocolate_bids = order_depth_chocolate.buy_orders
                        while chocolate_position > 0 and len(chocolate_bids.keys()) > 0:
                            # Go through dict looking for best buy orders and append order.
                            # Then subtract order amount from chocolate_position
                            # Remove order from the dict
                            best_bid = max(chocolate_bids.keys())
                            best_bid_volume = chocolate_bids[best_bid]
                            if best_bid_volume > chocolate_position:
                                best_bid_volume = chocolate_position
                            orders_chocolate.append(Order('CHOCOLATE', best_bid, -best_bid_volume))
                            chocolate_position -= best_bid_volume
                            chocolate_bids.pop(best_bid)

                    if gift_basket_position < 0:
                        gift_basket_asks = order_depth_gift_basket.sell_orders
                        while gift_basket_position < 0 and len(gift_basket_asks.keys()) > 0:
                            # Go through dict looking for best sell orders and append order.
                            # Then subtract order amount from gift_basket_position
                            # Remove order from the dict
                            best_ask = min(gift_basket_asks.keys())
                            best_ask_volume = gift_basket_asks[best_ask]
                            if best_ask_volume < gift_basket_position:
                                best_ask_volume = gift_basket_position
                            orders_gift_basket.append(Order('GIFT_BASKET', best_ask, -best_ask_volume))
                            gift_basket_position -= best_ask_volume
                            gift_basket_asks.pop(best_ask)

                    elif gift_basket_position > 0:
                        gift_basket_bids = order_depth_gift_basket.buy_orders
                        while gift_basket_position > 0 and len(gift_basket_bids.keys()) > 0:
                            # Go through dict looking for best sell orders and append order.
                            # Then subtract order amount from gift_basket_position
                            # Remove order from the dict
                            best_bid = max(gift_basket_bids.keys())
                            best_bid_volume = gift_basket_bids[best_bid]
                            if best_bid_volume > gift_basket_position:
                                best_bid_volume = gift_basket_position
                            orders_gift_basket.append(Order('GIFT_BASKET', best_bid, -best_bid_volume))
                            gift_basket_position -= best_bid_volume
                            gift_basket_bids.pop(best_bid)

            


        # Add all the above orders to the result dict
        
        result['CHOCOLATE'] = orders_chocolate
        result['GIFT_BASKET'] = orders_gift_basket
        # Return the dict of orders
        # These possibly contain buy or sell orders for PEARLS
        # Depending on the logic above
        logger.flush(state,  orders_chocolate + orders_gift_basket)

        return result
