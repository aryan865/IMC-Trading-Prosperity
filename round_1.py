from datamodel import OrderDepth, Order, TradingState
from typing import Dict, List
import math

AMETHYSTS = "AMETHYSTS"
STARFRUIT = "STARFRUIT"
SUBMISSION = "SUBMISSION"

DEFAULT_PRICES = {
    AMETHYSTS: 10000,
    STARFRUIT: 5000,
}

PRODUCTS = [
    AMETHYSTS,
    STARFRUIT,
]


class Trader:

    def __init__(self) -> None:

        print("Initializing Trader...")

        self.position_limit = {
            AMETHYSTS: 20,
            STARFRUIT: 20,
        }

        self.round = 0

        # Values to compute PnL
        self.cash = 0

        # Keeps the list of all past prices
        self.past_prices = {product: [] for product in PRODUCTS}

        # Keeps an exponential moving average of prices
        self.ema_prices = {product: None for product in PRODUCTS}

        self.ema_param = 0.5

    def get_position(self, product, state: TradingState):
        return state.position.get(product, 0)

    def get_value_on_product(self, product, state: TradingState):
        return self.get_position(product, state) * self.get_mid_price(product, state)

    def get_mid_price(self, product, state: TradingState):
        default_price = self.ema_prices[product]
        if default_price is None:
            default_price = DEFAULT_PRICES[product]

        if product not in state.order_depths:
            return default_price

        market_bids = state.order_depths[product].buy_orders
        market_asks = state.order_depths[product].sell_orders

        if not market_bids or not market_asks:
            # If there are no bid or ask orders, return the default price
            return default_price

        best_bid = max(market_bids)
        best_ask = min(market_asks)
        return (best_bid + best_ask)/2

    def update_pnl(self, state: TradingState):
        def update_cash():
            # Update cash
            for product in state.own_trades:
                for trade in state.own_trades[product]:
                    if trade.timestamp != state.timestamp - 100:
                        # Trade was already analyzed
                        continue

                    if trade.buyer == SUBMISSION:
                        self.cash -= trade.quantity * trade.price
                    if trade.seller == SUBMISSION:
                        self.cash += trade.quantity * trade.price

        def get_value_on_positions():
            # Calculate the value of all positions
            value = 0
            for product in state.position:
                value += self.get_value_on_product(product, state)
            return value

        # Update cash
        update_cash()
        return self.cash + get_value_on_positions()

    def update_ema_prices(self, state: TradingState):
        for product in PRODUCTS:
            mid_price = self.get_mid_price(product, state)
            if mid_price is not None:
                # Update EMA price
                if self.ema_prices[product] is None:
                    self.ema_prices[product] = mid_price
                else:
                    self.ema_prices[product] = self.ema_param * mid_price + (1 - self.ema_param) * self.ema_prices[product]

    def amethysts_strategy(self, state: TradingState):
        # Returns a list of orders with trades of amethysts.
        position_amethysts = self.get_position(AMETHYSTS, state)
        bid_volume = self.position_limit[AMETHYSTS] - position_amethysts
        ask_volume = -self.position_limit[AMETHYSTS] - position_amethysts
        orders = []
        orders.append(Order(AMETHYSTS, DEFAULT_PRICES[AMETHYSTS] - 1, bid_volume))
        orders.append(Order(AMETHYSTS, DEFAULT_PRICES[AMETHYSTS] + 1, ask_volume))
        return orders

    def starfruit_strategy(self, state: TradingState):
        position_starfruit = self.get_position(STARFRUIT, state)
        bid_volume = self.position_limit[STARFRUIT] - position_starfruit
        ask_volume = -self.position_limit[STARFRUIT] - position_starfruit
        orders = []

        if position_starfruit == 0:
            # Not long nor short
            orders.append(Order(STARFRUIT, math.floor(self.ema_prices[STARFRUIT] - 1), bid_volume))
            orders.append(Order(STARFRUIT, math.ceil(self.ema_prices[STARFRUIT] + 1), ask_volume))
        elif position_starfruit > 0:
            # Long position
            orders.append(Order(STARFRUIT, math.floor(self.ema_prices[STARFRUIT] - 2), bid_volume))
            orders.append(Order(STARFRUIT, math.ceil(self.ema_prices[STARFRUIT]), ask_volume))
        elif position_starfruit < 0:
            # Short position
            orders.append(Order(STARFRUIT, math.floor(self.ema_prices[STARFRUIT]), bid_volume))
            orders.append(Order(STARFRUIT, math.ceil(self.ema_prices[STARFRUIT] + 2), ask_volume))

        return orders

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        self.round += 1
        pnl = self.update_pnl(state)
        self.update_ema_prices(state)

        print(f"Log round {self.round}")

        print("TRADES:")
        for product in state.own_trades:
            for trade in state.own_trades[product]:
                if trade.timestamp == state.timestamp - 100:
                    print(trade)

        print(f"\tCash {self.cash}")
        for product in PRODUCTS:
            print(f"\tProduct {product}, Position {self.get_position(product, state)}, Midprice {self.get_mid_price(product, state)}, Value {self.get_value_on_product(product, state)}, EMA {self.ema_prices[product]}")
        print(f"\tPnL {pnl}")

        # Initialize the method output dict as an empty dict
        result = {}

        # Amethyst STRATEGY
        try:
            result[AMETHYSTS] = self.amethysts_strategy(state)
        except Exception as e:
            print("Error in amethysts strategy")
            print(e)

        # Starfruit STRATEGY
        try:
            result[STARFRUIT] = self.starfruit_strategy(state)
        except Exception as e:
            print("Error in starfruit strategy")
            print(e)

        print("+---------------------------------+")

        return result
