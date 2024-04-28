import numpy as np
import pandas as pd

# Load the data from the CSV file
data = pd.read_csv('modified_dataframe.csv')

# Select the columns for the coefficients matrix
selected_columns = ['SUNLIGHT_zscore', 'HUMIDITY_zscore', 'IMPORT_TARIFF_zscore', 'EXPORT_TARIFF_zscore', 'TRANSPORT_FEES_zscore']
coefficients_matrix = data[selected_columns].values

# Select the column for the target vector
target_vector = data['ORCHIDS_zscore'].values

# Solve the system of equations
coefficients = np.linalg.lstsq(coefficients_matrix, target_vector, rcond=None)[0]

# Print the coefficients
print('Coefficients:', coefficients)
