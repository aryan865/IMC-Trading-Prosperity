import pandas as pd

class SpreadCalculator:
    def __init__(self, filename):
        self.data = pd.read_csv(filename, header=None, names=['orchids_zscore', 'x_parameter'])
        self.data['spread'] = self.data['orchids_zscore'] - self.data['x_parameter']
        self.index = 0

    def get_next_spread(self):
        if self.index < len(self.data):
            spread = self.data.iloc[self.index]['spread']
            self.index += 1
            return spread
        else:
            return None

# Example usage:
spread_calculator = SpreadCalculator('modified_dataframe_1.csv')
while True:
    next_spread = spread_calculator.get_next_spread()
    if next_spread is None:
        break
    print("Next spread:", next_spread)
