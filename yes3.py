import numpy as np
from datamodel import Order, TradingState

class Trader:


    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders = []

            if product == "AMETHYSTS":
                # Market-making strategy for AMETHYSTS
                best_bid_price = max(order_depth.buy_orders.keys())
                best_ask_price = min(order_depth.sell_orders.keys())

                if best_bid_price and best_ask_price:
                    buy_price = int(best_bid_price) - 1  # Round to nearest integer
                    sell_price = int(best_ask_price) + 1  # Round to nearest integer

                    orders.append(Order(product, buy_price, 1))
                    orders.append(Order(product, sell_price, -1))

            elif product == "STARFRUIT":
                # Combine momentum trading with exponential mean reversion for STARFRUIT
                current_price = self.get_current_price(product, state)
                ema_short = self.calculate_ema(product, state, window=1)
                ema_long = self.calculate_ema(product, state, window=5)

                if current_price and ema_short and ema_long:
                    momentum = current_price - ema_short  # Positive: price increasing, Negative: price decreasing
                    deviation = current_price - ema_long  # Positive: above EMA, Negative: below EMA

                    # Momentum Trading
                    if momentum > 0:
                        # Buy if positive momentum
                        orders.append(Order(product, int(current_price) - 1, 1))  # Round to nearest integer
                    elif momentum < 0:
                        # Sell if negative momentum
                        orders.append(Order(product, int(current_price) + 1, -1))  # Round to nearest integer

                    # Exponential Mean Reversion
                    if deviation > 0:
                        # Sell if price significantly above EMA
                        orders.append(Order(product, int(current_price) + 1, -1))  # Round to nearest integer
                    elif deviation < 0:
                        # Buy if price significantly below EMA
                        orders.append(Order(product, int(current_price) - 1, 1))  # Round to nearest integer

            elif product == "COCONUTS":
                # Combine Bollinger Bands with RSI for COCONUTS
                bollinger_buy, bollinger_sell = self.bollinger_bands(product, state)
                rsi_signal = self.calculate_rsi(product, state, window=2)

                if bollinger_buy and rsi_signal and rsi_signal < 30:
                    # Buy if price is below lower band and RSI is below 30
                    orders.append(Order(product, bollinger_buy, 1))
                elif bollinger_sell and rsi_signal and rsi_signal > 70:
                    # Sell if price is above upper band and RSI is above 70
                    orders.append(Order(product, bollinger_sell, -1))

            result[product] = orders

        return result, 0, ""  # No conversion requests for now

    def calculate_ema(self, product, state, window):
        # Calculate Exponential Moving Average (EMA) for the given product and window size
        order_depth = state.order_depths[product]
        prices = list(order_depth.sell_orders.keys()) + list(order_depth.buy_orders.keys())
        prices.sort()  # Sort prices in ascending order

        if len(prices) < window:
            return None

        # Calculate exponential moving average
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        ema = np.convolve(prices, weights)[:len(prices)]

        return ema[-1]  # Return the most recent EMA value

    def calculate_rsi(self, product, state, window):
        # Calculate Relative Strength Index (RSI) for the given product and window size
        order_depth = state.order_depths[product]
        prices = list(order_depth.sell_orders.keys()) + list(order_depth.buy_orders.keys())
        prices.sort()  # Sort prices in ascending order

        if len(prices) < window:
            return None

        price_diffs = np.diff(prices)

        # Separate price gains and losses
        gains = np.where(price_diffs > 0, price_diffs, 0)
        losses = np.where(price_diffs < 0, abs(price_diffs), 0)

        avg_gain = self.calculate_ema(gains, window)
        avg_loss = self.calculate_ema(losses, window)

        if avg_loss == 0:
            return 0  # Prevent division by zero
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

    def get_current_price(self, product, state):
        # Placeholder function to get current price
        # You can implement this to fetch the latest price from state.order_depths
        # For simplicity, let's assume the price is the best bid or ask for now
        order_depth = state.order_depths[product]
        best_bid_price = max(order_depth.buy_orders.keys())
        best_ask_price = min(order_depth.sell_orders.keys())

        if best_bid_price and best_ask_price:
            return (best_bid_price + best_ask_price) / 2
        elif best_bid_price:
            return best_bid_price
        elif best_ask_price:
            return best_ask_price
        else:
            return None

    def bollinger_bands(self, product, state):
        # Calculate Bollinger Bands for the given product
        order_depth = state.order_depths[product]
        prices = list(order_depth.sell_orders.keys()) + list(order_depth.buy_orders.keys())
        prices.sort()  # Sort prices in ascending order

        if len(prices) < 2:  # Ensure enough data points for calculation
            return None, None

        sma = np.mean(prices[-2:])  # Calculate 20-period SMA
        std_dev = np.std(prices[-2:])  # Calculate standard deviation

        upper_band = sma + 1 * std_dev  # Upper Bollinger Band
        lower_band = sma - 1 * std_dev  # Lower Bollinger Band

        return lower_band, upper_band
