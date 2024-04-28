# Define the fees for each percentage point
fees = {
    1: 90,
    2: 360,
    3: 810,
    4: 1440,
    5: 2250,
    6: 3240,
    7: 4410,
    8: 5760,
    9: 7290,
    10: 9000,
    11: 10890,
    12: 12960,
    13: 15210,
    14: 17640,
    15: 20250
}

# Number of stocks
num_stocks = 9

# Calculate total fees
total_fees = sum(fees.values())

# Calculate fees per stock
fees_per_stock = total_fees / num_stocks

# Initialize variables to store allocated percentages and remaining fees
allocated_percentages = {}
remaining_fees = total_fees

# Allocate percentages to each stock
for percentage, fee in sorted(fees.items(), reverse=True):
    # Calculate the number of times this fee can be accommodated in the remaining fees
    times = remaining_fees // fee
    # If the number of times is greater than the number of stocks remaining, use the remaining fees
    times = min(times, num_stocks)
    
    # Calculate the percentage of the stock's allocation
    allocated_percentage = times * percentage
    
    # Update the allocated percentages and remaining fees
    allocated_percentages[percentage] = allocated_percentage
    remaining_fees -= times * fee
    num_stocks -= times
    
    if remaining_fees == 0:
        break

print("Allocated Percentages:")
for percentage, value in allocated_percentages.items():
    print(f"{percentage}%: {value}")

# Number of stocks
num_stocks = 9

# Calculate the percentage each stock gets
percentage_per_stock = 100 / num_stocks

# Display the percentage breakdown for each stock
print("Percentage breakdown for each stock:")
for i in range(1, num_stocks + 1):
    print(f"Stock {i}: {percentage_per_stock}%")


print("Remaining Fees:", remaining_fees)
