from datamodel import Order, TradingState
import pandas as pd

class Trader:
    def run(self, state: TradingState):
        result = {}

        # Since there's only one product (ORCHIDS), we don't need to loop through products
        product = "ORCHIDS"
        order_depth = state.order_depths[product]
        orders = []

        # Load the dataset from the state object
        data = state.observations.conversionObservations["ORCHIDS"]
        df = pd.DataFrame(data)

        # Calculate z-scores for parameters
        zscores = self.calculate_zscores(df)

        # Create variable x as a linear combination of parameters
        x = self.calculate_linear_combination(zscores)

        # Example: If x is positive, buy ORCHIDS
        if x > 0:
            price = int(self.get_current_price(product, state)) - 1
            if price > 0:
                orders.append(Order(product, price, 1))  # Buy 1 unit

        # Example: If x is negative, sell ORCHIDS
        elif x < 0:
            price = int(self.get_current_price(product, state)) + 1
            orders.append(Order(product, price, -1))  # Sell 1 unit

        result[product] = orders

        return result, 0, ""  # No conversion requests for now

    def calculate_zscores(self, df):
        # Calculate z-scores for each parameter
        sunlight_zscore = (df['SUNLIGHT'] - df['SUNLIGHT'].mean()) / df['SUNLIGHT'].std()
        humidity_zscore = (df['HUMIDITY'] - df['HUMIDITY'].mean()) / df['HUMIDITY'].std()
        transport_fees_zscore = (df['TRANSPORT_FEES'] - df['TRANSPORT_FEES'].mean()) / df['TRANSPORT_FEES'].std()
        export_tariff_zscore = (df['EXPORT_TARIFF'] - df['EXPORT_TARIFF'].mean()) / df['EXPORT_TARIFF'].std()
        import_tariff_zscore = (df['IMPORT_TARIFF'] - df['IMPORT_TARIFF'].mean()) / df['IMPORT_TARIFF'].std()

        return sunlight_zscore, humidity_zscore, transport_fees_zscore, export_tariff_zscore, import_tariff_zscore

    def calculate_linear_combination(self, zscores):
        # Linear combination: x = a * SUNLIGHT_zscore + b * HUMIDITY_zscore + c * TRANSPORT_FEES_zscore + d * EXPORT_TARIFF_zscore + e * IMPORT_TARIFF_zscore
        a, b, c, d, e = 0.2, 0.3, 0.1, 0.2, 0.2  # Adjust coefficients as needed
        x = a * zscores[0] + b * zscores[1] + c * zscores[2] + d * zscores[3] + e * zscores[4]
        return x

    def get_current_price(self, product, state):
        order_depth = state.order_depths[product]
        best_bid_price = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else 0
        best_ask_price = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else float('inf')

        if best_bid_price and best_ask_price:
            return (best_bid_price + best_ask_price) / 2
        elif best_bid_price:
            return best_bid_price
        elif best_ask_price:
            return best_ask_price
        else:
            return None