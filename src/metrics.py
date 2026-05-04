def load_metrics(row, fuel_cost_per_mile):
    miles = row["miles"] 
    rate = row["rate"]
    if miles < 80:
        fixed_cost_per_mile = 3.09
    else:
        fixed_cost_per_mile = 1.80
    total_cost_per_mile = fixed_cost_per_mile + fuel_cost_per_mile
    rate_per_mile = rate/miles
    net_profit_per_mile = rate_per_mile - total_cost_per_mile 
    row["rate_per_mile"] = rate_per_mile
    row["net_profit_per_mile"] = net_profit_per_mile
    return row 
def calculate_cost_per_gallon(row):
    total_cost = row["total_cost"]
    gallons = row["gallons"]
    cost_per_gallon = total_cost / gallons
    row["cost_per_gallon"] = cost_per_gallon
    return row
def calculate_fuel_metrics(current_odometer, previous_odometer, current_gallons, current_cost_per_gallon):
    miles_driven = current_odometer - previous_odometer
    mpg = miles_driven / current_gallons
    fuel_cost_per_mile = current_cost_per_gallon / mpg
    return miles_driven, mpg, fuel_cost_per_mile